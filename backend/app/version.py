import os
from pathlib import Path


def get_version():
    try:
        with open(Path(__file__).parent.parent / "VERSION", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "unknown"


def get_commit_hash():
    try:
        with open(Path(__file__).parent.parent / "COMMIT_HASH", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "unknown"
