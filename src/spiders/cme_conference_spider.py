from datetime import datetime

import dateutil
import scrapy
from scrapy.http.response.html import HtmlResponse

from src import helpers
from src.items import BaseItem, Field
from src.types import AsyncItem, Item, RequestorResponse


class CMEConferencesItem(BaseItem):
    """Item class for storing conference details."""

    title = Field("Title")
    start_date = Field("Start Date")
    end_date = Field("End Date")
    location = Field("Location")
    description = Field("Description")
    url = Field("URL")
    credit = Field("Credit")
    event_code = Field("Event Code")


class CMEConferencesSpider(scrapy.Spider):
    """Spider scrapes CME Conferences provided by American Medical Seminars."""

    name = "CMEConferences"
    base_urls = [
        "https://www.americanmedicalseminars.com/live/",
    ]

    async def start(self) -> AsyncItem[CMEConferencesItem] | RequestorResponse:
        for url in self.base_urls:
            yield scrapy.Request(url=url, callback=self.parse_conferences)  # type: ignore

    def parse_conferences(self, response: HtmlResponse) -> RequestorResponse:
        """Parse the response and extract conference details."""
        for conference_url in response.xpath("//div[h3]/parent::a/@href").getall():
            yield scrapy.Request(
                url=conference_url,
                callback=self.parse_conference_details,  # type: ignore
            )

    def parse_conference_details(
        self,
        response: HtmlResponse,
    ) -> Item[CMEConferencesItem]:
        """Parse conference details from the conference page."""
        conference_details = {
            "title": response.xpath("//h1/text()").get("").strip(),
            "location": self.get_conference_location(response),
            "description": response.xpath("//p/strong/text()").get("").strip(),
            "credit": self.get_conference_credit(response),
            "event_code": self.get_event_code(response),
            "url": response.url,
            **self.parse_conference_date(response),
        }

        yield CMEConferencesItem(**conference_details)

    def parse_conference_date(self, response: HtmlResponse) -> dict[str, str]:
        """Parse  date from the response."""
        conference_date = response.xpath(
            "//h6[text()='When']/following::p[1]/text()",
        ).getall()
        return {
            "start_date": conference_date[0].strip("– "),  # noqa: RUF001
            "end_date": conference_date[1].strip(),
        }

    def get_conference_location(self, response: HtmlResponse) -> str:
        """Parse location from the response."""
        location = response.xpath(
            "//h6[text()='Where']/following::p[1]/text()",
        ).getall()
        return ", ".join(location).strip() if location else ""

    def get_conference_credit(self, response: HtmlResponse) -> str:
        """Parse credit from the response."""
        return (
            response.xpath(
                "//h6[text()='Credit']/following::p[1]//strong/text()",
            )
            .get("")
            .strip()
        )

    def get_event_code(self, response: HtmlResponse) -> str:
        """Parse event code from the response."""
        return (
            response.xpath(
                "//h6[text()='Event Code']/following::p[1]/text()",
            )
            .get("")
            .strip()
        )

    def get_ordering_key(
        self,
        item: CMEConferencesItem,
    ) -> tuple[datetime | str, datetime | str, str]:
        """Return export order."""
        start_date = item.get("start_date", "")
        end_date = item.get("end_date", "")
        return (
            dateutil.parser.parse(start_date) if start_date else "",
            dateutil.parser.parse(end_date) if end_date else "",
            item.get("title", ""),
        )


if __name__ == "__main__":
    helpers.run_spider(CMEConferencesSpider)
