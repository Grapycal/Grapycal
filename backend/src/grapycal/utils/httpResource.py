import json
from pathlib import Path
import traceback
from typing import Any, Generic, Type, TypeVar
from urllib.parse import ParseResult, urlparse
import aiohttp
from grapycal.utils.misc import as_type
import yaml
import logging
import certifi
import ssl
from aiohttp import TCPConnector

logger = logging.getLogger(__name__)

T = TypeVar("T")


class HttpResource(Generic[T]):
    def __init__(self, url: str, data_type: Type[T] = Any, format=None):
        self.url = url
        self.data: T | None = None
        self.failed = False
        self.failed_exception = None
        if format is None:
            if url.endswith(".json"):
                format = "json"
            elif url.endswith(".yaml"):
                format = "yaml"
            else:
                format = "binary"
        self.format = format
        self.data_type = data_type

    async def is_avaliable(self):
        try:
            await self.get()
        except:
            return False
        return True

    async def get(self) -> T:
        if self.failed:
            raise Exception(f"Failed to get {self.url} : {self.failed_exception}")
        if self.data is not None:
            return self.data
        try:
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            connector = TCPConnector(ssl=ssl_context)
            async with aiohttp.request(
                "GET", self.url, connector=connector
            ) as response:
                if self.format == "yaml":
                    self.data = yaml.safe_load(await response.text())
                elif self.format == "json":
                    self.data = json.loads(await response.text())
                elif self.format == "binary":
                    self.data = as_type(await response.read(), self.data_type)
                else:
                    raise Exception(f"Unknown format {self.format}")
                connector.close()
        except Exception as e:
            self.failed = True
            self.failed_exception = e
            raise Exception(f"Failed to get {self.url} : {self.failed_exception}")
        return self.data
