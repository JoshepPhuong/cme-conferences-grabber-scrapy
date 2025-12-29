from collections.abc import AsyncGenerator, Generator, Iterator
from typing import TypeAlias, TypeVar

from scrapy import FormRequest, Request

from src.items import BaseItem

RequestorResponse = Iterator[Request]
FormRequestorResponse = Iterator[FormRequest]
BaseItemT = TypeVar("BaseItemT", bound=BaseItem)
Item: TypeAlias = Generator[BaseItemT]
AsyncItem: TypeAlias = AsyncGenerator[BaseItemT]
