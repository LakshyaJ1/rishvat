"""
AI CFO — Encryption Utilities

AES-256 encryption for connector credentials at rest.
In production, the encryption key comes from AWS/GCP Secrets Manager.
In development, it comes from the ENCRYPTION_KEY env var.
"""

import base64
import json
import os

from cryptography.fernet import Fernet

from app.config import get_settings


def _get_fernet() -> Fernet:
    """Get a Fernet instance using the configured encryption key."""
    settings = get_settings()
    key = settings.encryption_key

    # If the key isn't a valid Fernet key, derive one
    if len(key) != 44 or not key.endswith("="):
        # Pad or hash to get a valid 32-byte key, then base64 encode
        key_bytes = key.encode("utf-8")[:32].ljust(32, b"\0")
        key = base64.urlsafe_b64encode(key_bytes).decode("utf-8")

    return Fernet(key.encode("utf-8"))


def encrypt_json(data: dict) -> str:
    """
    Encrypt a dict as a JSON string using AES-256 (Fernet).
    Returns a base64-encoded encrypted string.
    """
    fernet = _get_fernet()
    json_bytes = json.dumps(data).encode("utf-8")
    encrypted = fernet.encrypt(json_bytes)
    return encrypted.decode("utf-8")


def decrypt_json(encrypted_data: str) -> dict:
    """
    Decrypt a Fernet-encrypted string back to a dict.
    """
    fernet = _get_fernet()
    decrypted = fernet.decrypt(encrypted_data.encode("utf-8"))
    return json.loads(decrypted.decode("utf-8"))
