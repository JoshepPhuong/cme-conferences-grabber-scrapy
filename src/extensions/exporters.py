from scrapy.extensions.feedexport import FeedExporter
from scrapy.spiders import Spider

from ..items import BaseItem


class LateFeedExporter(FeedExporter):
    """LateFeedExporter with ability to prepare items before export.

    `FeedExporter` saves item right after it was scrapped,
    `LateFeedExporter` stores all items in `scrapped_items` and exports them
    prepared in `close_spider` method.

    `BaseItem` used for defining custom fields names for export.
    So before export it's required to call `item.to_dict` for proper field names mapping.

    """

    scrapped_items: list[BaseItem] = []

    def item_scraped(self, item, spider: Spider):
        self.scrapped_items.append(item)
        return item

    def close_spider(self, spider: Spider):
        """Prepare items before export."""
        items = self.prepare_items(self.scrapped_items, spider)
        self._export_items(items, spider)
        return super().close_spider(spider)

    def prepare_items(self, items, spider: Spider) -> list[dict]:
        """Convert items to dicts.

        You can override this method, to implement sorting or filtering, but you should return list of dicts.

        """
        if items and isinstance(items[0], BaseItem):
            items = [i.to_dict() if not isinstance(i, dict) else i for i in items]
        return items

    def _export_items(self, items, spider: Spider):
        """Export all items."""
        for slot in self.slots:
            slot.start_exporting()

            for item in items:
                slot.exporter.export_item(item)

            slot.itemcount = len(items)


class OrderingMixin:
    """Mixin for items that defines export order."""

    def prepare_items(self, items, spider: Spider) -> list[dict]:
        """Prepare items for export."""
        items = sorted(
            items,
            key=lambda item: self._get_ordering_key(item, spider),
        )
        return super().prepare_items(items, spider)

    def _get_ordering_key(self, item, spider) -> tuple:
        """Return export order."""
        if hasattr(spider, "get_ordering_key"):
            return spider.get_ordering_key(item)
        if hasattr(spider, "ordering_fields"):
            return tuple(item[field] for field in spider.ordering_fields)
        return tuple(item.get(field, "") for field in item.keys())


class DefaultScrapedItemsExporter(OrderingMixin, LateFeedExporter):
    """Default exporter for scraped items.

    This exporter uses `BaseItem` to define export order and field names.
    It also sorts items by their export order before exporting.

    """
