
from anyserver import WebRequest, HtmxRequest

from taskserver.domain.serializers.base import Serializer


class WebSerializer(Serializer):
    _htmx = None

    def __init__(self, req: WebRequest) -> None:
        self.req = req

    @property
    def htmx(self):
        if self.req.header('hx-request', False):
            return HtmxRequest(self.req)
        return None  # Not an htmx request

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
