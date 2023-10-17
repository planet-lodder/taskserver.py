
from colorama import Style
import yaml


def bind(key):
    def get(self, key):
        self[key] = {} if not key in self else self[key]
        return self[key]

    def set(self, key, value):
        self[key] = value

    return property(
        lambda self: get(self, key),
        lambda self, value: set(self, key, value),
    )


def flatten(values, base=''):
    mapped = {}
    for key, val in values.items():
        subkey = f'{base}.{key}'
        if type(val) == dict:
            subvalues = flatten(val, subkey)
            mapped.update(subvalues)
        else:
            mapped[subkey] = val
    return mapped


def partial_values(values, prefix):
    found = {}
    for key in filter(lambda k: k.startswith(prefix), values):
        subpath = key[len(prefix):]
        found[subpath] = values[key]
    return found


class HtmxRequest():

    def __init__(self, req):
        self.req = req

        # TODO: Move this to the server layer
        self.print_details()

    @property
    def isHTMX(self):
        head = self.req.head
        return head["hx-request"] if "hx-request" in head else False

    @property
    def prompt(self):
        head = self.req.head
        return head["hx-prompt"] if "hx-prompt" in head else ""

    @property
    def triggerName(self):
        head = self.req.head
        return head["hx-trigger-name"] if "hx-trigger-name" in head else ""

    @property
    def triggerValue(self):
        name = self.triggerName
        return self.req.body[name] if name in self.req.body else ""

    def input(self, name):
        inputs = self.req.body or {}
        for key in filter(lambda k: k == name, inputs):
            return self.req.body[key]  # Key found
        return None  # Not found

    def inputs(self, prefix=""):
        res = {}
        inputs = self.req.body or {}
        for key in filter(lambda k: k.startswith(prefix), inputs):
            res[key] = inputs[key]
        return res

    def print_details(self):
        if not self.isHTMX:
            return

        req = self.req
        fVerb = f'{Style.RESET_ALL}{Style.BRIGHT}{req.verb}{Style.RESET_ALL}{Style.DIM}'
        fPath = f'{Style.RESET_ALL}{Style.BRIGHT}{req.path}{Style.RESET_ALL}{Style.DIM}'
        print(
            f'{Style.DIM}--- [ {fVerb} {fPath} ] --------------------------------')
        hx_headers = list(
            filter(lambda k: k.lower().startswith("hx-"), req.head))
        if len(hx_headers):
            head = {}
            for k in filter(lambda k: k.lower() != 'hx-request', hx_headers):
                head[k] = req.head[k]
            print(yaml.safe_dump({"head": head}).rstrip())
        if req.body:
            body = {}
            for k in (req.body if req.body else []):
                body[k] = req.body[k]
            print(yaml.safe_dump({"body": body}).rstrip())
        print('-'*64 + Style.RESET_ALL)
