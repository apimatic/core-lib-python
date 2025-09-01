# tests/test_hmac_signature_verifier.py
import hashlib
from typing import Optional

import pytest
from apimatic_core_interfaces.http.request import Request

from apimatic_core.security.hmac_signature_verifier import HmacSignatureVerifier
from apimatic_core.security.encoders import HexEncoder, Base64UrlEncoder
from apimatic_core.templating.template_engine import TemplateEngine


def compute_expected_signature_text(
    *,
    key: str,
    message_template: str,
    request: Request,
    hash_alg=hashlib.sha256,
    encoder=HexEncoder(),
    signature_value_template: Optional[str] = None,
) -> str:
    """Test-only helper: reproduce the verifier’s expected signature text."""
    engine = TemplateEngine()
    plan = engine.compile(message_template)
    message = engine.render(plan, request)
    import hmac as _hmac
    digest = _hmac.new(key.encode("utf-8"), message, hash_alg).digest()
    encoded = encoder.encode(digest)
    return signature_value_template.replace("{digest}", encoded) if signature_value_template else encoded


def seed_signature(
    *,
    header_name: str,
    key: str,
    message_template: str,
    request: Request,
    hash_alg=hashlib.sha256,
    encoder=HexEncoder(),
    signature_value_template: Optional[str] = None,
) -> str:
    sig = compute_expected_signature_text(
        key=key,
        message_template=message_template,
        request=request,
        hash_alg=hash_alg,
        encoder=encoder,
        signature_value_template=signature_value_template,
    )
    request.headers[header_name] = sig
    return sig


class BoomEncoder:
    def encode(self, digest: bytes) -> str:
        raise RuntimeError("boom")


class BadHash:
    def __call__(self, *args, **kwargs):
        raise RuntimeError("hash boom")


class TestHmacSignatureVerifier:
    # ---------- happy paths ----------
    def test_raw_body_hex(self):
        key = "k1"
        header = "X-Sig"
        tpl = "{raw_body}"
        enc = HexEncoder()
        v = HmacSignatureVerifier(
            key=key,
            signature_header=header,
            message_template=tpl,
            hash_alg=hashlib.sha256,
            encoder=enc,
        )
        req = Request(headers={}, body='{"a":1}', raw_body=b'{"a":1}')
        seed_signature(header_name=header, key=key, message_template=tpl,
                       request=req, hash_alg=hashlib.sha256, encoder=enc)
        assert v.verify(req).ok

    def test_header_plus_raw_with_prefix(self):
        key = "k2"
        header = "X-Sig-Ts"
        tpl = "v0:{$request.header.X-TS}:{raw_body}"
        enc = HexEncoder()
        svt = "v0={digest}"
        v = HmacSignatureVerifier(
            key=key,
            signature_header=header,
            message_template=tpl,
            hash_alg=hashlib.sha256,
            encoder=enc,
            signature_value_template=svt,
        )
        req = Request(headers={"X-TS": "111"}, body="{}", raw_body=b"{}")
        seed_signature(header_name=header, key=key, message_template=tpl,
                       request=req, hash_alg=hashlib.sha256, encoder=enc,
                       signature_value_template=svt)
        assert v.verify(req).ok

    def test_sha512_path_plus_raw_base64url(self):
        key = "k3"
        header = "X-Webhook"
        tpl = "{$request.path}:{raw_body}"
        enc = Base64UrlEncoder()
        v = HmacSignatureVerifier(
            key=key,
            signature_header=header,
            message_template=tpl,
            hash_alg=hashlib.sha512,
            encoder=enc,
        )
        req = Request(headers={}, path="/p/1", body="{}", raw_body=b"{}")
        seed_signature(header_name=header, key=key, message_template=tpl,
                       request=req, hash_alg=hashlib.sha512, encoder=enc)
        assert v.verify(req).ok

    def test_json_pointer_plus_raw(self):
        key = "k4"
        header = "X-Json"
        tpl = "{$request.body#/event/id}:{raw_body}"
        enc = HexEncoder()
        v = HmacSignatureVerifier(
            key=key,
            signature_header=header,
            message_template=tpl,
            encoder=enc,  # default sha256
        )
        req = Request(headers={}, body='{"event":{"id":"e1"}}', raw_body=b'{"event":{"id":"e1"}}')
        seed_signature(header_name=header, key=key, message_template=tpl,
                       request=req, encoder=enc)
        assert v.verify(req).ok

    def test_method_url_plus_raw(self):
        key = "k5"
        header = "X-MU"
        tpl = "{$method}:{$url}:{raw_body}"
        enc = HexEncoder()
        v = HmacSignatureVerifier(
            key=key,
            signature_header=header,
            message_template=tpl,
            encoder=enc,
        )
        req = Request(headers={}, method="POST", url="https://ex.test/u", body="{}", raw_body=b"{}")
        seed_signature(header_name=header, key=key, message_template=tpl,
                       request=req, encoder=enc)
        assert v.verify(req).ok

    def test_composite_template_and_wrapped_value(self):
        key = "k6"
        header = "X-Comp"
        tpl = "{$request.header.X-TS}:{$request.path}:{$request.body#/payload/checksum}:{raw_body}"
        enc = HexEncoder()
        svt = "complex={digest}"
        v = HmacSignatureVerifier(
            key=key,
            signature_header=header,
            message_template=tpl,
            encoder=enc,
            signature_value_template=svt,
        )
        req = Request(headers={"X-TS": "222"}, path="/o/9",
                      body='{"payload":{"checksum":"abc"}}', raw_body=b'{"payload":{"checksum":"abc"}}')
        seed_signature(header_name=header, key=key, message_template=tpl,
                       request=req, encoder=enc, signature_value_template=svt)
        assert v.verify(req).ok

    def test_constant_signature_value_template(self):
        key = "k7"
        header = "X-Const"
        tpl = "{raw_body}"
        enc = HexEncoder()
        svt = "CONST"
        v = HmacSignatureVerifier(
            key=key,
            signature_header=header,
            message_template=tpl,
            encoder=enc,
            signature_value_template=svt,
        )
        req = Request(headers={}, body="{}", raw_body=b"{}")
        seed_signature(header_name=header, key=key, message_template=tpl,
                       request=req, encoder=enc, signature_value_template=svt)
        assert v.verify(req).ok

    def test_empty_message_when_no_body_and_no_raw(self):
        key = "k8"
        header = "X-Empty"
        tpl = "{raw_body}"
        enc = HexEncoder()
        v = HmacSignatureVerifier(
            key=key,
            signature_header=header,
            message_template=tpl,
            encoder=enc,
        )
        req = Request(headers={})
        seed_signature(header_name=header, key=key, message_template=tpl,
                       request=req, encoder=enc)
        assert v.verify(req).ok

    # ---------- negatives / branches ----------
    def test_missing_signature_header_fails(self):
        v = HmacSignatureVerifier(
            key="k9",
            signature_header="X-Missing",
            message_template="{raw_body}",
            encoder=HexEncoder(),
        )
        req = Request(headers={}, body="{}", raw_body=b"{}")
        res = v.verify(req)
        assert not res.ok and isinstance(res.error, Exception)

    def test_blank_signature_header_fails(self):
        v = HmacSignatureVerifier(
            key="k10",
            signature_header="X-Blank",
            message_template="{raw_body}",
            encoder=HexEncoder(),
        )
        req = Request(headers={"X-Blank": "   "}, body="{}", raw_body=b"{}")
        res = v.verify(req)
        assert not res.ok

    def test_signature_mismatch_fails(self):
        v = HmacSignatureVerifier(
            key="k11",
            signature_header="X-Sig",
            message_template="{raw_body}",
            encoder=HexEncoder(),
        )
        req = Request(headers={"X-Sig": "wrong"}, body="{}", raw_body=b"{}")
        res = v.verify(req)
        assert not res.ok and res.error is not None

    @pytest.mark.parametrize("header_name", ["X-SIG", "x-sig", "X-Sig"])
    def test_header_lookup_case_insensitive(self, header_name):
        key = "k12"
        header = "X-Sig"
        tpl = "{raw_body}"
        enc = HexEncoder()
        v = HmacSignatureVerifier(
            key=key,
            signature_header=header,
            message_template=tpl,
            encoder=enc,
        )
        req = Request(headers={}, body="{}", raw_body=b"{}")
        sig = compute_expected_signature_text(key=key, message_template=tpl, request=req, encoder=enc)
        req.headers = {header_name: sig}
        assert v.verify(req).ok

    def test_verify_handles_encoder_exception(self):
        v = HmacSignatureVerifier(
            key="k13",
            signature_header="X-Err",
            message_template="{raw_body}",
            encoder=BoomEncoder(),
        )
        req = Request(headers={"X-Err": "anything"}, body="{}", raw_body=b"{}")
        res = v.verify(req)
        assert not res.ok and "Signature Verification Failed" in str(res.error)

    def test_verify_handles_hash_exception(self):
        v = HmacSignatureVerifier(
            key="k14",
            signature_header="X-Err",
            message_template="{raw_body}",
            hash_alg=BadHash(),
            encoder=HexEncoder(),
        )
        req = Request(headers={"X-Err": "anything"}, body="{}", raw_body=b"{}")
        res = v.verify(req)
        assert not res.ok and "Signature Verification Failed" in str(res.error)
