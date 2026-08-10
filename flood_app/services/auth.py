from functools import wraps

from flask import g, jsonify, redirect, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from ..db import db
from ..models import USER_ROLES, User


class AuthService:
    def create_user(self, full_name: str, email: str, password: str, role: str = "citizen"):
        if role not in USER_ROLES:
            raise ValueError(f"Invalid role: {role}. Must be one of {USER_ROLES}")

        existing = User.query.filter_by(email=email).first()
        if existing is not None:
            raise ValueError("An account with this email already exists.")

        user = User(
            full_name=full_name,
            email=email,
            password_hash=generate_password_hash(password),
            role=role,
            is_active=True,
        )
        db.session.add(user)
        db.session.commit()
        return user

    def authenticate(self, email: str, password: str):
        user = User.query.filter_by(email=email).first()
        if user is None or not check_password_hash(user.password_hash, password):
            raise ValueError("Invalid email or password.")
        if not user.is_active:
            raise ValueError("This account is inactive.")
        return user

    def login_user(self, user):
        session["user_id"] = user.id
        session["user_role"] = user.role
        session["user_email"] = user.email

    def logout_user(self):
        session.pop("user_id", None)
        session.pop("user_role", None)
        session.pop("user_email", None)

    def get_current_user(self):
        user_id = session.get("user_id")
        if not user_id:
            return None
        return db.session.get(User, user_id)


def load_current_user():
    if db is None or User is None:
        g.current_user = None
        return
    g.current_user = AuthService().get_current_user()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if getattr(g, "current_user", None) is None:
            if request.blueprint == "api_auth" or request.path.startswith("/api/"):
                return jsonify({"error": "authentication required"}), 401
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


def roles_required(*allowed_roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            user = getattr(g, "current_user", None)
            if user is None:
                if request.blueprint == "api_auth" or request.path.startswith("/api/"):
                    return jsonify({"error": "authentication required"}), 401
                return redirect(url_for("auth.login", next=request.path))
            if user.role not in allowed_roles:
                if request.blueprint == "api_auth" or request.path.startswith("/api/"):
                    return jsonify({"error": "forbidden"}), 403
                return redirect(url_for("web.home"))
            return view(*args, **kwargs)

        return wrapped

    return decorator


def register_auth_handlers(app):
    @app.before_request
    def _load_user():
        load_current_user()

    @app.context_processor
    def inject_auth_context():
        return {"current_user": getattr(g, "current_user", None), "user_roles": USER_ROLES}
