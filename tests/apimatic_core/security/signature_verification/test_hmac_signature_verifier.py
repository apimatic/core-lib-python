import json
import hashlib
from typing import Callable, Optional, Union

import pytest
from apimatic_core_interfaces.http.request import Request
from apimatic_core.utilities.api_helper import ApiHelper

from apimatic_core.security.signature_verification.hmac_signature_verifier import (
    HmacSignatureVerifier,
    HexEncoder,
    Base64UrlEncoder,
    Base64Encoder,
)

# ---------------------------
# Module-level resolver factories (work with pytest parametrize)
# ---------------------------

def exact_body_bytes(request: Request) -> bytes:
    """Return the exact textual body (UTF-8). Models '{$request.body}'."""
    return (getattr(request, "body", None) or "").encode("utf-8")


def resolve_body(request: Request) -> bytes:
    """Message = '{$request.body}' (text body only)."""
    return exact_body_bytes(request)


def resolve_method_header_and_body(header_name: str) -> Callable[[Request], bytes]:
    """Message = '{method}:{header}:{body}'."""
    def _resolver(request: Request) -> bytes:
        method = getattr(request, "method", "") or ""
        headers = getattr(request, "headers", {}) or {}
        header_value = ""
        needle = header_name.lower()
        for k, v in headers.items():
            if str(k).lower() == needle:
                header_value = str(v)
                break
        prefix = f"{method}:{header_value}:".encode("utf-8")
        return prefix + exact_body_bytes(request)
    return _resolver


def resolve_pointer_and_body(pointer: str) -> Callable[[Request], bytes]:
    """Message = '<value at JSON pointer>:{body}' using ApiHelper.get_value_by_json_pointer."""
    def _resolver(request: Request) -> bytes:
        body_text = getattr(request, "body", None)
        try:
            data = json.loads(body_text) if isinstance(body_text, str) and body_text.strip() else None
        except Exception:
            data = None
        picked = ApiHelper.get_value_by_json_pointer(data, pointer) if data is not None else None
        if isinstance(picked, (dict, list)):
            head = json.dumps(picked, separators=(",", ":"), sort_keys=True).encode("utf-8")
        elif picked is None:
            head = b""
        else:
            head = str(picked).encode("utf-8")
        return head + b":" + exact_body_bytes(request)
    return _resolver


def resolve_path_and_body(request: Request) -> bytes:
    """Message = '{path}:{body}'."""
    path = getattr(request, "path", "") or ""
    return f"{path}:".encode("utf-8") + exact_body_bytes(request)


def resolve_method_url_and_body(request: Request) -> bytes:
    """Message = '{method}:{url}:{body}'."""
    method = getattr(request, "method", "") or ""
    url = getattr(request, "url", "") or ""
    return f"{method}:{url}:".encode("utf-8") + exact_body_bytes(request)


def resolve_none_returns_none(_request: Request):
    """Resolver returning None to trigger raw_body fallback in verifier."""
    return None


# ---------------------------
# Signature helpers
# ---------------------------

def compute_expected_signature(
    *,
    key: str,
    resolver: Optional[Callable[[Request], Union[str, bytes, None]]],
    request: Request,
    hash_alg=hashlib.sha256,
    encoder=HexEncoder(),
    signature_value_template: Optional[str] = None,
) -> str:
    """
    Compute expected signature string exactly like the verifier will:
    - If resolver is None or returns None -> use raw_body, else body text.
    """
    import hmac as _hmac

    # Resolve message
    if callable(resolver):
        msg = resolver(request)
        if msg is None:
            # fallback same as verifier
            raw = getattr(request, "raw_body", None)
            if isinstance(raw, (bytes, bytearray)):
                message = bytes(raw)
            else:
                message = (getattr(request, "body", None) or "").encode("utf-8")
        else:
            message = msg.encode("utf-8") if isinstance(msg, str) else msg
    else:
        raw = getattr(request, "raw_body", None)
        if isinstance(raw, (bytes, bytearray)):
            message = bytes(raw)
        else:
            message = (getattr(request, "body", None) or "").encode("utf-8")

    # HMAC + encode
    digest = _hmac.new(key.encode("utf-8"), message, hash_alg).digest()
    encoded = encoder.encode(digest)

    if signature_value_template and "{digest}" not in signature_value_template:
        return signature_value_template
    return (signature_value_template or "{digest}").replace("{digest}", encoded)


def seed_header_signature(
    *,
    header_name: str,
    key: str,
    resolver: Optional[Callable[[Request], Union[str, bytes, None]]],
    request: Request,
    hash_alg=hashlib.sha256,
    encoder=HexEncoder(),
    signature_value_template: Optional[str] = None,
) -> str:
    value = compute_expected_signature(
        key=key,
        resolver=resolver,
        request=request,
        hash_alg=hash_alg,
        encoder=encoder,
        signature_value_template=signature_value_template,
    )
    request.headers = request.headers or {}
    request.headers[header_name] = value
    return value


# ---------------------------
# Tests (wrapped in a class)
# ---------------------------

class TestHmacSignatureVerifier:
    # ---------- fixtures ----------
    @pytest.fixture
    def enc_hex(self) -> HexEncoder:
        return HexEncoder()

    @pytest.fixture
    def enc_b64(self) -> Base64Encoder:
        return Base64Encoder()

    @pytest.fixture
    def enc_b64url(self) -> Base64UrlEncoder:
        return Base64UrlEncoder()

    @pytest.fixture
    def req_minimal(self) -> Request:
        # Minimal request, no body/raw initially
        return Request(headers={})

    @pytest.fixture
    def req_json_device(self) -> Request:
        body = '{"event":{"id":"evt_1"},"payload":{"checksum":"abc"},"device":{"id":"dev_007"}}'
        return Request(
            method="POST",
            path="/devices",
            url="https://api.example.test/devices",
            headers={"X-TS": "111", "X-Mixed": "MiXeD"},
            body=body,
        )

    # ---------- happy paths ----------

    @pytest.mark.parametrize(
        "header_name,resolver,hash_alg,encoder,svt",
        [
            # 1) Body-only with sha256 hex
            ("X-Sig", resolve_body, hashlib.sha256, HexEncoder(), None),
            # 2) Method + header + body; hex with wrapper
            ("X-Sig-TS", resolve_method_header_and_body("X-TS"), hashlib.sha256, HexEncoder(), "v0={digest}"),
            # 3) JSON pointer + body; sha512 + base64url
            ("X-Json", resolve_pointer_and_body("/event/id"), hashlib.sha512, Base64UrlEncoder(), None),
            # 4) Path + body; sha256 + base64
            ("X-Path", resolve_path_and_body, hashlib.sha256, Base64Encoder(), None),
            # 5) Method + URL + body; sha512 + hex
            ("X-MU", resolve_method_url_and_body, hashlib.sha512, HexEncoder(), None),
        ],
        ids=[
            "body_only_hex_sha256",
            "method_header_body_hex_wrapped",
            "json_pointer_body_b64url_sha512",
            "path_body_b64_sha256",
            "method_url_body_hex_sha512",
        ],
    )
    def test_hmac_verifier_happy(self, header_name, resolver, hash_alg, encoder, svt, req_json_device):
        key = "test-secret"
        verifier = HmacSignatureVerifier(
            key=key,
            signature_header=header_name,
            message_resolver=resolver,
            hash_alg=hash_alg,
            encoder=encoder,
            signature_value_template=svt,
        )
        seed_header_signature(
            header_name=header_name,
            key=key,
            resolver=resolver,
            request=req_json_device,
            hash_alg=hash_alg,
            encoder=encoder,
            signature_value_template=svt,
        )
        assert verifier.verify(req_json_device).ok

    # ---------- fallback to raw_body when resolver missing or returns None ----------

    def test_none_resolver_uses_raw_body(self, enc_hex):
        key = "k-none-resolver"
        header = "X-Sig"
        verifier = HmacSignatureVerifier(
            key=key,
            signature_header=header,
            message_resolver=None,  # triggers raw_body fallback
            encoder=enc_hex,
        )
        # raw_body present; body intentionally different
        req = Request(headers={}, body='{"x": 1}', raw_body=b'{"x":1}')
        seed_header_signature(
            header_name=header,
            key=key,
            resolver=None,  # seed helper mirrors verifier fallback
            request=req,
            encoder=enc_hex,
        )
        assert verifier.verify(req).ok

    def test_resolver_returning_none_uses_raw_body(self, enc_hex):
        key = "k-none-return"
        header = "X-Sig"
        verifier = HmacSignatureVerifier(
            key=key,
            signature_header=header,
            message_resolver=resolve_none_returns_none,  # returns None => fallback
            encoder=enc_hex,
        )
        req = Request(headers={}, body='{"a": 1}', raw_body=b'{"a":1}')
        seed_header_signature(
            header_name=header,
            key=key,
            resolver=resolve_none_returns_none,
            request=req,
            encoder=enc_hex,
        )
        assert verifier.verify(req).ok

    def test_fallback_uses_text_body_when_no_raw_body(self, enc_hex):
        key = "k-fallback-text"
        header = "X-Sig"
        verifier = HmacSignatureVerifier(
            key=key,
            signature_header=header,
            message_resolver=None,  # no resolver
            encoder=enc_hex,
        )
        req = Request(headers={}, body='{"z":2}')  # no raw_body
        seed_header_signature(
            header_name=header,
            key=key,
            resolver=None,
            request=req,
            encoder=enc_hex,
        )
        assert verifier.verify(req).ok

    # ---------- header case-insensitivity & constants ----------

    @pytest.mark.parametrize("variant_header", ["X-SIG", "x-sig", "X-Sig"])
    def test_signature_header_lookup_is_case_insensitive(self, variant_header, enc_hex):
        key = "k-ci"
        header = "X-Sig"
        verifier = HmacSignatureVerifier(
            key=key,
            signature_header=header,
            message_resolver=resolve_body,
            encoder=enc_hex,
        )
        req = Request(headers={}, body="{}")
        sig = compute_expected_signature(key=key, resolver=resolve_body, request=req, encoder=enc_hex)
        req.headers = {variant_header: sig}
        assert verifier.verify(req).ok

    def test_constant_signature_literal_accepted(self, enc_hex, req_minimal):
        key = "k-const"
        header = "X-Const"
        verifier = HmacSignatureVerifier(
            key=key,
            signature_header=header,
            message_resolver=resolve_body,
            encoder=enc_hex,
            signature_value_template="CONST",
        )
        seed_header_signature(
            header_name=header,
            key=key,
            resolver=resolve_body,
            request=req_minimal,
            encoder=enc_hex,
            signature_value_template="CONST",
        )
        assert verifier.verify(req_minimal).ok

    # ---------- negative paths ----------

    def test_missing_signature_header_fails(self, req_json_device, enc_hex):
        verifier = HmacSignatureVerifier(
            key="k-missing",
            signature_header="X-Missing",
            message_resolver=resolve_body,
            encoder=enc_hex,
        )
        res = verifier.verify(req_json_device)
        assert not res.ok and res.error is not None

    def test_blank_signature_header_fails(self, enc_hex):
        verifier = HmacSignatureVerifier(
            key="k-blank",
            signature_header="X-Blank",
            message_resolver=resolve_body,
            encoder=enc_hex,
        )
        req = Request(headers={"X-Blank": "   "}, body="{}")
        res = verifier.verify(req)
        assert not res.ok

    def test_signature_mismatch_fails(self, enc_hex):
        verifier = HmacSignatureVerifier(
            key="k-mismatch",
            signature_header="X-Sig",
            message_resolver=resolve_body,
            encoder=enc_hex,
        )
        req = Request(headers={"X-Sig": "wrong"}, body="{}")
        res = verifier.verify(req)
        assert not res.ok and res.error is not None

    class ExplodingEncoder:
        def encode(self, _digest: bytes) -> str:
            raise RuntimeError("boom")

    class ExplodingHash:
        def __call__(self, *args, **kwargs):
            raise RuntimeError("hash boom")

    def test_verify_handles_encoder_exception(self, req_json_device):
        verifier = HmacSignatureVerifier(
            key="k-enc-boom",
            signature_header="X-Err",
            message_resolver=resolve_body,
            encoder=self.ExplodingEncoder(),
        )
        req_json_device.headers = {"X-Err": "anything"}
        res = verifier.verify(req_json_device)
        assert not res.ok and "Signature Verification Failed" in str(res.error)

    def test_verify_handles_hash_exception(self, req_json_device, enc_hex):
        verifier = HmacSignatureVerifier(
            key="k-hash-boom",
            signature_header="X-Err",
            message_resolver=resolve_body,
            hash_alg=self.ExplodingHash(),
            encoder=enc_hex,
        )
        req_json_device.headers = {"X-Err": "anything"}
        res = verifier.verify(req_json_device)
        assert not res.ok and "Signature Verification Failed" in str(res.error)

    def test_resolver_wrong_type_results_in_failure(self):
        def bad_resolver(_req: Request):
            return 123  # not bytes/str/None

        verifier = HmacSignatureVerifier(
            key="k-bad",
            signature_header="X-Sig",
            message_resolver=bad_resolver,
        )
        req = Request(headers={"X-Sig": "anything"}, body="{}")
        res = verifier.verify(req)
        assert not res.ok and "Signature mismatch." == str(res.error)
