# tests/test_hmac_signature_verifier.py
# -*- coding: utf-8 -*-

import base64
import hashlib
import hmac
from typing import Dict, List

import pytest

from apimatic_core_interfaces.types.event_request import EventRequest
from apimatic_core.exceptions.signature_verification_error import SignatureVerificationError

# ⬇️ UPDATE THIS IMPORT PATH TO YOUR MODULE
from apimatic_core.security.hmac_signature_verifier import (
    HmacSignatureVerifier,
    HmacOrder,
    HexEncoder,
    Base64Encoder,
    Base64UrlEncoder,
)


class TestHmacSignatureVerifier:
    # -----------------------------
    # Class-scoped constants
    # -----------------------------
    KEY = "supersecretkey"
    DEFAULT_SIG_HEADER = "X-Signature"
    BODY = '{"event_type":"order_created","order_id":"123"}'

    # -----------------------------
    # Class-scoped fixture: baseline headers
    # -----------------------------
    @pytest.fixture(scope="class")
    def base_headers(self) -> Dict[str, str]:
        # common headers you might see on requests
        return {
            "Content-Type": "application/json",
            # optional; some tests override or remove these
            "X-Timestamp": "1699123456",
            "X-Request-Id": "req_123",
            "X-Nonce": "n-abc",
        }

    # -----------------------------
    # Static helpers (canonical signing helpers)
    # -----------------------------
    @staticmethod
    def _build_message(
        *,
        body: str,
        headers: Dict[str, str],
        additional_header_names: List[str],
        order: HmacOrder,
        delimiter: str,
    ) -> bytes:
        """
        Recreate the canonical string EXACTLY as the verifier does,
        then return it as UTF-8 bytes for HMAC.
        """
        norm = {str(k).lower(): str(v).strip() for k, v in headers.items()}
        parts: List[str] = []
        if order is HmacOrder.PREPEND:
            for name in additional_header_names:
                val = norm.get(name.lower())
                if val is not None:
                    parts.append(val)
            parts.append(body)
        else:
            parts.append(body)
            for name in additional_header_names:
                val = norm.get(name.lower())
                if val is not None:
                    parts.append(val)
        return delimiter.join(parts).encode("utf-8")

    @staticmethod
    def _sign_hex(key: str, message: bytes) -> str:
        return hmac.new(key.encode("utf-8"), message, hashlib.sha256).hexdigest()

    @staticmethod
    def _sign_b64(key: str, message: bytes) -> str:
        digest = hmac.new(key.encode("utf-8"), message, hashlib.sha256).digest()
        return base64.b64encode(digest).decode("utf-8")

    @staticmethod
    def _sign_b64url_nopad(key: str, message: bytes) -> str:
        digest = hmac.new(key.encode("utf-8"), message, hashlib.sha256).digest()
        return base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")

    # ==========================================================================
    # SUCCESS PATHS
    # ==========================================================================

    @pytest.mark.parametrize(
        "additional_headers,order,delimiter,encoder,signer",
        [
            # Hex, PREPEND timestamp & req-id before body
            (["X-Timestamp", "X-Request-Id"], HmacOrder.PREPEND, "|", HexEncoder(), _sign_hex.__func__),
            # Hex, APPEND nonce after body with ":" delimiter
            (["X-Nonce"], HmacOrder.APPEND, ":", HexEncoder(), _sign_hex.__func__),
            # Base64, PREPEND timestamp
            (["X-Timestamp"], HmacOrder.PREPEND, "|", Base64Encoder(), _sign_b64.__func__),
            # Base64Url (no padding), PREPEND timestamp
            (["X-Timestamp"], HmacOrder.PREPEND, "|", Base64UrlEncoder(), _sign_b64url_nopad.__func__),
        ],
        ids=[
            "hex_prepend_ts_and_reqid",
            "hex_append_nonce_with_colon",
            "base64_prepend_ts",
            "base64url_prepend_ts",
        ],
    )
    def test_verify_true_for_valid_signatures_across_encoders_orders_and_delimiters(
        self,
        base_headers,
        additional_headers,
        order,
        delimiter,
        encoder,
        signer,
    ):
        headers = dict(base_headers)  # copy
        message = self._build_message(
            body=self.BODY,
            headers=headers,
            additional_header_names=additional_headers,
            order=order,
            delimiter=delimiter,
        )
        signature = signer(self.KEY, message)
        headers[self.DEFAULT_SIG_HEADER] = signature

        verifier = HmacSignatureVerifier(
            key=self.KEY,
            signature_header=self.DEFAULT_SIG_HEADER,
            additional_headers=additional_headers,
            order=order,
            delimiter=delimiter,
            encoder=encoder,
        )
        req = EventRequest(headers=headers, body=self.BODY)
        assert verifier.verify(req) is True

    def test_verify_true_with_signature_header_whitespace_trimmed(self, base_headers):
        """
        Leading/trailing whitespace around the signature header value should be ignored.
        """
        headers = dict(base_headers)
        message = self._build_message(
            body=self.BODY,
            headers=headers,
            additional_header_names=["X-Timestamp"],
            order=HmacOrder.PREPEND,
            delimiter="|",
        )
        signature = self._sign_hex(self.KEY, message)
        headers[self.DEFAULT_SIG_HEADER] = f"   {signature}   "  # padded with spaces

        verifier = HmacSignatureVerifier(
            key=self.KEY,
            signature_header=self.DEFAULT_SIG_HEADER,
            additional_headers=["X-Timestamp"],
            order=HmacOrder.PREPEND,
            delimiter="|",
            encoder=HexEncoder(),
        )
        req = EventRequest(headers=headers, body=self.BODY)
        assert verifier.verify(req) is True

    def test_verify_true_when_configured_additional_header_is_missing(self, base_headers):
        """
        If a configured additional header is missing in the request, it is skipped,
        and verification still succeeds if the signer skipped it when generating the signature.
        """
        headers = {"Content-Type": base_headers["Content-Type"]}  # intentionally omit X-Timestamp
        message = self._build_message(
            body=self.BODY,
            headers=headers,
            additional_header_names=["X-Timestamp"],  # configured but absent → ignored
            order=HmacOrder.PREPEND,
            delimiter="|",
        )
        signature = self._sign_hex(self.KEY, message)
        headers[self.DEFAULT_SIG_HEADER] = signature

        verifier = HmacSignatureVerifier(
            key=self.KEY,
            signature_header=self.DEFAULT_SIG_HEADER,
            additional_headers=["X-Timestamp"],
            order=HmacOrder.PREPEND,
            delimiter="|",
            encoder=HexEncoder(),
        )
        req = EventRequest(headers=headers, body=self.BODY)
        assert verifier.verify(req) is True

    @pytest.mark.parametrize(
        "delimiter",
        [":", ".", ";", "~"],
        ids=["colon", "dot", "semicolon", "tilde"],
    )
    def test_verify_true_with_various_delimiters(self, base_headers, delimiter):
        headers = dict(base_headers)
        message = self._build_message(
            body=self.BODY,
            headers=headers,
            additional_header_names=["X-Timestamp"],
            order=HmacOrder.PREPEND,
            delimiter=delimiter,
        )
        signature = self._sign_hex(self.KEY, message)
        headers[self.DEFAULT_SIG_HEADER] = signature

        verifier = HmacSignatureVerifier(
            key=self.KEY,
            signature_header=self.DEFAULT_SIG_HEADER,
            additional_headers=["X-Timestamp"],
            order=HmacOrder.PREPEND,
            delimiter=delimiter,
            encoder=HexEncoder(),
        )
        req = EventRequest(headers=headers, body=self.BODY)
        assert verifier.verify(req) is True

    def test_verify_false_when_signature_mismatch(self, base_headers):
        headers = dict(base_headers)
        # Compute a valid message but provide an incorrect signature
        message = self._build_message(
            body=self.BODY,
            headers=headers,
            additional_header_names=["X-Timestamp"],
            order=HmacOrder.PREPEND,
            delimiter="|",
        )
        _ = self._sign_hex(self.KEY, message)  # not used
        headers[self.DEFAULT_SIG_HEADER] = "definitely-not-correct"

        verifier = HmacSignatureVerifier(
            key=self.KEY,
            signature_header=self.DEFAULT_SIG_HEADER,
            additional_headers=["X-Timestamp"],
            order=HmacOrder.PREPEND,
            delimiter="|",
            encoder=HexEncoder(),
        )
        req = EventRequest(headers=headers, body=self.BODY)
        assert verifier.verify(req) is False

    # ==========================================================================
    # FAILURE PATHS
    # ==========================================================================

    def test_verify_raises_signature_verification_error_when_signature_header_missing(self, base_headers):
        headers = dict(base_headers)
        headers.pop(self.DEFAULT_SIG_HEADER, None)  # ensure missing

        verifier = HmacSignatureVerifier(
            key=self.KEY,
            signature_header=self.DEFAULT_SIG_HEADER,
            additional_headers=["X-Timestamp"],
            order=HmacOrder.PREPEND,
            delimiter="|",
            encoder=HexEncoder(),
        )
        req = EventRequest(headers=headers, body=self.BODY)
        with pytest.raises(SignatureVerificationError) as exc:
            verifier.verify(req)
        assert "Signature header 'x-signature' is missing from the request." == str(exc.value)

    def test_verify_raises_signature_verification_error_when_none_encoder_missing(self, base_headers):
        headers = dict(base_headers)
        headers[self.DEFAULT_SIG_HEADER] = "definitely-not-correct"

        verifier = HmacSignatureVerifier(
            key=self.KEY,
            signature_header=self.DEFAULT_SIG_HEADER,
            additional_headers=["X-Timestamp"],
            order=HmacOrder.PREPEND,
            delimiter="|",
            encoder=None,
        )
        req = EventRequest(headers=headers, body=self.BODY)
        with pytest.raises(SignatureVerificationError) as exc:
            verifier.verify(req)
        assert "HMAC digest computation failed." == str(exc.value)
