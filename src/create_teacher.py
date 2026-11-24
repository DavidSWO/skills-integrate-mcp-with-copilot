import getpass
import json
import os
import sys

from app import TEACHER_CREDENTIALS_FILE, create_password_record


def main() -> int:
    if len(sys.argv) != 2 or not sys.argv[1].strip():
        print("Usage: python src/create_teacher.py <username>", file=sys.stderr)
        return 2

    username = sys.argv[1].strip().lower()
    password = getpass.getpass("Teacher password (12+ characters): ")
    if len(password) < 12:
        print("Password must be at least 12 characters.", file=sys.stderr)
        return 2
    if password != getpass.getpass("Confirm password: "):
        print("Passwords do not match.", file=sys.stderr)
        return 2

    path = TEACHER_CREDENTIALS_FILE
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("teachers"), list):
            raise ValueError("Teacher credentials file must contain a teachers list.")
    except FileNotFoundError:
        data = {"teachers": []}
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"Cannot read teacher credentials: {exc}", file=sys.stderr)
        return 1

    record = create_password_record(username, password)
    data["teachers"] = [
        existing
        for existing in data["teachers"]
        if not isinstance(existing, dict)
        or existing.get("username", "").strip().lower() != username
    ]
    data["teachers"].append(record)

    temporary_path = path.with_suffix(path.suffix + ".tmp")
    temporary_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    os.chmod(temporary_path, 0o600)
    temporary_path.replace(path)
    os.chmod(path, 0o600)
    print(f"Teacher account saved in {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())