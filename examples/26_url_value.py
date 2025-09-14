"""
Example 26 — URL value
Transform string into a parsed URL and validate scheme/host.
"""
from typing import List
from urllib.parse import urlparse, ParseResult

from constrained_values import Response, Status, TypeValidationStrategy
from constrained_values.value import TransformationStrategy, ConstrainedValue, PipeLineStrategy

class ToURL(TransformationStrategy[str, ParseResult]):
    def transform(self, value: str) -> Response[ParseResult]:
        p = urlparse(value)
        if not p.scheme or not p.netloc:
            return Response(Status.EXCEPTION, "missing scheme or host", None)
        return Response(Status.OK, "parsed", p)

class HttpURL(ConstrainedValue[ParseResult]):
    def get_strategies(self) -> List[PipeLineStrategy]:
        return [TypeValidationStrategy(str), ToURL()]

def main():
    ok = HttpURL("https://example.com/path?q=1")
    bad = HttpURL("not-a-url")
    if ok.ok:
        parsed = ok.value
        print("ok :", ok.status.name, parsed.geturl())
    else:
        print("ok :", ok.status.name, ok.details)
    print("bad:", bad.status.name, bad.details)

if __name__ == "__main__":
    main()
