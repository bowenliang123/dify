# -*- coding:utf-8 -*-
import logging

from flask import request
from flask_login import login_required, current_user
from flask_restful import Resource, fields, marshal_with, reqparse, marshal, inputs

from controllers.console import api
from controllers.console.setup import setup_required
from controllers.console.error import AccountNotLinkTenantError
from controllers.console.wraps import account_initialization_required
from libs.helper import TimestampField
from libs.page_helper import page_data, page_data_with_args
from extensions.ext_database import db
from models.account import Tenant
from services.account_service import TenantService, AccountService
from services.workspace_service import WorkspaceService
from models.account import Account


provider_fields = {
    'provider_name': fields.String,
    'provider_type': fields.String,
    'is_valid': fields.Boolean,
    'token_is_set': fields.Boolean,
}

tenant_fields = {
    'id': fields.String,
    'name': fields.String,
    'plan': fields.String,
    'status': fields.String,
    'created_at': TimestampField,
    'role': fields.String,
    'providers': fields.List(fields.Nested(provider_fields)),
    'in_trail': fields.Boolean,
    'trial_end_reason': fields.String,
}

tenants_fields = {
    'id': fields.String,
    'name': fields.String,
    'plan': fields.String,
    'status': fields.String,
    'created_at': TimestampField,
    'current': fields.Boolean
}


class TenantListApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    def get(self):
        tenants = TenantService.get_join_tenants(current_user)

        for tenant in tenants:
            if tenant.id == current_user.current_tenant_id:
                tenant.current = True  # Set current=True for current tenant
        return {'workspaces': marshal(tenants, tenants_fields)}, 200


class TenantApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    @marshal_with(tenant_fields)
    def get(self):
        if request.path == '/info':
            logging.warning('Deprecated URL /info was used.')

        tenant = current_user.current_tenant

        return WorkspaceService.get_tenant_info(tenant), 200


class SwitchWorkspaceApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('tenant_id', type=str, required=True, location='json')
        args = parser.parse_args()

        # check if tenant_id is valid, 403 if not
        try:
            TenantService.switch_tenant(current_user, args['tenant_id'])
        except Exception:
            raise AccountNotLinkTenantError("Account not link tenant")

        new_tenant = db.session.query(Tenant).get(args['tenant_id'])  # Get new tenant

        return {'result': 'success', 'new_tenant': marshal(WorkspaceService.get_tenant_info(new_tenant), tenant_fields)}

class TenantListAllApi(Resource):

    app_pagination_fields = page_data(tenant_fields)

    @marshal_with(app_pagination_fields)
    def get(self):

        parser = reqparse.RequestParser()
        parser.add_argument('page', type=inputs.int_range(1, 99999), required=False, default=1, location='args')
        parser.add_argument('limit', type=inputs.int_range(1, 100), required=False, default=20, location='args')
        args = parser.parse_args()

        return page_data_with_args(Tenant, args['page'], args['limit'])

        r#eturn {'workspaces': marshal(tenants, tenants_fields)}, 200

class TenantAddApi(Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, location='json')    
        args = parser.parse_args()
        
        if TenantService.has_tenant(args['name']):
            return {'result': 'failed', 'message': 'You already have a workspace.'}, 400
        else:
            tenant = TenantService.create_tenant(args['name'])
            return {'result': 'success', 'message': 'Workspace created.'}, 200
        
class TenantUserApi(Resource):

    def get(self):
        ''''get all users in the workspace'''
        parser = reqparse.RequestParser()
        parser.add_argument('tenant_id', type=str, required=True, location='args')
        args = parser.parse_args()

        # Tenant(id=args['tenant_id'])
        members = TenantService.get_tenant_members(Tenant(id=args['tenant_id']))
        account_field = Account.get_account_filed()
        account_field['role'] = fields.String
        return {'result': 'success', 'data': marshal(members, account_field)}, 200
    
    def post(self):
        '''add user to workspace'''
        parser = reqparse.RequestParser()
        parser.add_argument('tenant_id', type=str, required=True, location='json')
        parser.add_argument('user_id', type=str, required=True, location='json')
        parser.add_argument('role', type=str, required=False, location='json')
        args = parser.parse_args()

        tenant = TenantService.load_tenant(args['tenant_id'])
        if not tenant:
            return {'result': 'failed', 'message': 'Workspace not found.'}, 400
        
        user = AccountService.load_user(args['user_id'])
        if not user:
            return {'result': 'failed', 'message': 'User not found.'}, 400
        
        role = args['role'] if args['role'] else 'normal'
        tenant_join = TenantService.create_tenant_member(Tenant(id=args['tenant_id']), Account(id=args['user_id']), role)
        if tenant_join:
            return {'result': 'success'}, 200
        else:
            return {'result': 'failed', 'message': 'User already in workspace.'}, 400
        


api.add_resource(TenantListApi, '/workspaces')  # GET for getting all tenants
api.add_resource(TenantApi, '/workspaces/current', endpoint='workspaces_current')  # GET for getting current tenant info
api.add_resource(TenantApi, '/info', endpoint='info')  # Deprecated
api.add_resource(SwitchWorkspaceApi, '/workspaces/switch')  # POST for switching tenant
api.add_resource(TenantListAllApi, '/workspaces/all')
api.add_resource(TenantAddApi, '/workspaces/add')
api.add_resource(TenantUserApi, '/workspaces/users')
