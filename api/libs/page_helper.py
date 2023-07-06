# -*- coding:utf-8 -*-
from flask_restful import fields

from extensions.ext_database import db

def page_data(data_fields):
    return {
        'page': fields.Integer,
        'limit': fields.Integer(attribute='per_page'),
        'total': fields.Integer,
        'has_more': fields.Boolean(attribute='has_next'),
        'data': fields.List(fields.Nested(data_fields), attribute='items')
     }

def page_data_with_args(model, page_no, limit):
    return db.paginate(
            db.select(model),
            page=page_no,
            per_page=limit,
            error_out=False)