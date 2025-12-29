import logging
import pathlib
import re
import typing
from dataclasses import dataclass

import scrapy
import scrapy.settings
from scrapy import spiderloader
from scrapy.utils import log


@dataclass
class Grabber:
    """Dataclass which represents grabber by it's name, class name, path.

    It is also allows to check if the given name is relevant for the grabber or
    not.

    """

    name: str
    class_name: str
    path: pathlib.Path
    module_name: str = ""

    def is_suitable_name(self, name: str) -> bool:
        """Return whether the grabber relevant to the given name or not."""
        name_parts = name.lower().split(" ")

        name_relevant = all(part in self.name.lower() for part in name_parts)
        class_name_relevant = all(part in self.class_name.lower() for part in name_parts)
        path_relevant = (
            name == str(self.path)
            # For dot notation path
            or name == str(self.path).removesuffix(".py").replace("/", ".")
        )
        module_name_relevant = name == self.module_name or name == self.module_name.removesuffix(
            ".py",
        )

        return any(
            [
                name_relevant,
                class_name_relevant,
                path_relevant,
                module_name_relevant,
            ],
        )

    def get_sort_length(self) -> int:
        """Return sort length.

        This is simply max length of the grabber's names (class name,
        grabber's name, module name).

        This is a number which is needed to correctly sort relevant grabbers.
        So, for example, if we want to run `abc_grabber.py` and type abc, then
        we definitely don't want to start `abc_events_grabber.py`. Thus the less
        sort number - the more relevant the grabber.

        """
        attributes_to_get_sort_length = (
            self.name,
            self.class_name,
            self.module_name,
        )
        return max(map(len, attributes_to_get_sort_length))

    def __post_init__(self):
        self.module_name = self.path.name


def get_all_grabbers(settings: scrapy.settings.Settings) -> list[Grabber]:
    """Return list of all grabbers."""
    grabbers = []

    spider_loader = spiderloader.SpiderLoader.from_settings(settings)

    for grabber_name in spider_loader.list():
        loaded_grabber = spider_loader.load(grabber_name)
        grabber_path = f"{loaded_grabber.__module__.replace('.', '/')}.py"
        grabber = Grabber(
            name=grabber_name,
            class_name=loaded_grabber.__name__,
            path=pathlib.Path(grabber_path),
        )
        grabbers.append(grabber)

    return grabbers


def display_brief_results(
    grabber_name: str,
    out: str,
    settings: scrapy.settings.Settings,
) -> None:
    """Log grabber's run results."""
    logger = logging.getLogger("scrapy")
    log.configure_logging(settings)

    match out:
        case out if "ERROR" in out:
            logger.error(
                "Errors during executing of "
                f"`{grabber_name}` grabber:\n{'\n'.join(get_errors(out))}",
            )
        case out if "WARNING" in out:
            logger.warning(
                f"Warn during executing of `{grabber_name}` grabber",
            )
        case _:
            logger.info(
                f"Successfully finished `{grabber_name}` run.",
            )


def get_errors(out: str) -> typing.Iterable[str]:
    """Return error from grabber's out."""
    error_regex = r"ERROR([\s\S]+?)(?:(?:INFO)|(?:WARNING)|(?:ERROR))"
    errors = re.findall(error_regex, out)

    formatted_errors = []
    for number, error in enumerate(errors, start=1):
        error = error.replace("\x1b[0m", "")
        error = error.strip()

        # Strip redundant spaces for each line of error
        error = "\n   ".join(error_part.strip() for error_part in error.split("\n"))
        formatted_errors.append(f"{number}. {error}")

    return formatted_errors
