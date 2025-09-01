# test_hmac_signature_verifier.py
import hashlib
import types
import pytest

from apimatic_core.security import (
    HmacSignatureVerifier,
    HexEncoder,
    Base64Encoder,
    SignatureVerificationError,
)

# ---------- Simple Request factory ----------
def make_request(**kwargs):
    """
    Minimal Request-like object exposing attributes the verifier reads:
    headers, body (str), raw_body (bytes), path, url, method, query (dict[str, list[str] | str]).
    """
    defaults = dict(
        headers={},
        body=None,
        raw_body=None,
        path="",
        url="",
        method="",
        query=None,
    )
    defaults.update(kwargs)
    return types.SimpleNamespace(**defaults)


# ---------- Common fixtures ----------
@pytest.fixture
def hex_encoder():
    return HexEncoder()

@pytest.fixture
def b64_encoder():
    return Base64Encoder()

@pytest.fixture
def json_body():
    # compact JSON (stable string for predictable HMAC)
    return '{"event":{"id":"evt_123","type":"update"},"payload":{"checksum":"abc123"}}'

@pytest.fixture
def json_body_bytes(json_body):
    return json_body.encode("utf-8")


# ---------- Helper to seed signature header ----------
def seed_header(verifier: HmacSignatureVerifier, req, header_name: str):
    sig = verifier.compute_expected_signature(req)
    req.headers[header_name] = sig
    return sig


# ================== HAPPY PATHS ==================

def test_signs_raw_body_only_with_hex_digest(hex_encoder, json_body, json_body_bytes):
    verifier = HmacSignatureVerifier(
        key="secret123",
        signature_header="X-Signature",
        message_template="{raw_body}",
        hash_alg=hashlib.sha256,
        encoder=hex_encoder,
    )
    req = make_request(headers={}, body=json_body, raw_body=json_body_bytes)
    seed_header(verifier, req, "X-Signature")
    assert verifier.verify(req).ok is True


def test_signing_with_timestamp_header_and_literal_prefix_in_expected_value(hex_encoder, json_body, json_body_bytes):
    # Pattern: "v0:{header}:{raw_body}" -> expected "v0={digest}"
    verifier = HmacSignatureVerifier(
        key="ts-secret",
        signature_header="X-Signature-TS",
        message_template="v0:{$request.header.X-Event-Timestamp}:{raw_body}",
        hash_alg=hashlib.sha256,
        encoder=hex_encoder,
        signature_value_template="v0={digest}",
    )
    req = make_request(headers={"X-Event-Timestamp": "1724925600"}, body=json_body, raw_body=json_body_bytes)
    seed_header(verifier, req, "X-Signature-TS")
    assert verifier.verify(req).ok is True


def test_signing_raw_body_with_prefixed_signature_value_template(hex_encoder, json_body, json_body_bytes):
    # Pattern: "{raw_body}" -> expected "sha256={digest}"
    verifier = HmacSignatureVerifier(
        key="prefixed-secret",
        signature_header="X-Digest-256",
        message_template="{raw_body}",
        hash_alg=hashlib.sha256,
        encoder=hex_encoder,
        signature_value_template="sha256={digest}",
    )
    req = make_request(headers={}, body=json_body, raw_body=json_body_bytes)
    seed_header(verifier, req, "X-Digest-256")
    assert verifier.verify(req).ok is True


def test_signing_raw_body_with_base64_encoding(b64_encoder, json_body, json_body_bytes):
    verifier = HmacSignatureVerifier(
        key="b64-secret",
        signature_header="X-B64-Digest",
        message_template="{raw_body}",
        hash_alg=hashlib.sha256,
        encoder=b64_encoder,
    )
    req = make_request(headers={}, body=json_body, raw_body=json_body_bytes)
    seed_header(verifier, req, "X-B64-Digest")
    assert verifier.verify(req).ok is True


def test_signing_path_plus_raw_body_with_sha512_and_base64(b64_encoder, json_body, json_body_bytes):
    verifier = HmacSignatureVerifier(
        key="sha512-secret",
        signature_header="X-Path-Body-Digest",
        message_template="{$request.path}:{raw_body}",
        hash_alg=hashlib.sha512,
        encoder=b64_encoder,
    )
    req = make_request(headers={}, path="/orders/123", body=json_body, raw_body=json_body_bytes)
    seed_header(verifier, req, "X-Path-Body-Digest")
    assert verifier.verify(req).ok is True


def test_signing_json_pointer_value_concatenated_with_raw_body(hex_encoder, json_body, json_body_bytes):
    verifier = HmacSignatureVerifier(
        key="jsonptr-secret",
        signature_header="X-JsonPtr-Digest",
        message_template="{$request.body#/event/id}:{raw_body}",
        hash_alg=hashlib.sha256,
        encoder=hex_encoder,
    )
    req = make_request(headers={}, body=json_body, raw_body=json_body_bytes)
    seed_header(verifier, req, "X-JsonPtr-Digest")
    assert verifier.verify(req).ok is True


def test_signing_method_url_and_raw_body(hex_encoder, json_body, json_body_bytes):
    verifier = HmacSignatureVerifier(
        key="method-url-secret",
        signature_header="X-Method-Url-Digest",
        message_template="{$method}:{$url}:{raw_body}",
        hash_alg=hashlib.sha256,
        encoder=hex_encoder,
    )
    req = make_request(headers={}, method="POST", url="https://api.example.com/orders",
                       body=json_body, raw_body=json_body_bytes)
    seed_header(verifier, req, "X-Method-Url-Digest")
    assert verifier.verify(req).ok is True


def test_signing_header_path_and_json_pointer_plus_raw_with_prefixed_value(hex_encoder, json_body, json_body_bytes):
    verifier = HmacSignatureVerifier(
        key="composite-secret",
        signature_header="X-Composite-Digest",
        message_template="{$request.header.X-Event-TS}:{$request.path}:{$request.body#/payload/checksum}:{raw_body}",
        hash_alg=hashlib.sha256,
        encoder=hex_encoder,
        signature_value_template="composite={digest}",
    )
    req = make_request(headers={"X-Event-TS": "1724925600"}, path="/orders/123",
                       body=json_body, raw_body=json_body_bytes)
    seed_header(verifier, req, "X-Composite-Digest")
    assert verifier.verify(req).ok is True


# ================== EDGE CASES / NEGATIVE ==================

def test_failed_when_signature_header_missing(hex_encoder, json_body, json_body_bytes):
    verifier = HmacSignatureVerifier(
        key="secret",
        signature_header="X-Required",
        message_template="{raw_body}",
        hash_alg=hashlib.sha256,
        encoder=hex_encoder,
    )
    req = make_request(headers={}, body=json_body, raw_body=json_body_bytes)
    result = verifier.verify(req)
    assert result.ok is False
    assert isinstance(result.error, Exception)


def test_failed_on_signature_mismatch_returns_signature_verification_error(hex_encoder, json_body, json_body_bytes):
    verifier = HmacSignatureVerifier(
        key="secret",
        signature_header="X-Signature",
        message_template="{raw_body}",
        hash_alg=hashlib.sha256,
        encoder=hex_encoder,
    )
    req = make_request(headers={"X-Signature": "wrong"}, body=json_body, raw_body=json_body_bytes)
    result = verifier.verify(req)
    assert result.ok is False
    assert isinstance(result.error, SignatureVerificationError)


@pytest.mark.parametrize("header_name", ["X-SIGNATURE", "x-signature", "X-Signature"])
def test_header_lookup_is_case_insensitive(hex_encoder, header_name, json_body, json_body_bytes):
    verifier = HmacSignatureVerifier(
        key="secret123",
        signature_header="X-Signature",
        message_template="{raw_body}",
        hash_alg=hashlib.sha256,
        encoder=hex_encoder,
    )
    req = make_request(headers={}, body=json_body, raw_body=json_body_bytes)
    sig = verifier.compute_expected_signature(req)
    req.headers = {header_name: sig}
    assert verifier.verify(req).ok is True


def test_raw_body_placeholder_falls_back_to_text_body_when_bytes_missing(hex_encoder):
    body = '{"a":1}'
    verifier = HmacSignatureVerifier(
        key="secret",
        signature_header="X-Signature",
        message_template="{raw_body}",
        hash_alg=hashlib.sha256,
        encoder=hex_encoder,
    )
    req = make_request(headers={}, body=body, raw_body=None)
    seed_header(verifier, req, "X-Signature")
    assert verifier.verify(req).ok is True


def test_missing_json_pointer_resolves_to_empty_string_but_is_consistent_with_compute(json_body, json_body_bytes, hex_encoder):
    # Signed message becomes ":<raw_body>"
    verifier = HmacSignatureVerifier(
        key="secret",
        signature_header="X-Signature",
        message_template="{$request.body#/does/not/exist}:{raw_body}",
        hash_alg=hashlib.sha256,
        encoder=hex_encoder,
    )
    req = make_request(headers={}, body=json_body, raw_body=json_body_bytes)
    seed_header(verifier, req, "X-Signature")
    assert verifier.verify(req).ok is True


def test_request_query_and_method_can_be_used_in_template(hex_encoder, json_body, json_body_bytes):
    verifier = HmacSignatureVerifier(
        key="secret",
        signature_header="X-Signature",
        message_template="{$method}:{$request.query.foo}:{raw_body}",
        hash_alg=hashlib.sha256,
        encoder=hex_encoder,
    )
    req = make_request(headers={}, method="GET", query={"foo": ["bar", "baz"]},
                       body=json_body, raw_body=json_body_bytes)
    seed_header(verifier, req, "X-Signature")
    assert verifier.verify(req).ok is True


@pytest.mark.parametrize(
    "bad_template",
    [
        "prefix:{$request.header.X-TS:{raw_body}",  # unclosed expr
        "{$}: {raw_body}",                          # empty expr
    ],
)
def test_constructor_raises_on_invalid_template(hex_encoder, bad_template):
    with pytest.raises(ValueError):
        HmacSignatureVerifier(
            key="k",
            signature_header="X-Signature",
            message_template=bad_template,
            hash_alg=hashlib.sha256,
            encoder=hex_encoder,
        )


@pytest.mark.parametrize(
    "encoder_cls, value_prefix",
    [
        (HexEncoder, "sha256="),
        (Base64Encoder, "sha256="),
    ],
)
def test_signature_value_template_prefix_is_applied_consistently(encoder_cls, value_prefix, json_body, json_body_bytes):
    encoder = encoder_cls()
    verifier = HmacSignatureVerifier(
        key="secret",
        signature_header="X-Digest",
        message_template="{raw_body}",
        hash_alg=hashlib.sha256,
        encoder=encoder,
        signature_value_template="sha256={digest}",
    )
    req = make_request(headers={}, body=json_body, raw_body=json_body_bytes)
    sig = verifier.compute_expected_signature(req)
    assert sig.startswith(value_prefix)
    req.headers["X-Digest"] = sig
    assert verifier.verify(req).ok is True
