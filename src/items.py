import scrapy


class Field(scrapy.Field):
    """Base field for item.

    Provide ability to specify human-readable name for field, for example:

        class Item(BaseItem):
            first_name = Field("Person's First Name")

    so in code will be used `first_name`, and in export - `"Person's First Name"`.

    """

    def __init__(self, name):
        self.name = name
        super().__init__()


class SortedItemMeta(scrapy.item.ItemMeta):
    """Metaclass that allow saving of fields declaration order.

    Default Item's metaclass simply uses `dir(class)` to find all fields, which does not preserve order of fields in
    `item.fields`, and resulting CSV export may be hard to check with `Item` declaration.

    """

    def __new__(mcs, class_name, bases, attrs):
        """Copy declared fields to `cls.fields` including fields from parent classes.

        Code is very similar to original's `__new__` method

        """
        classcell = attrs.pop("__classcell__", None)
        new_bases = tuple(base._class for base in bases if hasattr(base, "_class"))
        _class = super(scrapy.item.ItemMeta, mcs).__new__(mcs, "x_" + class_name, new_bases, attrs)

        # change here, before:
        # fields = getattr(_class, 'fields', {})

        known = set(attrs)

        def visit(name):
            known.add(name)
            return name

        fields = {
            visit(name): f
            for base in bases
            if hasattr(base, "fields")
            for name, f in base.fields.items()
            if name not in known
        }

        # Original code:
        new_attrs = {}
        for n in dir(_class):
            if n in attrs:
                continue
            v = getattr(_class, n)
            if isinstance(v, Field):
                fields[n] = v
            elif n in attrs:
                new_attrs[n] = attrs[n]

        # add new fields/attrs that declared on new Item class
        for n, v in attrs.items():
            if isinstance(v, Field):
                fields[n] = v
            elif n in attrs:
                new_attrs[n] = attrs[n]

        new_attrs["fields"] = fields
        new_attrs["_class"] = _class
        if classcell is not None:
            new_attrs["__classcell__"] = classcell
        return super(scrapy.item.ItemMeta, mcs).__new__(mcs, class_name, bases, new_attrs)


class BaseItem(scrapy.Item, metaclass=SortedItemMeta):
    """Base Item class that must be used for spiders.

    Note: if item inherits `BaseItem`, it is required to use `Field` instead of
    `scrapy.Field`.

    Note: if `BaseItem` used, default `FeedExporter` won't work because of fields renaming.
    Use 'src.extensions.exporters.LateFeedExporter' subclasses for this items.

    Example:
        class Event(BaseItem):
            event_id = Field("Event Id")
            title = Field("Title")

        Set values in spiders like:
            event = Event()
            event["event_id"] = 1
            event["title"] = "Title"

            `event["aaa"] = 2` will raise KeyError


    Scrapy doc about Item: https://doc.scrapy.org/en/latest/topics/items.html

    """

    skip_fields = []

    def to_dict(self):
        """Return item as dict where keys are names of fields.

        This method is required to call before export. If it won't be called,
        item fields will not match export headers and items won't be exported.

        Example:
            object {"title": a, "event_id": 1} will be returned as
            {"Title": a, "Event Id": 1} if item is Event

            class Event(BaseItem):
                event_id = Field("Event Id")
                title = Field("Title")

        """
        return {self.fields[field].name: self.get(field, "") for field in self.fields}

    @classmethod
    def export_fields(cls):
        """Return `export_order` where fields are replaces by theirs names.

        List that is return by this method must be used in spider for
        `FEED_EXPORT_FIELDS` setting.

        Example:
            If export_order = ("event_id", "title", "url"), then method
            returns ("Event Id", "Title", "URL")

        """
        return [cls.fields[f].name for f in cls.get_export_order()]

    @classmethod
    def get_export_order(cls):
        """Return export order.

        Example:
            ("event_id", "title", "url", ...)

        May be used to override `export_order` (add, remove items) in child
        classes.

        """
        return tuple(f for f in cls.fields.keys() if f not in cls.skip_fields)
