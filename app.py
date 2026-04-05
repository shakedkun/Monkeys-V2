"""
Monkeys V2 – Dummy Backend (Flask)
===================================
Run:  python app.py
"""

from flask import Flask, session

import data_store


def create_app():
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates",
    )
    app.secret_key = "monkeys-dummy-secret-key-2026"
    app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB upload limit
    app.config["WTF_CSRF_ENABLED"] = False  # disable CSRF for dummy backend

    # ── Make session user available to all templates ──
    @app.context_processor
    def inject_user():
        return {"current_user": session.get("user")}

    # ── Make categories & locations available to templates ──
    @app.context_processor
    def inject_data():
        return {
            "categories": data_store.categories,
            "locations": data_store.locations,
        }

    # ── Register blueprints ──────────────────
    from routes.pages import pages
    from routes.auth_api import auth_api
    from routes.task_api import task_api
    from routes.comment_api import comment_api
    from routes.file_api import file_api
    from routes.contact_api import contact_api
    from routes.archive_api import archive_api
    from routes.bakarim_api import bakarim_api
    from routes.handover_api import handover_api

    app.register_blueprint(pages)
    app.register_blueprint(auth_api)
    app.register_blueprint(task_api)
    app.register_blueprint(comment_api)
    app.register_blueprint(file_api)
    app.register_blueprint(contact_api)
    app.register_blueprint(archive_api)
    app.register_blueprint(bakarim_api)
    app.register_blueprint(handover_api)

    return app


if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    app = create_app()
    print()
    print("  Monkeys V2 (Dummy Backend - Flask) running at http://localhost:5000")
    print()
    print("   Test accounts:")
    print("     admin / admin123   (privilege 2 - admin)")
    print("     user1 / pass123    (privilege 1 - standard)")
    print("     pending_user / pass456  (privilege 0 - pending)")
    print()
    app.run(debug=True, host="0.0.0.0", port=5000)
