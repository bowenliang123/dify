import logging
from datetime import datetime
from typing import Optional

import flask_login
import requests
from flask import request, redirect, current_app, session
from flask_restful import Resource

from libs.oauth import OAuthUserInfo, GitHubOAuth, GoogleOAuth, GFOauth
from extensions.ext_database import db
from models.account import Account, AccountStatus
from services.account_service import AccountService, RegisterService
from .. import api


def get_oauth_providers():
    with current_app.app_context():
        github_oauth = GitHubOAuth(client_id=current_app.config.get('GITHUB_CLIENT_ID'),
                                   client_secret=current_app.config.get(
                                       'GITHUB_CLIENT_SECRET'),
                                   redirect_uri=current_app.config.get(
                                       'CONSOLE_URL') + '/console/api/oauth/authorize/github')

        google_oauth = GoogleOAuth(client_id=current_app.config.get('GOOGLE_CLIENT_ID'),
                                   client_secret=current_app.config.get(
                                       'GOOGLE_CLIENT_SECRET'),
                                   redirect_uri=current_app.config.get(
                                       'CONSOLE_URL') + '/console/api/oauth/authorize/google')

        gf_oauth = GFOauth(client_id=current_app.config.get('GF_CLIENT_ID'),
                           client_secret=current_app.config.get(
                               'GF_CLIENT_SECRET'),
                           redirect_uri=current_app.config.get(
                               'GF_REDIRECT_URL'),
                           conf=current_app.config
                           )

        OAUTH_PROVIDERS = {
            'github': github_oauth,
            'google': google_oauth,
            'gf': gf_oauth
        }
        return OAUTH_PROVIDERS


class OAuthLogin(Resource):
    def get(self, provider: str):
        OAUTH_PROVIDERS = get_oauth_providers()
        with current_app.app_context():
            oauth_provider = OAUTH_PROVIDERS.get(provider)
            print(vars(oauth_provider))
        if not oauth_provider:
            return {'error': 'Invalid provider'}, 400

        auth_url = oauth_provider.get_authorization_url()
        return redirect(auth_url)


class OAuthCallback(Resource):
    def get(self, provider: str):
        OAUTH_PROVIDERS = get_oauth_providers()
        with current_app.app_context():
            oauth_provider = OAUTH_PROVIDERS.get(provider)
        if not oauth_provider:
            return {'error': 'Invalid provider'}, 400

        code = request.args.get('code')
        try:
            token = oauth_provider.get_access_token(code)
            user_info = oauth_provider.get_user_info(token)
        except requests.exceptions.HTTPError as e:
            logging.exception(
                f"An error occurred during the OAuth process with {provider}: {e.response.text}")
            return {'error': 'OAuth process failed'}, 400

        with current_app.app_context():
            default_workspace = current_app.config.get('DEFAULT_WORKSPACE')

        account = _generate_account(provider, user_info, default_workspace)
        #
        # if account.status == AccountStatus.PENDING.value:
        #     account.status = AccountStatus.ACTIVE.value
        #     account.initialized_at = datetime.utcnow()
        #     db.session.commit()

        # login user
        # session.clear()
        flask_login.login_user(account, remember=True)
        logging.info('access_token: %s', token)
        session["access_token"] = token
        for k in session.keys():
            logging.info('session key: ' + k)
        logging.info('access_token from get: ' + session.get('access_token'))
        AccountService.update_last_login(account, request)

        return redirect(f'{current_app.config.get("APP_URL")}')


def _get_account_by_openid_or_email(provider: str, user_info: OAuthUserInfo) -> Optional[Account]:
    account = Account.get_by_openid(provider, user_info.id)

    if not account:
        account = Account.query.filter_by(email=user_info.email).first()

    return account


def _generate_account(provider: str, user_info: OAuthUserInfo, default_workspace: str):
    # Get account by openid or email.
    account = _get_account_by_openid_or_email(provider, user_info)

    if not account:
        # Create account
        account_name = user_info.name if user_info.name else 'GfGpt'
        account = RegisterService.register(
            email=user_info.email,
            name=account_name,
            password=None,
            open_id=user_info.id,
            provider=provider,
            tenant_id=default_workspace
        )

        # Set interface language
        preferred_lang = request.accept_languages.best_match(['zh', 'en'])
        if preferred_lang == 'zh':
            interface_language = 'zh-Hans'
        else:
            interface_language = 'en-US'
        account.interface_language = interface_language
        db.session.commit()
        # Link account
        AccountService.link_account_integrate(provider, user_info.id, account)

    return account


api.add_resource(OAuthLogin, '/oauth/login/<provider>')
api.add_resource(OAuthCallback, '/oauth/authorize/<provider>')
