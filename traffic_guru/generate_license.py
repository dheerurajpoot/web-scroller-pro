#!/usr/bin/env python3
"""
Admin tool: generate a license key for the current machine.
Run: python generate_license.py

This script is for the software developer/issuer only.
It generates a key tied to the current machine's hardware ID.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from license.license_manager import generate_license_key, get_machine_id


def main():
    mid = get_machine_id()
    key = generate_license_key()
    print("=" * 55)
    print("  Traffic Guru — License Key Generator")
    print("=" * 55)
    print(f"  Machine ID : {mid}")
    print(f"  License Key: {key}")
    print("=" * 55)
    print("\nShare this key with the user for activation.")


if __name__ == "__main__":
    main()
