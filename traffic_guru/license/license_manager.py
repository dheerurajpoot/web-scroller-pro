"""
License key system for Traffic Guru.

Key format  : TGURU-XXXX-XXXX-XXXX-XXXX  (base36 segments)
Validation  : HMAC-SHA256 of (machine-id + segments) vs embedded checksum
Storage     : ~/.traffic_guru/license.dat  (Fernet-encrypted JSON)
"""

import base64
import hashlib
import hmac
import json
import os
import platform
import re
import uuid
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cryptography.fernet import Fernet

# Secret used to sign keys — change this before distributing
_SIGNING_SECRET = b"TrafficGuru@2024#SecretSigningKey!"

_LICENSE_PATH = Path.home() / ".traffic_guru" / "license.dat"
_ENCRYPTION_KEY = b"TrafficGuru_Enc_32BytesKeyPad123="  # must be 32 bytes → base64 → Fernet

_fernet: "Fernet | None" = None


def _get_fernet() -> "Fernet":
    """Lazy import so tooling (e.g. generate_license.py) can run without cryptography."""
    global _fernet
    if _fernet is None:
        from cryptography.fernet import Fernet

        _fernet = Fernet(base64.urlsafe_b64encode(_ENCRYPTION_KEY[:32]))
    return _fernet


# ──────────────────────────────────────────────
#  Machine fingerprint
# ──────────────────────────────────────────────

def get_machine_id() -> str:
    """Return a stable, cross-platform machine identifier."""
    raw = f"{platform.node()}-{platform.machine()}-{platform.processor()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


# ──────────────────────────────────────────────
#  Key generation  (for internal use / tooling)
# ──────────────────────────────────────────────

def generate_license_key() -> str:
    """Generate a new valid license key (for issuance)."""
    mid = get_machine_id()
    payload = uuid.uuid4().hex[:16].upper()
    segments = [payload[i:i+4] for i in range(0, 16, 4)]
    body = "-".join(segments)
    sig = hmac.new(_SIGNING_SECRET, (mid + body).encode(), hashlib.sha256).hexdigest()[:8].upper()
    return f"TGURU-{body}-{sig}"


# ──────────────────────────────────────────────
#  Validation
# ──────────────────────────────────────────────

def _parse_key(key: str):
    """Return (body, sig) or raise ValueError."""
    key = key.strip().upper()
    pattern = r"^TGURU-([A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4})-([A-Z0-9]{8})$"
    m = re.match(pattern, key)
    if not m:
        raise ValueError("Invalid key format")
    return m.group(1), m.group(2)


def validate_key(key: str) -> tuple[bool, str]:
    """
    Returns (is_valid, message).
    Validates structure + HMAC signature.
    """
    try:
        body, sig = _parse_key(key)
    except ValueError:
        return False, "Invalid key format. Expected: TGURU-XXXX-XXXX-XXXX-XXXX-XXXXXXXX"

    mid = get_machine_id()
    expected = hmac.new(
        _SIGNING_SECRET, (mid + body).encode(), hashlib.sha256
    ).hexdigest()[:8].upper()

    if not hmac.compare_digest(sig, expected):
        return False, "License key is invalid or was generated for a different machine."

    return True, "License key is valid."


# ──────────────────────────────────────────────
#  Activation  (persist to disk)
# ──────────────────────────────────────────────

def activate(key: str) -> tuple[bool, str]:
    valid, msg = validate_key(key)
    if not valid:
        return False, msg

    data = {"key": key, "machine_id": get_machine_id(), "activated": True}
    _license_path().parent.mkdir(parents=True, exist_ok=True)
    encrypted = _get_fernet().encrypt(json.dumps(data).encode())
    _license_path().write_bytes(encrypted)
    return True, "Activation successful. Thank you for using Traffic Guru!"


def is_activated() -> bool:
    path = _license_path()
    if not path.exists():
        return False
    try:
        raw = _get_fernet().decrypt(path.read_bytes())
        data = json.loads(raw)
        key = data.get("key", "")
        stored_mid = data.get("machine_id", "")
        # Machine must match
        if stored_mid != get_machine_id():
            return False
        valid, _ = validate_key(key)
        return valid and data.get("activated", False)
    except Exception:
        return False


def deactivate():
    path = _license_path()
    if path.exists():
        path.unlink()


def _license_path() -> Path:
    return _LICENSE_PATH
