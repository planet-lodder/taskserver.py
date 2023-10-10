from abc import ABC, abstractmethod
from typing import Type, TypeVar


class Serializer(ABC):
    data = None
    errors = []

    @abstractmethod
    def parse(self): ...

    def validate(self):
        # Clear previous validation result
        self.errors = []
        self.data = self.parse()
        return self.data and len(self.errors) == 0


class WebSerializer(Serializer):

    def __init__(self, req) -> None:
        self.req = req

    def head(self, key=None, default=None):
        head = self.req.head if self.req and self.req.head else {}
        if key:
            return head[key] if key in head else default
        return head

    def body(self, key=None, default=None):
        body = self.req.body if self.req and self.req.body else {}
        if key:
            return body[key] if key in body else default
        return body


TWebSerializer = TypeVar("TWebSerializer", bound=WebSerializer)


class Serialize():

    @staticmethod
    def fromWeb(req, cls: Type[TWebSerializer]) -> TWebSerializer:
        res = cls(req)
        return res
