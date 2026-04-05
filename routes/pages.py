"""
Web page routes – renders Jinja2 templates (equivalent to Flask render_template).
"""

import time
from functools import wraps
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    session,
    request,
)

import data_store
from forms import SubmitForm

pages = Blueprint("pages", __name__)


# ── Auth decorators ──────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = session.get("user")
        if not user:
            return redirect(url_for("pages.login"))
        if user.get("privilege", 0) < 1:
            return "Access denied – account pending approval.", 403
        return f(*args, **kwargs)
    return decorated


def privilege_required(min_level):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = session.get("user")
            if not user:
                return redirect(url_for("pages.login"))
            if user.get("privilege", 0) < min_level:
                return "Access denied – insufficient privileges.", 403
            return f(*args, **kwargs)
        return decorated
    return decorator


# ── Pages ────────────────────────────────────

@pages.route("/")
@login_required
def index():
    user = session["user"]
    return render_template(
        "index.html",
        username=user["full_name"],
        freedom_date=user["freedom_date"],
    )


@pages.route("/login")
def login():
    return render_template("loginP.html")


@pages.route("/password_recovery")
def password_recovery():
    return render_template(
        "password_recovery.html", token_verified=False, token=None
    )


@pages.route("/password_recovery/<token>")
def password_recovery_token(token):
    entry = data_store.reset_tokens.get(token)
    if not entry or time.time() > entry["expires_at"]:
        return "The link is invalid or expired."
    return render_template(
        "password_recovery.html", token_verified=True, token=token
    )


@pages.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("pages.login"))


@pages.route("/contacts")
@login_required
def contacts():
    return render_template("contactsP.html")


@pages.route("/archive")
@login_required
def archive():
    return render_template("archive.html")


@pages.route("/gant")
@login_required
def gant():
    return render_template("gant.html")


@pages.route("/admission")
@privilege_required(2)
def admission():
    return render_template("admission.html")


@pages.route("/binyan_coah")
@login_required
def binyan_coah():
    return redirect(url_for("pages.tasks", page_type="binyan_coah", category_id=9))


@pages.route("/tasks", methods=["GET", "POST"])
@login_required
def tasks():
    form = SubmitForm()
    page_type = request.args.get("page_type", "tasks")
    category_id = request.args.get("category_id", "")
    task_to_open = request.args.get("task_to_open", "")

    cat = [{"id": c["id"], "name": c["name"]} for c in data_store.categories]

    return render_template(
        "tasks/tasks.html",
        form=form,
        cat=cat,
        page_type=page_type,
        task_to_open=task_to_open,
        category_id=category_id,
    )


@pages.route("/transfer_page")
@login_required
def transfer_page():
    return render_template("handover_page.html")


@pages.route("/manage_bakarim")
@privilege_required(2)
def manage_bakarim():
    return render_template("manage_bakarim.html")


@pages.route("/hafifa")
@login_required
def hafifa():
    return redirect(url_for("pages.tasks", page_type="hafifa", category_id=19))
