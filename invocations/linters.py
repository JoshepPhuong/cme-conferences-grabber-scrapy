import os

import invoke

from . import printing

DEFAULT_FOLDERS = " ".join(
    [
        "src",
        "invocations",
    ],
)


@invoke.task
def all(context: invoke.Context, path: str = DEFAULT_FOLDERS) -> None:  # noqa: A001
    """Run all linters not covered by pre-commit.

    Args:
        context: Invoke's context
        path(str): Path to selected file

    Usage:
        # is simple mode without report
        inv linters.all
        # usage on selected file
        inv linters.all --path='apps/users/models.py'

    """
    printing.print_success("Linters: running all linters")
    linters = [mypy]

    # We can't use `dead-fixtures` in Github Actions because it depend on environment variables
    if not os.environ.get("GITHUB_ACTIONS"):
        linters.append(dead_fixtures)

    failed = []
    for linter in linters:
        try:
            linter(context, path)
        except invoke.UnexpectedExit:
            failed.append(linter.__name__)
    if failed:
        printing.print_error(
            f"Linters failed: {', '.join(map(str.capitalize, failed))}",
        )
        raise invoke.Exit(code=1)


@invoke.task
def dead_fixtures(context: invoke.Context, path: str = DEFAULT_FOLDERS) -> None:
    """Lint not used fixtures, see https://github.com/jllorencetti/pytest-deadfixtures."""
    context.run(command=f"pytest {path} --dead-fixtures")


@invoke.task
def mypy(context: invoke.Context, path: str = DEFAULT_FOLDERS) -> None:
    """Lint code with mypy."""
    context.run(command=f"mypy {path}")
