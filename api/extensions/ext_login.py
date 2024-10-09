import json

import flask_login
from flask import Response, request
from werkzeug.exceptions import Unauthorized

import contexts
from libs.passport import PassportService
from services.account_service import AccountService


def init_app(app):
    login_manager = flask_login.LoginManager()
    login_manager.init_app(app)

    # Flask-Login configuration
    @login_manager.request_loader
    def load_user_from_request(request_from_flask_login):
        """Load user based on the request."""
        if request.blueprint not in {"console", "inner_api"}:
            return None
        # Check if the user_id contains a dot, indicating the old format
        auth_header = request.headers.get("Authorization", "")
        if not auth_header:
            auth_token = request.args.get("_token")
            if not auth_token:
                raise Unauthorized("Invalid Authorization token.")
        else:
            if " " not in auth_header:
                raise Unauthorized("Invalid Authorization header format. Expected 'Bearer <api-key>' format.")
            auth_scheme, auth_token = auth_header.split(None, 1)
            auth_scheme = auth_scheme.lower()
            if auth_scheme != "bearer":
                raise Unauthorized("Invalid Authorization header format. Expected 'Bearer <api-key>' format.")

        decoded = PassportService().verify(auth_token)
        user_id = decoded.get("user_id")

        logged_in_account = AccountService.load_logged_in_account(account_id=user_id, token=auth_token)
        if logged_in_account:
            contexts.tenant_id.set(logged_in_account.current_tenant_id)
        return logged_in_account

    @login_manager.unauthorized_handler
    def unauthorized_handler():
        """Handle unauthorized requests."""
        return Response(
            json.dumps({"code": "unauthorized", "message": "Unauthorized."}),
            status=401,
            content_type="application/json",
        )
