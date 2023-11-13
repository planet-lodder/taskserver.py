
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
