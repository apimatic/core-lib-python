from apimatic_core.templating.json_pointer_resolver import JsonPointerResolver


class TestJsonPointerResolver:
    def test_scalars(self):
        r = JsonPointerResolver(body_text='{"a":{"s":"val","n":10,"b":true}}')
        assert r.resolve("/a/s") == "val"
        assert r.resolve_as_bytes("/a/s") == b"val"
        assert r.resolve_as_bytes("/a/n") == b"10"
        # current impl uses str(True) → b"True"
        assert r.resolve_as_bytes("/a/b") == b"True"

    def test_dict_and_list_are_canonicalized(self):
        r = JsonPointerResolver(body_text='{"o":{"z":1,"a":2},"arr":[3,2,1]}')
        assert r.resolve_as_bytes("/o") == b'{"a":2,"z":1}'
        assert r.resolve_as_bytes("/arr") == b"[3,2,1]"

    def test_missing_pointer(self):
        r = JsonPointerResolver(body_text='{"x":1}')
        assert r.resolve("/missing") is None
        assert r.resolve_as_bytes("/missing") == b""

    def test_non_json_body(self):
        r = JsonPointerResolver(body_text="not-json")
        assert r.resolve_as_bytes("/x") == b""

    def test_empty_pointer_entire_document(self):
        # RFC 6901: empty pointer = whole document
        r = JsonPointerResolver(body_text='{"k":1,"a":2}')
        assert r.resolve_as_bytes("") == b'{"a":2,"k":1}'

    def test_bytes_passthrough(self):
        # exercise _to_bytes path for bytes
        r = JsonPointerResolver(body_text='{"bin": "ignored"}')
        # simulate an internal call: passing bytes directly to _to_bytes
        assert r._to_bytes(b"X") == b"X"
