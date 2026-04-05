"""
In-memory data store – simulates the database.
All data lives in Python dicts/lists and resets on server restart.
"""

import threading

_lock = threading.Lock()

# ── Auto-increment IDs ───────────────────────
_next_ids = {
    "user": 4,
    "post": 6,
    "comment": 4,
    "contact": 4,
    "file": 3,
    "site": 4,
    "archive_task": 4,
    "archive_file": 3,
    "bakar": 4,
}


def get_id(entity: str) -> int:
    with _lock:
        val = _next_ids[entity]
        _next_ids[entity] += 1
        return val


# ── Categories ───────────────────────────────
categories = [
    {"id": 1, "name": "תקלות רשת"},
    {"id": 2, "name": "תחזוקה"},
    {"id": 3, "name": "בקשות שירות"},
    {"id": 4, "name": "משימות יומיות"},
    {"id": 5, "name": "הדרכות"},
    {"id": 6, "name": "תקלות חומרה"},
    {"id": 7, "name": "תקלות תוכנה"},
    {"id": 8, "name": "אבטחת מידע"},
    {"id": 9, "name": "בניין כוח"},
    {"id": 10, "name": "דוחות"},
    {"id": 11, "name": "ישיבות"},
    {"id": 12, "name": "רכש"},
    {"id": 13, "name": "פרויקטים"},
    {"id": 14, "name": "תקלות תקשורת"},
    {"id": 15, "name": "גיבויים"},
    {"id": 16, "name": "שדרוגים"},
    {"id": 17, "name": "ניטור"},
    {"id": 18, "name": "תיעוד"},
    {"id": 19, "name": "הפיפה"},
    {"id": 20, "name": "אחר"},
]

# ── Locations ────────────────────────────────
locations = [
    "בסיס 1",
    "בסיס 2",
    "בסיס 3",
    "מטה",
    "שטח צפון",
    "שטח דרום",
    "שטח מרכז",
    "חדר שרתים",
    "מעבדה",
    "אחר",
]

# ── Users ────────────────────────────────────
users = [
    {
        "id": 1,
        "username": "admin",
        "password": "admin123",
        "email": "admin@monkeys.local",
        "full_name": "מנהל מערכת",
        "team": "מטה",
        "id_number": "1234567",
        "phone_number": "0501234567",
        "freedom_date": "2027-06-15",
        "privilege": 2,
        "last_login": "2026-04-05",
    },
    {
        "id": 2,
        "username": "user1",
        "password": "pass123",
        "email": "user1@monkeys.local",
        "full_name": "יוסי כהן",
        "team": "צוות א",
        "id_number": "2345678",
        "phone_number": "0502345678",
        "freedom_date": "2027-03-20",
        "privilege": 1,
        "last_login": "2026-04-04",
    },
    {
        "id": 3,
        "username": "pending_user",
        "password": "pass456",
        "email": "pending@monkeys.local",
        "full_name": "דני לוי",
        "team": "צוות ב",
        "id_number": "3456789",
        "phone_number": "0503456789",
        "freedom_date": "2027-09-01",
        "privilege": 0,
        "last_login": None,
    },
]

# ── Posts (Tasks) ────────────────────────────
posts = [
    {
        "id": 1,
        "title": "תקלה במתג ראשי",
        "content": "המתג הראשי בחדר השרתים לא מגיב. יש לבדוק חיבורים ולהחליף במידת הצורך.",
        "category_id": 1,
        "location": "חדר שרתים",
        "username": "admin",
        "user_id": 1,
        "date_posted": "2026-04-01 09:30:00",
        "edited": None,
    },
    {
        "id": 2,
        "title": "החלפת טונר מדפסת",
        "content": "יש להחליף טונר במדפסת הקומה השנייה. הטונר החלופי נמצא במחסן.",
        "category_id": 2,
        "location": "מטה",
        "username": "user1",
        "user_id": 2,
        "date_posted": "2026-04-02 14:15:00",
        "edited": None,
    },
    {
        "id": 3,
        "title": "בקשה להתקנת תוכנה",
        "content": "להתקין Office 365 על מחשב חדש בחדר 204.",
        "category_id": 3,
        "location": "בסיס 1",
        "username": "user1",
        "user_id": 2,
        "date_posted": "2026-04-03 08:00:00",
        "edited": None,
    },
    {
        "id": 4,
        "title": "עדכון מערכת הפעלה",
        "content": "יש לעדכן את כל תחנות העבודה לגרסה האחרונה של Windows.",
        "category_id": 16,
        "location": "בסיס 2",
        "username": "admin",
        "user_id": 1,
        "date_posted": "2026-04-03 11:00:00",
        "edited": "2026-04-04 09:00:00",
    },
    {
        "id": 5,
        "title": "הדרכת אבטחת מידע",
        "content": "לתאם הדרכת אבטחת מידע לכלל הצוות. לכלול נושאי פישינג וסיסמאות.",
        "category_id": 5,
        "location": "מטה",
        "username": "admin",
        "user_id": 1,
        "date_posted": "2026-04-04 16:00:00",
        "edited": None,
    },
]

# ── Comments ─────────────────────────────────
comments = [
    {
        "id": 1,
        "content": "בדקתי את המתג - נראה שיש בעיה בפורט 24. הזמנתי חלק חלופי.",
        "post_id": 1,
        "user_id": 2,
        "userID": "user1",
        "data_posted": "2026-04-01 11:00:00",
        "edited": [],
    },
    {
        "id": 2,
        "content": "החלק הגיע, אתקין מחר בבוקר.",
        "post_id": 1,
        "user_id": 2,
        "userID": "user1",
        "data_posted": "2026-04-02 15:30:00",
        "edited": [],
    },
    {
        "id": 3,
        "content": "הטונר הוחלף בהצלחה.",
        "post_id": 2,
        "user_id": 2,
        "userID": "user1",
        "data_posted": "2026-04-02 16:00:00",
        "edited": [],
    },
]

# ── Files ────────────────────────────────────
files = [
    {
        "id": 1,
        "file_name": "switch_log_20260401.txt",
        "real_name": "uploads/switch_log_20260401.txt",
        "post_id": 1,
        "uploaded_by": 1,
        "uploaded_at": "2026-04-01 10:00:00",
    },
    {
        "id": 2,
        "file_name": "toner_receipt.pdf",
        "real_name": "uploads/toner_receipt.pdf",
        "post_id": 2,
        "uploaded_by": 2,
        "uploaded_at": "2026-04-02 14:30:00",
    },
]

# ── Contacts ─────────────────────────────────
contacts = [
    {
        "id": 1,
        "first_name": "אבי",
        "last_name": "כהן",
        "phone_number": "0541234567",
        "role": "טכנאי רשת",
        "site": "בסיס 1",
    },
    {
        "id": 2,
        "first_name": "שרה",
        "last_name": "לוי",
        "phone_number": "0549876543",
        "role": "מנהלת פרויקטים",
        "site": "מטה",
    },
    {
        "id": 3,
        "first_name": "דוד",
        "last_name": "ישראלי",
        "phone_number": "0525551234",
        "role": "קצין אבטחת מידע",
        "site": "בסיס 2",
    },
]

# ── Archive: Sites ───────────────────────────
sites = [
    {"id": 1, "name": "אתר אלפא"},
    {"id": 2, "name": "אתר בטא"},
    {"id": 3, "name": "אתר גמא"},
]

# ── Archive: Tasks ───────────────────────────
archive_tasks = [
    {"id": 1, "name": "התקנת תשתיות", "site_id": 1},
    {"id": 2, "name": "תחזוקה שוטפת", "site_id": 1},
    {"id": 3, "name": "שדרוג מערכות", "site_id": 2},
]

# ── Archive: Files ───────────────────────────
archive_files = [
    {
        "id": 1,
        "file_name": "infra_plan.pdf",
        "file_path": "uploads/archive/infra_plan.pdf",
        "site_id": 1,
        "task_id": 1,
        "special_type": "plan",
    },
    {
        "id": 2,
        "file_name": "maintenance_log.pdf",
        "file_path": "uploads/archive/maintenance_log.pdf",
        "site_id": 1,
        "task_id": 2,
        "special_type": "log",
    },
]

# ── Bakarim ──────────────────────────────────
bakarim = [
    {"id": 1, "full_name": "רון דהן", "t_number": "T-1001"},
    {"id": 2, "full_name": "מיכל אברהם", "t_number": "T-1002"},
    {"id": 3, "full_name": "עמית פרץ", "t_number": "T-1003"},
]

# ── Password reset tokens ────────────────────
# { token_str: {"username": str, "expires_at": float} }
reset_tokens: dict = {}
