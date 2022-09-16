from core_lib.utilities.auth_helper import AuthHelper


class TestAuthHelper:

    def test_base64_encoded_none_value(self):
        base64_encoded_value = AuthHelper.get_base64_encoded_value()
        assert base64_encoded_value is None

    def test_base64_encoded_value(self):
        base64_encoded_value = AuthHelper.get_base64_encoded_value('test_username', 'test_password')
        assert base64_encoded_value == 'dGVzdF91c2VybmFtZTp0ZXN0X3Bhc3N3b3Jk'
