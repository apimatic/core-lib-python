import pytest
from apimatic_core_interfaces.http.request import Request
from apimatic_core.templating.template_resolver import (
    MethodResolver,
    UrlResolver,
    PathResolver,
    HeaderResolver,
    QueryResolver,
    JsonBodyPointerResolver,
)


class TestTemplateResolvers:
    def test_method_matches_and_none(self):
        r = MethodResolver()
        assert r.matches("method")
        fn = r.compile("method")
        # None → empty string, upper() guarded in engine, but resolver uses request.method directly
        assert fn(Request(method=None)) == b""

    def test_url_matches_and_none(self):
        r = UrlResolver()
        assert r.matches("url")
        assert r.compile("url")(Request(url=None)) == b""

    def test_path_matches_and_none(self):
        r = PathResolver()
        assert r.matches("request.path")
        assert r.compile("request.path")(Request(path=None)) == b""

    def test_header_case_insensitive_and_missing_and_none_headers(self):
        r = HeaderResolver()
        assert r.matches("request.header.X-Key")
        fn = r.compile("request.header.X-Key")
        assert fn(Request(headers={"x-key": "VAL"})) == b"VAL"
        assert fn(Request(headers={"X-Other": "nope"})) == b""
        assert fn(Request(headers=None)) == b""

    @pytest.mark.parametrize(
        "query, expected",
        [
            ({"color": ["red", "blue"]}, b"red"),
            ({"color": "red"}, b"red"),
            ({"color": 42}, b"42"),
            (None, b""),
        ],
    )
    def test_query_first_value_coercions(self, query, expected):
        r = QueryResolver()
        assert r.matches("request.query.color")
        fn = r.compile("request.query.color")
        assert fn(Request(query=query)) == expected

    def test_json_body_pointer_present_and_missing(self):
        r = JsonBodyPointerResolver()
        assert r.matches("request.body#/a/b")
        fn = r.compile("request.body#/a/b")
        assert fn(Request(body='{"a":{"b":"v"}}')) == b"v"
        # missing
        assert r.compile("request.body#/missing")(Request(body='{"a":1}')) == b""
