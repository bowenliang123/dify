# -*- coding:utf-8 -*-
from datetime import datetime

import pytz
from flask import current_app, request
from flask_login import login_required, current_user
from flask_restful import Resource, reqparse, fields, marshal_with, inputs

from controllers.console import api
from controllers.console.setup import setup_required
from controllers.console.workspace.error import AccountAlreadyInitedError, InvalidInvitationCodeError, \
    RepeatPasswordNotMatchError
from controllers.console.wraps import account_initialization_required
from libs.helper import TimestampField, supported_language, timezone
from extensions.ext_database import db
from models.account import InvitationCode, AccountIntegrate, Account
from services.account_service import AccountService,RegisterService


account_fields = {
    'id': fields.String,
    'name': fields.String,
    'avatar': fields.String,
    'email': fields.String,
    'interface_language': fields.String,
    'interface_theme': fields.String,
    'timezone': fields.String,
    'last_login_at': TimestampField,
    'last_login_ip': fields.String,
    'created_at': TimestampField
}


class AccountInitApi(Resource):

    @setup_required
    @login_required
    def post(self):
        account = current_user

        if account.status == 'active':
            raise AccountAlreadyInitedError()

        parser = reqparse.RequestParser()

        if current_app.config['EDITION'] == 'CLOUD':
            parser.add_argument('invitation_code', type=str, location='json')

        parser.add_argument(
            'interface_language', type=supported_language, required=True, location='json')
        parser.add_argument('timezone', type=timezone,
                            required=True, location='json')
        args = parser.parse_args()

        if current_app.config['EDITION'] == 'CLOUD':
            if not args['invitation_code']:
                raise ValueError('invitation_code is required')

            # check invitation code
            invitation_code = db.session.query(InvitationCode).filter(
                InvitationCode.code == args['invitation_code'],
                InvitationCode.status == 'unused',
            ).first()

            if not invitation_code:
                raise InvalidInvitationCodeError()

            invitation_code.status = 'used'
            invitation_code.used_at = datetime.utcnow()
            invitation_code.used_by_tenant_id = account.current_tenant_id
            invitation_code.used_by_account_id = account.id

        account.interface_language = args['interface_language']
        account.timezone = args['timezone']
        account.interface_theme = 'light'
        account.status = 'active'
        account.initialized_at = datetime.utcnow()
        db.session.commit()

        return {'result': 'success'}


class AccountProfileApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    @marshal_with(account_fields)
    def get(self):
        return current_user


class AccountNameApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    @marshal_with(account_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, location='json')
        args = parser.parse_args()

        # Validate account name length
        if len(args['name']) < 3 or len(args['name']) > 30:
            raise ValueError(
                "Account name must be between 3 and 30 characters.")

        updated_account = AccountService.update_account(current_user, name=args['name'])

        return updated_account


class AccountAvatarApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    @marshal_with(account_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('avatar', type=str, required=True, location='json')
        args = parser.parse_args()

        updated_account = AccountService.update_account(current_user, avatar=args['avatar'])

        return updated_account


class AccountInterfaceLanguageApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    @marshal_with(account_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            'interface_language', type=supported_language, required=True, location='json')
        args = parser.parse_args()

        updated_account = AccountService.update_account(current_user, interface_language=args['interface_language'])

        return updated_account


class AccountInterfaceThemeApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    @marshal_with(account_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('interface_theme', type=str, choices=[
            'light', 'dark'], required=True, location='json')
        args = parser.parse_args()

        updated_account = AccountService.update_account(current_user, interface_theme=args['interface_theme'])

        return updated_account


class AccountTimezoneApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    @marshal_with(account_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('timezone', type=str,
                            required=True, location='json')
        args = parser.parse_args()

        # Validate timezone string, e.g. America/New_York, Asia/Shanghai
        if args['timezone'] not in pytz.all_timezones:
            raise ValueError("Invalid timezone string.")

        updated_account = AccountService.update_account(current_user, timezone=args['timezone'])

        return updated_account

class AccountListApi(Resource):

    app_pagination_fields = {
        'page': fields.Integer,
        'limit': fields.Integer(attribute='per_page'),
        'total': fields.Integer,
        'has_more': fields.Boolean(attribute='has_next'),
        'data': fields.List(fields.Nested(account_fields), attribute='items')
        }

    @marshal_with(app_pagination_fields)
    def get(self):
        
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=inputs.int_range(1, 99999), required=False, default=1, location='args')
        parser.add_argument('limit', type=inputs.int_range(1, 100), required=False, default=20, location='args')
        args = parser.parse_args()

        app_models = db.paginate(
            db.select(Account),
            page=args['page'],
            per_page=args['limit'],
            error_out=False)

        return app_models
        # return db.session.query(Account).all()

class AccountAddApi(Resource):

    # @marshal_with(account_fields)
    def post(self):
        
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, location='json')
        parser.add_argument('email', type=str, required=True, location='json')
        parser.add_argument('password', type=str, required=True, location='json')

        args = parser.parse_args()

        if AccountService.has_account(email=args['email']):
            return {"result": "failed", "message": "Email already exists."}
        
        else: 
            RegisterService.register(
            email=args['email'],
            name=args['name'],
            password=args['password'])
            return {"result": "success"}

class AccountPasswordApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    @marshal_with(account_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('password', type=str,
                            required=False, location='json')
        parser.add_argument('new_password', type=str,
                            required=True, location='json')
        parser.add_argument('repeat_new_password', type=str,
                            required=True, location='json')
        args = parser.parse_args()

        if args['new_password'] != args['repeat_new_password']:
            raise RepeatPasswordNotMatchError()

        AccountService.update_account_password(
            current_user, args['password'], args['new_password'])

        return {"result": "success"}


class AccountIntegrateApi(Resource):
    integrate_fields = {
        'provider': fields.String,
        'created_at': TimestampField,
        'is_bound': fields.Boolean,
        'link': fields.String
    }

    integrate_list_fields = {
        'data': fields.List(fields.Nested(integrate_fields)),
    }

    @setup_required
    @login_required
    @account_initialization_required
    @marshal_with(integrate_list_fields)
    def get(self):
        account = current_user

        account_integrates = db.session.query(AccountIntegrate).filter(
            AccountIntegrate.account_id == account.id).all()

        base_url = request.url_root.rstrip('/')
        oauth_base_path = "/console/api/oauth/login"
        providers = ["github", "google"]

        integrate_data = []
        for provider in providers:
            existing_integrate = next((ai for ai in account_integrates if ai.provider == provider), None)
            if existing_integrate:
                integrate_data.append({
                    'id': existing_integrate.id,
                    'provider': provider,
                    'created_at': existing_integrate.created_at,
                    'is_bound': True,
                    'link': None
                })
            else:
                integrate_data.append({
                    'id': None,
                    'provider': provider,
                    'created_at': None,
                    'is_bound': False,
                    'link': f'{base_url}{oauth_base_path}/{provider}'
                })

        return {'data': integrate_data}


# Register API resources
api.add_resource(AccountInitApi, '/account/init')
api.add_resource(AccountProfileApi, '/account/profile')
api.add_resource(AccountNameApi, '/account/name')
api.add_resource(AccountAvatarApi, '/account/avatar')
api.add_resource(AccountInterfaceLanguageApi, '/account/interface-language')
api.add_resource(AccountInterfaceThemeApi, '/account/interface-theme')
api.add_resource(AccountTimezoneApi, '/account/timezone')
api.add_resource(AccountPasswordApi, '/account/password')
api.add_resource(AccountIntegrateApi, '/account/integrates')
api.add_resource(AccountAddApi, '/account/add')
api.add_resource(AccountListApi, '/account/list')
# api.add_resource(AccountEmailApi, '/account/email')
# api.add_resource(AccountEmailVerifyApi, '/account/email-verify')
