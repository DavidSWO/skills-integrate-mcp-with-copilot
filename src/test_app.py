import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException
from starlette.requests import Request

import app


def request_with_cookie(token: str | None = None) -> Request:
    headers = []
    if token:
        headers.append((b"cookie", f"{app.SESSION_COOKIE}={token}".encode()))
    return Request({"type": "http", "headers": headers})


class TeacherAuthorizationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.credentials_path = Path(self.temp_dir.name) / "teachers.json"
        record = app.create_password_record("teacher@example.edu", "correct horse battery")
        self.credentials_path.write_text(json.dumps({"teachers": [record]}), encoding="utf-8")
        self.credentials_patch = patch.object(app, "TEACHER_CREDENTIALS_FILE", self.credentials_path)
        self.credentials_patch.start()
        self.original_activities = deepcopy(app.activities)

    def tearDown(self):
        app.activities.clear()
        app.activities.update(self.original_activities)
        self.credentials_patch.stop()
        self.temp_dir.cleanup()

    def test_activity_list_remains_public(self):
        self.assertIn("Chess Club", app.get_activities())

    def test_anonymous_signup_and_unregister_are_rejected(self):
        with self.assertRaises(HTTPException) as signup_error:
            app.signup_for_activity("Chess Club", "new@example.edu", request_with_cookie())
        self.assertEqual(signup_error.exception.status_code, 401)

        with self.assertRaises(HTTPException) as unregister_error:
            app.unregister_from_activity(
                "Chess Club", "michael@mergington.edu", request_with_cookie()
            )
        self.assertEqual(unregister_error.exception.status_code, 401)

    def test_teacher_session_can_manage_registrations(self):
        token = app.create_session_token("teacher@example.edu")
        request = request_with_cookie(token)

        result = app.signup_for_activity("Chess Club", "new@example.edu", request)
        self.assertIn("Signed up", result["message"])
        self.assertIn("new@example.edu", app.activities["Chess Club"]["participants"])

        result = app.unregister_from_activity("Chess Club", "new@example.edu", request)
        self.assertIn("Unregistered", result["message"])
        self.assertNotIn("new@example.edu", app.activities["Chess Club"]["participants"])

    def test_expired_or_tampered_session_is_rejected(self):
        expired = app.create_session_token("teacher@example.edu", now=1)
        self.assertIsNone(app.current_teacher(request_with_cookie(expired), now=2 + app.SESSION_TTL_SECONDS))

        valid = app.create_session_token("teacher@example.edu")
        tampered = valid[:-1] + ("A" if valid[-1] != "A" else "B")
        self.assertIsNone(app.current_teacher(request_with_cookie(tampered)))

    def test_password_record_verifies_without_storing_plaintext(self):
        record = app.load_teacher_records()["teacher@example.edu"]
        self.assertTrue(app.password_matches(record, "correct horse battery"))
        self.assertFalse(app.password_matches(record, "wrong password"))
        self.assertNotIn("password", record)


if __name__ == "__main__":
    unittest.main()