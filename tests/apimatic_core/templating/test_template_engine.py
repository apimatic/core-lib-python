# tests/test_template_engine.py
import pytest
from apimatic_core_interfaces.http.request import Request
from apimatic_core.templating.template_engine import TemplateEngine
from apimatic_core.templating.template_resolver import (
    MethodResolver,
    UrlResolver,
    PathResolver,
    HeaderResolver,
    QueryResolver,
    JsonBodyPointerResolver,
)


def make_engine() -> TemplateEngine:
    return TemplateEngine([
        MethodResolver(),
        UrlResolver(),
        PathResolver(),
        HeaderResolver(),
        QueryResolver(),
        JsonBodyPointerResolver(),
    ])


class TestTemplateEngine:
    def test_literal_only(self):
        eng = make_engine()
        plan = eng.compile("abc:123")
        assert eng.render(plan, Request()) == b"abc:123"

    def test_literal_and_raw_body(self):
        eng = make_engine()
        plan = eng.compile("prefix:{raw_body}:suffix")
        req = Request(body='{"x":1}', raw_body=b'{"x":1}')
        assert eng.render(plan, req) == b"prefix:{\"x\":1}:suffix"

    def test_two_raw_bodies_concat(self):
        eng = make_engine()
        plan = eng.compile("{raw_body}{raw_body}")
        req = Request(body="X", raw_body=b"X")
        assert eng.render(plan, req) == b"XX"

    def test_method_url_path_headers_query_json(self):
        eng = make_engine()
        tpl = "::".join([
            "{$method}",
            "{$url}",
            "{$request.path}",
            "{$request.header.X-Foo}",
            "{$request.query.id}",
            "{$request.body#/a/b}",
        ])
        plan = eng.compile(tpl)
        req = Request(
            method="get",
            url="https://example.test/u?p=1",
            path="/u",
            headers={"x-foo": "BAR"},
            query={"id": ["007"]},
            body='{"a":{"b":"V"}}',
            raw_body=b'{"a":{"b":"V"}}',
        )
        out = eng.render(plan, req)
        assert out == b"GET::https://example.test/u?p=1::/u::BAR::007::V"

    def test_unknown_expression_resolves_to_empty(self):
        eng = make_engine()
        plan = eng.compile("A={$unknown}:B")
        assert eng.render(plan, Request()) == b"A=:B"

    def test_raw_body_fallback_to_text_when_raw_missing(self):
        eng = make_engine()
        plan = eng.compile("{raw_body}")
        req = Request(body="txt", raw_body=None)
        assert eng.render(plan, req) == b"txt"

    @pytest.mark.parametrize("bad", [
        "prefix:{$request.header.X-TS:{raw_body}",   # unclosed
        "{$}: {raw_body}",                            # empty expr
        "{$request.header.}:{raw_body}",              # missing header name
        "{$request.query.}:{raw_body}",               # missing query name
        "{$request.body#}:{raw_body}",                # missing pointer segment
        "{$request.body#not/a/pointer}:{raw_body}",   # pointer must start with '/'
    ])
    def test_bad_template_raises(self, bad):
        eng = make_engine()
        with pytest.raises(ValueError):
            eng.compile(bad)
