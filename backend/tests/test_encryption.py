"""
AI CFO - Encryption and Credential Security Tests

Tests that connector credentials survive encrypt-decrypt roundtrips
and that the credential storage path works end-to-end.
"""

from app.utils.encryption import decrypt_json, encrypt_json


class TestEncryptionRoundTrip:
    """Verify AES-256 (Fernet) encryption utilities."""

    def test_encrypt_decrypt_simple_dict(self):
        """A simple dict survives the roundtrip."""
        original = {"api_key": "sk_test_abc123"}
        encrypted = encrypt_json(original)
        decrypted = decrypt_json(encrypted)
        assert decrypted == original

    def test_encrypt_decrypt_nested_dict(self):
        """A nested dict with multiple credential fields survives."""
        original = {
            "access_token": "access-sandbox-12345",
            "client_id": "client_id_xyz",
            "secret": "secret_abc",
            "env": "sandbox",
        }
        encrypted = encrypt_json(original)
        decrypted = decrypt_json(encrypted)
        assert decrypted == original

    def test_encrypted_output_is_not_plaintext(self):
        """Encrypted output does not contain the original value."""
        original = {"api_key": "sk_test_super_secret"}
        encrypted = encrypt_json(original)
        assert "sk_test_super_secret" not in encrypted

    def test_different_inputs_produce_different_ciphertexts(self):
        """Two different inputs produce different encrypted outputs."""
        a = encrypt_json({"key": "value_a"})
        b = encrypt_json({"key": "value_b"})
        assert a != b

    def test_same_input_produces_different_ciphertexts(self):
        """Fernet adds a random IV, so same input != same ciphertext."""
        data = {"api_key": "sk_test_same"}
        a = encrypt_json(data)
        b = encrypt_json(data)
        # Both decrypt to the same value
        assert decrypt_json(a) == decrypt_json(b)
        # But the encrypted strings should differ (random IV)
        assert a != b
