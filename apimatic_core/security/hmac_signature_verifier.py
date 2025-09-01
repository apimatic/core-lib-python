import hashlib
import hmac
from typing import Optional, List, Callable

from apimatic_core_interfaces.http.request import Request
from apimatic_core_interfaces.security.verification_result import VerificationResult

from apimatic_core.exceptions.signature_verification_error import SignatureVerificationError
from apimatic_core.security.encoders import DigestEncoder, HexEncoder
from apimatic_core.templating.template_engine import TemplateEngine


class HmacSignatureVerifier:
    """
    Template-driven HMAC signature verifier.

    - Builds the message to sign using a template with placeholders:
        {raw_body}
        {$method} | {$url} | {$request.path}
        {$request.header.<HeaderName>}
        {$request.query.<ParamName>}
        {$request.body#/json/pointer}
    - Computes HMAC(message, key, hash_alg) and encodes with the chosen encoder.
    - Optionally wraps the encoded digest via `signature_value_template`, e.g., "sha256={digest}".

    Parameters
    ----------
    key : str
        Shared secret (non-empty).
    signature_header : str
        Name of the header carrying the provided signature (case-insensitive lookup).
    message_template : str
        Template to construct the signed message (see placeholders above).
    hash_alg : callable, optional
        Hash function from hashlib (default: hashlib.sha256).
    encoder : DigestEncoder, optional
        Encoder for the raw HMAC bytes (default: HexEncoder()).
    signature_value_template : str, optional
        Optional template for the expected signature value, where `{digest}` is replaced
        by the encoded digest. If omitted, the expected signature is the encoded digest itself.
    """

    def __init__(
        self,
        *,
        key: str,
        signature_header: str,
        message_template: str,
        hash_alg=hashlib.sha256,
        encoder: DigestEncoder = HexEncoder(),
        signature_value_template: Optional[str] = None,
    ) -> None:
        # Basic config validation
        if not isinstance(key, str) or not key:
            raise ValueError("key must be a non-empty string.")
        if not isinstance(signature_header, str) or not signature_header.strip():
            raise ValueError("signature_header must be a non-empty string.")
        if not isinstance(message_template, str) or not message_template:
            raise ValueError("message_template must be a non-empty string.")

        self._key_bytes: bytes = key.encode("utf-8")
        self._signature_header_lc = signature_header.lower().strip()
        self._hash_alg = hash_alg
        self._encoder = encoder
        self._sig_value_template = signature_value_template

        # Compile template once for performance
        self._engine = TemplateEngine()
        self._plan: List[Callable[[Request], bytes]] = self._engine.compile(message_template)

    def verify(self, request: Request) -> VerificationResult:
        """Verify the signature in the request headers."""
        try:
            provided = self._read_signature_header(request)
            if provided is None:
                return VerificationResult.failed(
                    ValueError(f"Signature header '{self._signature_header_lc}' is missing.")
                )

            message = self._engine.render(self._plan, request)
            digest = hmac.new(self._key_bytes, message, self._hash_alg).digest()
            encoded = self._encoder.encode(digest)
            expected = (
                self._sig_value_template.replace("{digest}", encoded)
                if self._sig_value_template else
                encoded
            )

            ok = hmac.compare_digest(provided, expected)
            return VerificationResult.passed() if ok else VerificationResult.failed(
                SignatureVerificationError("Signature mismatch.")
            )
        except Exception as exc:
            return VerificationResult.failed(
                SignatureVerificationError(f"Signature Verification Failed: {exc}")
            )

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _read_signature_header(self, request: Request) -> Optional[str]:
        headers = {str(k).lower(): str(v) for k, v in (getattr(request, "headers", {}) or {}).items()}
        value = headers.get(self._signature_header_lc)
        return None if value is None or str(value).strip() == "" else str(value)
