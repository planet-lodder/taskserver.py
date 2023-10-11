from typing import Generic, Type, TypeVar
from taskserver.domain.serializers.base import Serializer
from taskserver.domain.serializers.web import WebSerializer

TSerializer = TypeVar("TSerializer", bound=Serializer)
TWebSerializer = TypeVar("TWebSerializer", bound=WebSerializer)


class Serialize(Generic[TSerializer]):

    @staticmethod
    def fromWeb(req, cls: Type[TWebSerializer]) -> TWebSerializer:
        res = cls(req)
        return res
