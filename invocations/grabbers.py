import logging
import pathlib

import invoke
from scrapy.utils import project

from . import printing
from .utils import run_grabber


@invoke.tasks.task
def run(
    context: invoke.context.Context,
    name: str,
    brief_logs: bool = False,
) -> None:
    """Run grabber.

    In order to run the grabber must be provided one of:
        * grabber's name
        * grabber's class name
        * python file's name
        * full relative path to grabber

    If provided arg is a full path or file's name and grabber with this path
    exists then it will be executed, otherwise grabber with relevant name will
    be retrieved and executed.

    """
    # Temporary disable logging to avoid displaying message about disabled
    # loggers, coz this message appears every time we get project settings.
    # If `brief_logs` is False, then we get this message from the grabber and
    # if it is True, we don't need this message at all
    logging.disable()
    settings = project.get_project_settings()
    logging.disable(logging.NOTSET)

    exact_grabber_path: pathlib.Path
    PYTHON_COMMAND = "PYTHONPATH=.:$PYTHONPATH python"

    all_grabbers = run_grabber.get_all_grabbers(settings)
    relevant_grabbers = [grabber for grabber in all_grabbers if grabber.is_suitable_name(name=name)]

    if not relevant_grabbers:
        printing.print_error(
            f"Grabber with name `{name}` wasn't found, ensure the "
            "name is correct and the grabber exists.",
        )
        raise invoke.exceptions.Exit()

    # Sort by len of name, because grabbers without unspecified words are
    # preferable, e.g. `acg_grabber.py` is preferable over
    # `acg_posters_grabber.py` if we want to run grabber with name `ACG`
    relevant_grabbers.sort(key=lambda grabber: grabber.get_sort_length())
    exact_grabber_path = relevant_grabbers[0].path

    printing.print_success(f"Run `{exact_grabber_path.name}`.")

    env_variables = {}

    # We don't need colors and timestamps in grabber's logs because these logs
    # will not be displayed if `brief_logs` is True.
    # Also colored logs with timestamps is much harder to parse, but
    # we need to parse errors in case when `brief_logs` is True.
    if brief_logs:
        env_variables.update(
            {
                "SHOW_PLAIN_LOGS": "1",
                "NO_COLOR": "1",
            },
        )

    result = context.run(
        f"{PYTHON_COMMAND} {exact_grabber_path}",
        # Avoid displaying command which starts grabber
        echo=False,
        # Hide grabber's output when `brief_logs` is True
        hide=brief_logs,
        env=env_variables,
    )

    if brief_logs:
        run_grabber.display_brief_results(
            exact_grabber_path.name,
            result.stdout,
            settings,
        )
