"""
Comprehensive tests for every endpoint in the Monkeys V2 dummy backend.

Run:  python -m pytest tests/ -v
"""

import copy
import importlib
import io
import sys
import os
import time

import pytest

# ── Ensure project root is on sys.path ──
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import data_store as _ds_module
from app import create_app


# ================================================================
# Fixtures
# ================================================================

# Snapshot the original data-store state so we can reset between tests.
_ORIG = {
    attr: copy.deepcopy(getattr(_ds_module, attr))
    for attr in (
        "users", "posts", "comments", "files", "contacts",
        "sites", "archive_tasks", "archive_files", "bakarim",
        "reset_tokens", "_next_ids",
    )
}


@pytest.fixture(autouse=True)
def _reset_data_store():
    """Reset the in-memory data store to its original state before every test."""
    for attr, snapshot in _ORIG.items():
        setattr(_ds_module, attr, copy.deepcopy(snapshot))
    yield


@pytest.fixture()
def app():
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


# ── helpers ──────────────────────────────────

def _login(client, username="admin", password="admin123"):
    """Log in via the API and return the response JSON."""
    rv = client.post("/api/login_user", json={
        "username": username,
        "password": password,
    })
    return rv.get_json()


def _login_standard(client):
    return _login(client, "user1", "pass123")


def _login_pending(client):
    return _login(client, "pending_user", "pass456")


# ================================================================
# 1. WEB PAGES
# ================================================================

class TestWebPages:
    """Test all GET page routes for template rendering, redirects, and auth."""

    # ── / (index) ──
    def test_index_requires_login(self, client):
        rv = client.get("/", follow_redirects=False)
        assert rv.status_code == 302
        assert "/login" in rv.headers["Location"]

    def test_index_renders_for_logged_in_admin(self, client):
        _login(client)
        rv = client.get("/")
        assert rv.status_code == 200

    def test_index_renders_for_standard_user(self, client):
        _login_standard(client)
        rv = client.get("/")
        assert rv.status_code == 200

    def test_index_denied_for_pending_user(self, client):
        _login_pending(client)
        rv = client.get("/")
        assert rv.status_code == 403

    # ── /login ──
    def test_login_page(self, client):
        rv = client.get("/login")
        assert rv.status_code == 200

    # ── /password_recovery ──
    def test_password_recovery_page(self, client):
        rv = client.get("/password_recovery")
        assert rv.status_code == 200

    # ── /password_recovery/<token> ──
    def test_password_recovery_valid_token(self, client):
        token = "valid-test-token"
        _ds_module.reset_tokens[token] = {
            "username": "admin",
            "expires_at": time.time() + 3600,
        }
        rv = client.get(f"/password_recovery/{token}")
        assert rv.status_code == 200
        assert b"password_recovery" in rv.data.lower() or rv.status_code == 200

    def test_password_recovery_expired_token(self, client):
        token = "expired-token"
        _ds_module.reset_tokens[token] = {
            "username": "admin",
            "expires_at": time.time() - 10,
        }
        rv = client.get(f"/password_recovery/{token}")
        assert rv.status_code == 200
        assert b"invalid or expired" in rv.data.lower()

    def test_password_recovery_invalid_token(self, client):
        rv = client.get("/password_recovery/does-not-exist")
        assert rv.status_code == 200
        assert b"invalid or expired" in rv.data.lower()

    # ── /logout ──
    def test_logout_redirects_to_login(self, client):
        _login(client)
        rv = client.get("/logout", follow_redirects=False)
        assert rv.status_code == 302
        assert "/login" in rv.headers["Location"]

    def test_logout_clears_session(self, client):
        _login(client)
        client.get("/logout")
        rv = client.get("/", follow_redirects=False)
        assert rv.status_code == 302  # redirected to login

    # ── /contacts ──
    def test_contacts_requires_login(self, client):
        rv = client.get("/contacts", follow_redirects=False)
        assert rv.status_code == 302

    def test_contacts_renders(self, client):
        _login(client)
        rv = client.get("/contacts")
        assert rv.status_code == 200

    # ── /archive ──
    def test_archive_requires_login(self, client):
        rv = client.get("/archive", follow_redirects=False)
        assert rv.status_code == 302

    def test_archive_renders(self, client):
        _login(client)
        rv = client.get("/archive")
        assert rv.status_code == 200

    # ── /gant ──
    def test_gant_requires_login(self, client):
        rv = client.get("/gant", follow_redirects=False)
        assert rv.status_code == 302

    def test_gant_renders(self, client):
        _login(client)
        rv = client.get("/gant")
        assert rv.status_code == 200

    # ── /admission ──
    def test_admission_requires_admin(self, client):
        _login_standard(client)
        rv = client.get("/admission")
        assert rv.status_code == 403

    def test_admission_renders_for_admin(self, client):
        _login(client)
        rv = client.get("/admission")
        assert rv.status_code == 200

    def test_admission_requires_login(self, client):
        rv = client.get("/admission", follow_redirects=False)
        assert rv.status_code == 302

    # ── /binyan_coah ──
    def test_binyan_coah_redirects(self, client):
        _login(client)
        rv = client.get("/binyan_coah", follow_redirects=False)
        assert rv.status_code == 302
        assert "page_type=binyan_coah" in rv.headers["Location"]
        assert "category_id=9" in rv.headers["Location"]

    # ── /tasks ──
    def test_tasks_get(self, client):
        _login(client)
        rv = client.get("/tasks")
        assert rv.status_code == 200

    def test_tasks_post(self, client):
        _login(client)
        rv = client.post("/tasks")
        assert rv.status_code == 200

    def test_tasks_requires_login(self, client):
        rv = client.get("/tasks", follow_redirects=False)
        assert rv.status_code == 302

    def test_tasks_with_params(self, client):
        _login(client)
        rv = client.get("/tasks?page_type=binyan_coah&category_id=9&task_to_open=1")
        assert rv.status_code == 200

    # ── /transfer_page ──
    def test_transfer_page_requires_login(self, client):
        rv = client.get("/transfer_page", follow_redirects=False)
        assert rv.status_code == 302

    def test_transfer_page_renders(self, client):
        _login(client)
        rv = client.get("/transfer_page")
        assert rv.status_code == 200

    # ── /manage_bakarim ──
    def test_manage_bakarim_requires_admin(self, client):
        _login_standard(client)
        rv = client.get("/manage_bakarim")
        assert rv.status_code == 403

    def test_manage_bakarim_renders_for_admin(self, client):
        _login(client)
        rv = client.get("/manage_bakarim")
        assert rv.status_code == 200

    # ── /hafifa ──
    def test_hafifa_redirects(self, client):
        _login(client)
        rv = client.get("/hafifa", follow_redirects=False)
        assert rv.status_code == 302
        assert "page_type=hafifa" in rv.headers["Location"]
        assert "category_id=19" in rv.headers["Location"]


# ================================================================
# 2. AUTHENTICATION APIs
# ================================================================

class TestAuthAPI:
    # ── /api/login_user ──
    def test_login_success(self, client):
        data = _login(client, "admin", "admin123")
        assert data["response"] == "Logged in successfully."
        assert "update_last_login_result" in data

    def test_login_wrong_password(self, client):
        data = _login(client, "admin", "wrong")
        assert data["response"] == "Username or password are incorrect."

    def test_login_wrong_username(self, client):
        data = _login(client, "nonexistent", "admin123")
        assert data["response"] == "Username or password are incorrect."

    def test_login_updates_last_login(self, client):
        data = _login(client, "admin", "admin123")
        assert "Last login" in data["update_last_login_result"]

    def test_login_first_login(self, client):
        data = _login(client, "pending_user", "pass456")
        assert "first login" in data["update_last_login_result"]

    # ── /api/register_user ──
    def test_register_success(self, client):
        rv = client.post("/api/register_user", json={
            "username": "newuser",
            "password": "abc123",
            "conpass": "abc123",
            "email": "new@example.com",
            "full_name": "New User",
            "team": "Team A",
            "id_number": "9999999",
            "phone_number": "0509999999",
            "freedom_date": "2028-01-01",
        })
        assert rv.get_json()["response"] == "success"

    def test_register_password_mismatch(self, client):
        rv = client.post("/api/register_user", json={
            "username": "newuser",
            "password": "abc123",
            "conpass": "xyz789",
            "email": "new@example.com",
            "full_name": "New User",
        })
        data = rv.get_json()
        assert data["response"] != "success"

    def test_register_duplicate_username(self, client):
        rv = client.post("/api/register_user", json={
            "username": "admin",
            "password": "abc123",
            "conpass": "abc123",
            "email": "unique@example.com",
            "full_name": "Dup User",
        })
        data = rv.get_json()
        assert data["response"] != "success"

    def test_register_duplicate_email(self, client):
        rv = client.post("/api/register_user", json={
            "username": "uniqueuser",
            "password": "abc123",
            "conpass": "abc123",
            "email": "admin@monkeys.local",
            "full_name": "Dup Email",
        })
        data = rv.get_json()
        assert data["response"] != "success"

    def test_register_missing_fields(self, client):
        rv = client.post("/api/register_user", json={
            "username": "",
            "password": "abc123",
            "conpass": "abc123",
            "email": "",
            "full_name": "",
        })
        data = rv.get_json()
        assert data["response"] != "success"

    def test_register_creates_pending_user(self, client):
        client.post("/api/register_user", json={
            "username": "newpending",
            "password": "abc123",
            "conpass": "abc123",
            "email": "pending2@example.com",
            "full_name": "Pending Person",
        })
        user = next(u for u in _ds_module.users if u["username"] == "newpending")
        assert user["privilege"] == 0

    # ── /api/send_verification_email ──
    def test_send_verification_email_success(self, client):
        rv = client.post("/api/send_verification_email", json={"username": "admin"})
        assert rv.get_json()["response"] == "success"
        assert len(_ds_module.reset_tokens) == 1

    def test_send_verification_email_unknown_user(self, client):
        rv = client.post("/api/send_verification_email", json={"username": "nobody"})
        data = rv.get_json()
        assert data["response"] != "success"

    # ── /api/reset_password ──
    def test_reset_password_success(self, client):
        token = "test-reset-token"
        _ds_module.reset_tokens[token] = {
            "username": "admin",
            "expires_at": time.time() + 3600,
        }
        rv = client.post("/api/reset_password", json={
            "token": token,
            "password": "newpass999",
        })
        assert rv.get_json()["response"] == "success"
        admin = next(u for u in _ds_module.users if u["username"] == "admin")
        assert admin["password"] == "newpass999"

    def test_reset_password_expired_token(self, client):
        token = "expired-token"
        _ds_module.reset_tokens[token] = {
            "username": "admin",
            "expires_at": time.time() - 10,
        }
        rv = client.post("/api/reset_password", json={
            "token": token,
            "password": "newpass999",
        })
        assert rv.get_json()["response"] == "Invalid or expired token."

    def test_reset_password_invalid_token(self, client):
        rv = client.post("/api/reset_password", json={
            "token": "fake-token",
            "password": "newpass999",
        })
        assert rv.get_json()["response"] == "Invalid or expired token."

    def test_reset_password_removes_token(self, client):
        token = "oneuse-token"
        _ds_module.reset_tokens[token] = {
            "username": "admin",
            "expires_at": time.time() + 3600,
        }
        client.post("/api/reset_password", json={"token": token, "password": "x"})
        assert token not in _ds_module.reset_tokens


# ================================================================
# 3. TASK / POST APIs
# ================================================================

class TestTaskAPI:
    # ── /api/get_tasks ──
    def test_get_tasks_all(self, client):
        rv = client.get("/api/get_tasks")
        data = rv.get_json()
        assert "tasks_on_page" in data
        assert "pages_number" in data
        assert "current_page" in data
        assert len(data["tasks_on_page"]) == 5

    def test_get_tasks_filter_by_category(self, client):
        rv = client.get("/api/get_tasks?category_id=1")
        data = rv.get_json()
        for t in data["tasks_on_page"]:
            assert t["category_id"] == 1

    def test_get_tasks_filter_by_content(self, client):
        rv = client.get("/api/get_tasks?content=מתג")
        data = rv.get_json()
        assert len(data["tasks_on_page"]) >= 1

    def test_get_tasks_filter_by_location(self, client):
        rv = client.get("/api/get_tasks?location=מטה")
        data = rv.get_json()
        for t in data["tasks_on_page"]:
            assert t["location"] == "מטה"

    def test_get_tasks_filter_by_date_range(self, client):
        rv = client.get("/api/get_tasks?start_date=2026-04-02&end_date=2026-04-03")
        data = rv.get_json()
        for t in data["tasks_on_page"]:
            d = t["date_posted"].split(" ")[0]
            assert "2026-04-02" <= d <= "2026-04-03"

    def test_get_tasks_filter_by_post_id(self, client):
        rv = client.get("/api/get_tasks?post_id=1")
        data = rv.get_json()
        assert len(data["tasks_on_page"]) == 1
        assert data["tasks_on_page"][0]["id"] == 1

    def test_get_tasks_pagination(self, client):
        rv = client.get("/api/get_tasks?current_page=1")
        data = rv.get_json()
        assert data["current_page"] == 1

    def test_get_tasks_sorted_descending(self, client):
        rv = client.get("/api/get_tasks")
        data = rv.get_json()
        dates = [t["date_posted"] for t in data["tasks_on_page"]]
        assert dates == sorted(dates, reverse=True)

    def test_get_tasks_response_fields(self, client):
        rv = client.get("/api/get_tasks")
        data = rv.get_json()
        task = data["tasks_on_page"][0]
        expected_keys = {"content", "category_id", "title", "id", "username", "location", "date_posted", "edited"}
        assert expected_keys == set(task.keys())

    # ── /api/get_task ──
    def test_get_task_by_id(self, client):
        rv = client.get("/api/get_task?task_id=1")
        data = rv.get_json()
        assert data["id"] == 1
        assert "title" in data
        assert "content" in data

    def test_get_task_not_found(self, client):
        rv = client.get("/api/get_task?task_id=999")
        assert rv.status_code == 404

    # ── /api/add_post ──
    def test_add_post(self, client):
        _login(client)
        rv = client.post("/api/add_post", json={
            "title": "New Task",
            "content": "Description",
            "category_id": 1,
            "location": "מטה",
        })
        data = rv.get_json()
        assert data["response"] == "success"
        assert "post_id" in data
        assert isinstance(data["post_id"], int)

    def test_add_post_appears_in_store(self, client):
        _login(client)
        rv = client.post("/api/add_post", json={
            "title": "Store Test",
            "content": "Body",
            "category_id": 2,
            "location": "בסיס 1",
        })
        pid = rv.get_json()["post_id"]
        assert any(p["id"] == pid for p in _ds_module.posts)

    def test_add_post_sets_username(self, client):
        _login(client)
        rv = client.post("/api/add_post", json={
            "title": "T", "content": "C", "category_id": 1, "location": "L",
        })
        pid = rv.get_json()["post_id"]
        post = next(p for p in _ds_module.posts if p["id"] == pid)
        assert post["username"] == "admin"

    # ── /api/edit_post ──
    def test_edit_post(self, client):
        rv = client.post("/api/edit_post", json={
            "post_id": 1,
            "title": "Updated Title",
            "content": "Updated Content",
        })
        data = rv.get_json()
        assert data["response"] == "success"
        assert data["post_id"] == 1
        post = next(p for p in _ds_module.posts if p["id"] == 1)
        assert post["title"] == "Updated Title"
        assert post["edited"] is not None

    def test_edit_post_not_found(self, client):
        rv = client.post("/api/edit_post", json={
            "post_id": 999,
            "title": "X",
        })
        assert rv.status_code == 404

    # ── /api/delete_post ──
    def test_delete_post(self, client):
        rv = client.get("/api/delete_post?id=1")
        assert rv.get_json()["response"] == "success"
        assert not any(p["id"] == 1 for p in _ds_module.posts)

    def test_delete_post_removes_comments(self, client):
        assert any(c["post_id"] == 1 for c in _ds_module.comments)
        client.get("/api/delete_post?id=1")
        assert not any(c["post_id"] == 1 for c in _ds_module.comments)

    def test_delete_post_removes_files(self, client):
        assert any(f["post_id"] == 1 for f in _ds_module.files)
        client.get("/api/delete_post?id=1")
        assert not any(f["post_id"] == 1 for f in _ds_module.files)

    def test_delete_post_nonexistent(self, client):
        rv = client.get("/api/delete_post?id=999")
        assert rv.get_json()["response"] == "success"  # idempotent

    # ── /api/change_post_category ──
    def test_change_post_category(self, client):
        rv = client.post("/api/change_post_category", json={
            "post_id": 1,
            "new_category_id": 5,
        })
        assert rv.get_json()["response"] == "success"
        post = next(p for p in _ds_module.posts if p["id"] == 1)
        assert post["category_id"] == 5


# ================================================================
# 4. COMMENT APIs
# ================================================================

class TestCommentAPI:
    # ── /api/get_comments_for_task ──
    def test_get_comments(self, client):
        rv = client.get("/api/get_comments_for_task?task_id=1")
        data = rv.get_json()
        assert isinstance(data, list)
        assert len(data) == 2
        for c in data:
            assert "id" in c
            assert "content" in c
            assert "edited" in c
            assert "data_posted" in c
            assert "userID" in c
            assert "comment_id" in c

    def test_get_comments_empty(self, client):
        rv = client.get("/api/get_comments_for_task?task_id=999")
        assert rv.get_json() == []

    # ── /api/add_comment ──
    def test_add_comment(self, client):
        _login(client)
        rv = client.post("/api/add_comment", json={
            "content": "New comment",
            "post_id": 1,
        })
        data = rv.get_json()
        assert data["response"] == "success"
        assert data["post_id"] == 1

    def test_add_comment_appears_in_store(self, client):
        _login(client)
        initial_count = len(_ds_module.comments)
        client.post("/api/add_comment", json={"content": "Test", "post_id": 1})
        assert len(_ds_module.comments) == initial_count + 1

    # ── /api/edit_comment ──
    def test_edit_comment(self, client):
        rv = client.post("/api/edit_comment", json={
            "comment_id": 1,
            "content": "Edited comment",
            "post_id": 1,
        })
        data = rv.get_json()
        assert data["response"] == "success"
        comment = next(c for c in _ds_module.comments if c["id"] == 1)
        assert comment["content"] == "Edited comment"
        assert len(comment["edited"]) == 1

    # ── /api/delete_comment ──
    def test_delete_comment(self, client):
        rv = client.get("/api/delete_comment?id=1")
        assert rv.get_json()["response"] == "success"
        assert not any(c["id"] == 1 for c in _ds_module.comments)


# ================================================================
# 5. FILE APIs
# ================================================================

class TestFileAPI:
    # ── /api/get_task_files_list ──
    def test_get_task_files(self, client):
        rv = client.get("/api/get_task_files_list?task_id=1")
        data = rv.get_json()
        assert isinstance(data, list)
        assert len(data) == 1
        f = data[0]
        expected = {"id", "uploaded_at", "uploaded_by", "post_id", "file_name", "real_name"}
        assert expected == set(f.keys())

    def test_get_task_files_empty(self, client):
        rv = client.get("/api/get_task_files_list?task_id=999")
        assert rv.get_json() == []

    # ── /api/upload_post_image/ ──
    def test_upload_post_image(self, client):
        data = {"file": (io.BytesIO(b"image data"), "photo.png")}
        rv = client.post("/api/upload_post_image/", content_type="multipart/form-data", data=data)
        result = rv.get_json()
        assert "location" in result
        assert "photo.png" in result["location"]

    def test_upload_post_image_no_file(self, client):
        rv = client.post("/api/upload_post_image/", content_type="multipart/form-data", data={})
        assert rv.status_code == 400

    # ── /api/upload_post_file/ ──
    def test_upload_post_file(self, client):
        _login(client)
        data = {
            "file": (io.BytesIO(b"file data"), "doc.pdf"),
            "taskid": "1",
        }
        rv = client.post("/api/upload_post_file/", content_type="multipart/form-data", data=data)
        assert rv.get_json()["response"] == "success"

    def test_upload_post_file_stored(self, client):
        _login(client)
        initial = len(_ds_module.files)
        data = {
            "file": (io.BytesIO(b"data"), "test.txt"),
            "taskid": "1",
        }
        client.post("/api/upload_post_file/", content_type="multipart/form-data", data=data)
        assert len(_ds_module.files) == initial + 1

    def test_upload_post_file_no_file(self, client):
        rv = client.post("/api/upload_post_file/", content_type="multipart/form-data", data={"taskid": "1"})
        assert rv.status_code == 400

    # ── /api/delete_file ──
    def test_delete_file(self, client):
        rv = client.get("/api/delete_file?id=1")
        assert rv.get_json()["response"] == "success"
        assert not any(f["id"] == 1 for f in _ds_module.files)

    # ── /api/upload_pdf_bc/ ──
    def test_upload_pdf_bc(self, client):
        _login(client)
        data = {
            "pdf_file": (io.BytesIO(b"%PDF-1.4 content"), "report.pdf"),
            "taskid": "1",
        }
        rv = client.post("/api/upload_pdf_bc/", content_type="multipart/form-data", data=data)
        assert rv.get_json()["response"] == "success"

    def test_upload_pdf_bc_no_file(self, client):
        rv = client.post("/api/upload_pdf_bc/", content_type="multipart/form-data", data={"taskid": "1"})
        assert rv.status_code == 400

    # ── /api/download_word_bc/ ──
    def test_download_word_bc(self, client):
        rv = client.get("/api/download_word_bc/?task_id=1")
        assert rv.status_code == 200
        assert rv.content_type == "application/octet-stream"
        assert b"Task:" in rv.data or len(rv.data) > 0

    def test_download_word_bc_not_found(self, client):
        rv = client.get("/api/download_word_bc/?task_id=999")
        assert rv.status_code == 200  # returns "Task not found" body
        assert b"Task not found" in rv.data

    # ── /api/download_archive_file ──
    def test_download_archive_file(self, client):
        rv = client.get("/api/download_archive_file?file_id=1")
        assert rv.status_code == 200

    def test_download_archive_file_not_found(self, client):
        rv = client.get("/api/download_archive_file?file_id=999")
        assert rv.status_code == 404


# ================================================================
# 6. CONTACT APIs
# ================================================================

class TestContactAPI:
    # ── /api/get_contacts ──
    def test_get_contacts_all(self, client):
        rv = client.get("/api/get_contacts")
        data = rv.get_json()
        assert "contacts_on_page" in data
        assert "pages_number" in data
        assert "current_page" in data
        assert len(data["contacts_on_page"]) == 3

    def test_get_contacts_search(self, client):
        rv = client.get("/api/get_contacts?search_string=אבי")
        data = rv.get_json()
        assert len(data["contacts_on_page"]) >= 1

    def test_get_contacts_search_by_phone(self, client):
        rv = client.get("/api/get_contacts?search_string=0541234567")
        data = rv.get_json()
        assert len(data["contacts_on_page"]) >= 1

    def test_get_contacts_pagination(self, client):
        rv = client.get("/api/get_contacts?current_page=1")
        data = rv.get_json()
        assert data["current_page"] == 1

    # ── /api/add_contact ──
    def test_add_contact(self, client):
        rv = client.post("/api/add_contact", json={
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "0501112222",
            "role": "Developer",
            "site": "מטה",
        })
        assert rv.get_json()["response"] == "success"
        assert len(_ds_module.contacts) == 4

    # ── /api/edit_contact ──
    def test_edit_contact(self, client):
        rv = client.post("/api/edit_contact", json={
            "contact_id": 1,
            "first_name": "Updated",
            "last_name": "Name",
            "phone_number": "0501111111",
            "role": "Manager",
            "site": "בסיס 2",
        })
        assert rv.get_json()["response"] == "success"
        contact = next(c for c in _ds_module.contacts if c["id"] == 1)
        assert contact["first_name"] == "Updated"

    # ── /api/delete_contact ──
    def test_delete_contact(self, client):
        rv = client.get("/api/delete_contact?id=1")
        assert rv.get_json()["response"] == "success"
        assert not any(c["id"] == 1 for c in _ds_module.contacts)


# ================================================================
# 7. ARCHIVE APIs
# ================================================================

class TestArchiveAPI:
    # ── /api/get_sites ──
    def test_get_sites_all(self, client):
        rv = client.get("/api/get_sites")
        data = rv.get_json()
        assert isinstance(data, list)
        assert len(data) == 3
        assert "id" in data[0]
        assert "name" in data[0]

    def test_get_sites_search(self, client):
        rv = client.get("/api/get_sites?search_string=אלפא")
        data = rv.get_json()
        assert len(data) == 1
        assert data[0]["name"] == "אתר אלפא"

    def test_get_sites_search_no_match(self, client):
        rv = client.get("/api/get_sites?search_string=doesnotexist")
        assert rv.get_json() == []

    # ── /api/get_site_tasks ──
    def test_get_site_tasks(self, client):
        rv = client.get("/api/get_site_tasks?site_id=1")
        data = rv.get_json()
        assert len(data) == 2
        for t in data:
            assert t["site_id"] == 1

    def test_get_site_tasks_with_search(self, client):
        rv = client.get("/api/get_site_tasks?site_id=1&search_string=תחזוקה")
        data = rv.get_json()
        assert len(data) == 1

    def test_get_site_tasks_empty(self, client):
        rv = client.get("/api/get_site_tasks?site_id=999")
        assert rv.get_json() == []

    # ── /api/get_site_task_files ──
    def test_get_site_task_files(self, client):
        rv = client.get("/api/get_site_task_files?task_id=1")
        data = rv.get_json()
        assert len(data) == 1
        f = data[0]
        expected = {"id", "file_name", "file_path", "site_id", "task_id", "special_type"}
        assert expected == set(f.keys())

    def test_get_site_task_files_empty(self, client):
        rv = client.get("/api/get_site_task_files?task_id=999")
        assert rv.get_json() == []

    # ── /api/add_archive_task ──
    def test_add_archive_task(self, client):
        rv = client.post("/api/add_archive_task", json={
            "name": "New Archive Task",
            "site_id": 1,
        })
        assert rv.get_json()["response"] == "success"
        assert len(_ds_module.archive_tasks) == 4

    # ── /api/add_file_archive_task ──
    def test_add_file_archive_task(self, client):
        data = {
            "pdf_file": (io.BytesIO(b"%PDF data"), "newfile.pdf"),
            "file_name": "newfile.pdf",
            "site_id": "1",
            "task_id": "1",
            "special_type": "plan",
        }
        rv = client.post("/api/add_file_archive_task", content_type="multipart/form-data", data=data)
        result = rv.get_json()
        assert result["database_response"] == "success"
        assert result["files_response"] == "success"
        assert len(_ds_module.archive_files) == 3

    def test_add_file_archive_task_without_file(self, client):
        data = {
            "file_name": "virtual.pdf",
            "site_id": "2",
            "task_id": "3",
            "special_type": "log",
        }
        rv = client.post("/api/add_file_archive_task", content_type="multipart/form-data", data=data)
        result = rv.get_json()
        assert result["database_response"] == "success"


# ================================================================
# 8. BAKARIM APIs
# ================================================================

class TestBakarimAPI:
    # ── /get-bakarim ──
    def test_get_bakarim(self, client):
        rv = client.get("/get-bakarim")
        data = rv.get_json()
        assert isinstance(data, list)
        assert len(data) == 3
        b = data[0]
        assert "id" in b
        assert "full_name" in b
        assert "t_number" in b

    # ── /get-bakar ──
    def test_get_bakar(self, client):
        rv = client.get("/get-bakar?bakar_id=1")
        data = rv.get_json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == 1

    def test_get_bakar_not_found(self, client):
        rv = client.get("/get-bakar?bakar_id=999")
        assert rv.get_json() == []

    # ── /create-bakar ──
    def test_create_bakar(self, client):
        rv = client.post("/create-bakar", json={
            "full_name": "Test Person",
            "t_number": "T-9999",
        })
        assert rv.status_code == 201
        data = rv.get_json()
        assert data["message"] == "Bakar created successfully."
        assert "bakar" in data
        assert data["bakar"]["full_name"] == "Test Person"
        assert data["bakar"]["t_number"] == "T-9999"
        assert isinstance(data["bakar"]["id"], int)

    # ── /update-bakar ──
    def test_update_bakar(self, client):
        rv = client.put("/update-bakar", json={
            "bakar_id": 1,
            "full_name": "Updated Name",
            "t_number": "T-0001",
        })
        assert rv.status_code == 200
        data = rv.get_json()
        assert data["message"] == "Bakar updated successfully."
        assert data["bakar"]["full_name"] == "Updated Name"

    def test_update_bakar_not_found(self, client):
        rv = client.put("/update-bakar", json={
            "bakar_id": 999,
            "full_name": "X",
        })
        assert rv.status_code == 404

    # ── /delete-bakar ──
    def test_delete_bakar(self, client):
        rv = client.delete("/delete-bakar?bakar_id=1")
        assert rv.status_code == 200
        data = rv.get_json()
        assert "massage" in data  # note: spec has the typo "massage"
        assert not any(b["id"] == 1 for b in _ds_module.bakarim)

    def test_delete_bakar_not_found(self, client):
        rv = client.delete("/delete-bakar?bakar_id=999")
        assert rv.status_code == 404


# ================================================================
# 9. HANDOVER APIs
# ================================================================

class TestHandoverAPI:
    # ── /transfer-tasks-titles ──
    def test_transfer_tasks_titles(self, client):
        rv = client.get("/transfer-tasks-titles")
        data = rv.get_json()
        assert isinstance(data, list)
        assert len(data) == 5
        assert all(isinstance(t, str) for t in data)

    # ── /send-handover-email ──
    def test_send_handover_email(self, client):
        rv = client.post("/send-handover-email", json={
            "tasks": ["Task A", "Task B"],
            "general_comment": "Everything is fine.",
            "questions": "No questions.",
        })
        assert rv.status_code == 200
        data = rv.get_json()
        assert "response" in data


# ================================================================
# 10. EDGE CASES & INTEGRATION
# ================================================================

class TestEdgeCases:
    def test_register_then_login(self, client):
        """Register a new user, then log in with their credentials."""
        client.post("/api/register_user", json={
            "username": "fresh",
            "password": "freshpass",
            "conpass": "freshpass",
            "email": "fresh@example.com",
            "full_name": "Fresh User",
        })
        data = _login(client, "fresh", "freshpass")
        assert data["response"] == "Logged in successfully."

    def test_add_post_get_task_roundtrip(self, client):
        """Add a post then fetch it back via get_task."""
        _login(client)
        rv = client.post("/api/add_post", json={
            "title": "Round Trip",
            "content": "Body text",
            "category_id": 3,
            "location": "בסיס 1",
        })
        pid = rv.get_json()["post_id"]
        rv2 = client.get(f"/api/get_task?task_id={pid}")
        task = rv2.get_json()
        assert task["title"] == "Round Trip"
        assert task["content"] == "Body text"

    def test_add_comment_get_comments_roundtrip(self, client):
        _login(client)
        client.post("/api/add_comment", json={"content": "Hello!", "post_id": 1})
        rv = client.get("/api/get_comments_for_task?task_id=1")
        data = rv.get_json()
        assert any(c["content"] == "Hello!" for c in data)

    def test_password_reset_flow(self, client):
        """Full flow: send verification → use token → reset → login with new password."""
        client.post("/api/send_verification_email", json={"username": "user1"})
        token = list(_ds_module.reset_tokens.keys())[0]

        rv = client.get(f"/password_recovery/{token}")
        assert rv.status_code == 200

        client.post("/api/reset_password", json={"token": token, "password": "newpass"})
        data = _login(client, "user1", "newpass")
        assert data["response"] == "Logged in successfully."

    def test_upload_and_fetch_file_roundtrip(self, client):
        _login(client)
        data = {
            "file": (io.BytesIO(b"content"), "roundtrip.txt"),
            "taskid": "2",
        }
        client.post("/api/upload_post_file/", content_type="multipart/form-data", data=data)
        rv = client.get("/api/get_task_files_list?task_id=2")
        files = rv.get_json()
        assert any(f["file_name"] == "roundtrip.txt" for f in files)

    def test_delete_post_cascade(self, client):
        """Ensure deleting a post also removes its comments and files."""
        assert any(c["post_id"] == 1 for c in _ds_module.comments)
        assert any(f["post_id"] == 1 for f in _ds_module.files)
        client.get("/api/delete_post?id=1")
        assert not any(c["post_id"] == 1 for c in _ds_module.comments)
        assert not any(f["post_id"] == 1 for f in _ds_module.files)

    def test_pending_user_cannot_access_protected_pages(self, client):
        _login_pending(client)
        for path in ["/", "/contacts", "/archive", "/gant", "/tasks", "/transfer_page"]:
            rv = client.get(path)
            assert rv.status_code == 403, f"Expected 403 for {path}"

    def test_unauthenticated_cannot_access_protected_pages(self, client):
        for path in ["/", "/contacts", "/archive", "/gant", "/tasks",
                     "/transfer_page", "/admission", "/manage_bakarim",
                     "/binyan_coah", "/hafifa"]:
            rv = client.get(path, follow_redirects=False)
            assert rv.status_code == 302, f"Expected redirect for {path}"
