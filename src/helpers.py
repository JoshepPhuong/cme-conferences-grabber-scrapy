import logging
import os
import pathlib
from copy import copy

from openpyxl.worksheet.worksheet import Worksheet
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import Spider
from scrapy.utils.conf import closest_scrapy_cfg
from scrapy.utils.project import get_project_settings


def run_spider(grabber: type[Spider], stop_after_crawl: bool = True, export_format="xlsx"):
    """Used for debugging spider in PyCharm.

    If something does not work while using it, run spider by scrapy `scrapy crawl aan_spider -t {file_format} -o {file}`

    """
    os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "src.settings")
    project_root = pathlib.Path(closest_scrapy_cfg()).parent
    settings = get_project_settings()
    export_path = project_root / f"out.{export_format}"
    export_path.unlink(missing_ok=True)

    settings.update(
        {
            "FEEDS": {
                export_path: {
                    "format": export_format,
                },
            },
        },
    )
    process = CrawlerProcess(settings)

    process.crawl(grabber)
    process.start(stop_after_crawl=stop_after_crawl)

    scrapy_logger = logging.getLogger("scrapy")
    scrapy_logger.info(f"Finished. Check results in {export_path.name}")


def format_sheet(sheet: Worksheet):
    """Apply default format for result xlsx file.

    Format:
        * Headers (First row) - freeze and apply wrap_text,
        * Other rows - apply shrink to fit
        * Add autofilter for all columns

    """
    rows = sheet.iter_rows()
    first_row = next(rows)
    for cell in first_row:
        alignment = copy(cell.alignment)
        cell.alignment = alignment

    for row in rows:
        for cell in row:
            alignment = copy(cell.alignment)
            cell.alignment = alignment

    # Set first cell that is not supposed to be frozen
    sheet.freeze_panes = "A2"

    # Enable autofilter for all columns
    sheet.auto_filter.ref = sheet.dimensions
