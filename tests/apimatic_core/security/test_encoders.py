import hashlib
import base64

from apimatic_core.security.encoders import HexEncoder, Base64Encoder, Base64UrlEncoder


class TestEncoders:
    def test_hex_encoder(self):
        d = hashlib.sha256(b"abc").digest()
        assert HexEncoder().encode(d) == hashlib.sha256(b"abc").hexdigest()

    def test_base64_encoder(self):
        d = hashlib.sha256(b"abc").digest()
        assert Base64Encoder().encode(d) == base64.b64encode(d).decode("utf-8")

    def test_base64url_encoder(self):
        d = hashlib.sha256(b"abc").digest()
        out = Base64UrlEncoder().encode(d)
        assert out == base64.urlsafe_b64encode(d).decode("utf-8").rstrip("=")
        # ensure there's no padding
        assert not out.endswith("=")
