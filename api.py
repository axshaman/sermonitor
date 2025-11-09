"""REST API resources for the SERM Monitoring platform."""
from __future__ import annotations

import datetime as dt
from http import HTTPStatus
from typing import Any, Dict

from flask import request
from flask_restful import Api, Resource
from marshmallow import Schema, ValidationError, fields, validate
from requests.exceptions import HTTPError

from models.models import Users, db
from pdf_loader import generate_pdf_report
from services import (
    add_keywords_to_user,
    delete_user_keywords,
    get_keywords_for_user,
    perform_search,
)

api = Api(prefix="/api")


class UserSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    surname = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    patronymic = fields.Str(load_default=None, validate=validate.Length(max=50))
    date_of_birth = fields.Date(load_default=None)
    telegram_id = fields.Str(required=True, validate=validate.Length(min=1, max=64))
    password = fields.Str(load_default=None, validate=validate.Length(max=255))
    phone = fields.Str(required=True, validate=validate.Length(min=5, max=16))
    phone2 = fields.Str(load_default=None, validate=validate.Length(max=16))
    city = fields.Str(required=True, validate=validate.Length(min=1, max=30))
    city2 = fields.Str(load_default=None, validate=validate.Length(max=30))
    city3 = fields.Str(load_default=None, validate=validate.Length(max=30))
    link = fields.Str(load_default=None, validate=validate.Length(max=200))
    link2 = fields.Str(load_default=None, validate=validate.Length(max=200))
    link3 = fields.Str(load_default=None, validate=validate.Length(max=200))
    link4 = fields.Str(load_default=None, validate=validate.Length(max=200))
    link5 = fields.Str(load_default=None, validate=validate.Length(max=200))


class KeywordSchema(Schema):
    telegram_id = fields.Str(required=True, validate=validate.Length(min=1, max=64))
    keywords = fields.List(
        fields.Str(validate=validate.Length(min=1, max=50)),
        required=True,
        validate=validate.Length(min=1),
    )


class SearchSchema(Schema):
    telegram_id = fields.Str(required=True, validate=validate.Length(min=1, max=64))
    keywords = fields.List(
        fields.Str(validate=validate.Length(min=1, max=50)),
        required=False,
        load_default=list,
    )
    generate_pdf = fields.Bool(load_default=False)


user_schema = UserSchema()
keyword_schema = KeywordSchema()
search_schema = SearchSchema()


class UserRegister(Resource):
    """Register a new user coming from the Telegram bot."""

    def post(self) -> tuple[Dict[str, Any], int]:
        try:
            payload = user_schema.load(request.get_json(force=True))
        except ValidationError as exc:
            return {"status": "validation_error", "errors": exc.messages}, HTTPStatus.BAD_REQUEST

        if Users.find_by_telegram_id(payload["telegram_id"]):
            return {"status": "duplicate", "message": "User already exists."}, HTTPStatus.CONFLICT

        user = Users(**payload)
        user.save()
        return {"status": "ok", "user": user.to_dict()}, HTTPStatus.CREATED


class CheckUser(Resource):
    """Check whether a user exists."""

    def post(self):
        telegram_id = request.get_json(force=True).get("telegram_id")
        if not telegram_id:
            return {"status": "validation_error", "message": "telegram_id is required"}, HTTPStatus.BAD_REQUEST

        user = Users.find_by_telegram_id(telegram_id)
        if user:
            return {"user": "authorized", "details": user.to_dict()}, HTTPStatus.OK
        return {"user": "unauthorized"}, HTTPStatus.NOT_FOUND


class CheckKeyWords(Resource):
    """Manage keywords associated with a user."""

    def post(self):
        try:
            payload = keyword_schema.load(request.get_json(force=True))
        except ValidationError as exc:
            return {"status": "validation_error", "errors": exc.messages}, HTTPStatus.BAD_REQUEST

        user = Users.find_by_telegram_id(payload["telegram_id"])
        if not user:
            return {"status": "user_not_found"}, HTTPStatus.NOT_FOUND

        added = add_keywords_to_user(user, payload["keywords"])
        return {
            "status": "ok",
            "keywords": [kw.to_dict() for kw in added],
        }, HTTPStatus.CREATED

    def get(self):
        try:
            payload = search_schema.load(request.get_json(force=True))
        except ValidationError as exc:
            return {"status": "validation_error", "errors": exc.messages}, HTTPStatus.BAD_REQUEST

        user = Users.find_by_telegram_id(payload["telegram_id"])
        if not user:
            return {"status": "user_not_found"}, HTTPStatus.NOT_FOUND

        keywords = get_keywords_for_user(user)
        return {"keywords": keywords}, HTTPStatus.OK

    def delete(self):
        try:
            payload = keyword_schema.load(request.get_json(force=True))
        except ValidationError as exc:
            return {"status": "validation_error", "errors": exc.messages}, HTTPStatus.BAD_REQUEST

        user = Users.find_by_telegram_id(payload["telegram_id"])
        if not user:
            return {"status": "user_not_found"}, HTTPStatus.NOT_FOUND

        removed = delete_user_keywords(user, payload["keywords"])
        return {"status": "ok", "removed": removed}, HTTPStatus.OK


class Search(Resource):
    """Perform a monitoring search and optionally generate a PDF report."""

    def post(self):
        try:
            payload = search_schema.load(request.get_json(force=True))
        except ValidationError as exc:
            return {"status": "validation_error", "errors": exc.messages}, HTTPStatus.BAD_REQUEST

        user = Users.find_by_telegram_id(payload["telegram_id"])
        if not user:
            return {"status": "user_not_found"}, HTTPStatus.NOT_FOUND

        keywords = payload["keywords"] or get_keywords_for_user(user)
        if not keywords:
            return {"status": "no_keywords", "message": "No keywords available"}, HTTPStatus.BAD_REQUEST

        query = " ".join(filter(None, [user.name, user.surname, user.patronymic or ""]))
        try:
            results = perform_search(query, keywords)
        except HTTPError as exc:
            return {
                "status": "search_error",
                "message": str(exc),
            }, HTTPStatus.BAD_GATEWAY

        if payload["generate_pdf"]:
            filename = generate_pdf_report(user, results)
        else:
            filename = None

        response = {
            "status": "ok",
            "results": results,
            "generated_at": dt.datetime.utcnow().isoformat() + "Z",
        }
        if filename:
            response["pdf_report"] = filename
        return response, HTTPStatus.OK


class Result(Resource):
    """Return keywords that were used for previous searches."""

    def get(self):
        payload = request.get_json(force=True) or {}
        telegram_id = payload.get("telegram_id")
        if not telegram_id:
            return {"status": "validation_error", "message": "telegram_id is required"}, HTTPStatus.BAD_REQUEST

        user = Users.find_by_telegram_id(telegram_id)
        if not user:
            return {"status": "user_not_found"}, HTTPStatus.NOT_FOUND

        return {"keywords": get_keywords_for_user(user)}, HTTPStatus.OK


class UserData(Resource):
    """Return the profile data for a user."""

    def get(self):
        payload = request.get_json(force=True) or {}
        telegram_id = payload.get("telegram_id")
        if not telegram_id:
            return {"status": "validation_error", "message": "telegram_id is required"}, HTTPStatus.BAD_REQUEST

        user = Users.find_by_telegram_id(telegram_id)
        if not user:
            return {"status": "user_not_found"}, HTTPStatus.NOT_FOUND

        return {"user": user.to_dict()}, HTTPStatus.OK


class UserDelete(Resource):
    """Remove a user and detach associated keywords."""

    def delete(self):
        payload = request.get_json(force=True) or {}
        telegram_id = payload.get("telegram_id")
        if not telegram_id:
            return {"status": "validation_error", "message": "telegram_id is required"}, HTTPStatus.BAD_REQUEST

        user = Users.find_by_telegram_id(telegram_id)
        if not user:
            return {"status": "user_not_found"}, HTTPStatus.NOT_FOUND

        db.session.delete(user)
        db.session.commit()
        return {"status": "ok"}, HTTPStatus.OK


def register_resources(app):
    api.add_resource(UserRegister, "/register")
    api.add_resource(CheckUser, "/check-user")
    api.add_resource(CheckKeyWords, "/check-keywords")
    api.add_resource(Search, "/search")
    api.add_resource(Result, "/result")
    api.add_resource(UserData, "/user-data")
    api.add_resource(UserDelete, "/user")
    api.init_app(app)
