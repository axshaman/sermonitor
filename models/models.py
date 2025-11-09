"""Database models for the SERM Monitoring platform."""
from __future__ import annotations

import datetime as dt
from typing import Dict, Iterable, List

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

subs = db.Table(
    "subs",
    db.Column("users_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("words_id", db.Integer, db.ForeignKey("keywords.id"), primary_key=True),
)


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow
    )


class Users(db.Model, TimestampMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    patronymic = db.Column(db.String(50), nullable=True)
    date_of_birth = db.Column(db.Date(), nullable=True)
    telegram_id = db.Column(db.String(64), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(16), unique=True, nullable=False)
    phone2 = db.Column(db.String(16), nullable=True, unique=True)
    city = db.Column(db.String(30), nullable=False)
    city2 = db.Column(db.String(30), nullable=True)
    city3 = db.Column(db.String(30), nullable=True)
    link = db.Column(db.String(200), nullable=True)
    link2 = db.Column(db.String(200), nullable=True)
    link3 = db.Column(db.String(200), nullable=True)
    link4 = db.Column(db.String(200), nullable=True)
    link5 = db.Column(db.String(200), nullable=True)

    keywords = db.relationship(
        "KeyWords", secondary=subs, back_populates="users", lazy="selectin"
    )

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_telegram_id(cls, telegram_id: str) -> "Users | None":
        return cls.query.filter_by(telegram_id=str(telegram_id)).first()

    def to_dict(self) -> Dict[str, str]:
        return {
            "id": self.id,
            "name": self.name,
            "surname": self.surname,
            "patronymic": self.patronymic,
            "telegram_id": self.telegram_id,
            "phone": self.phone,
            "city": self.city,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class KeyWords(db.Model, TimestampMixin):
    __tablename__ = "keywords"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    users = db.relationship(
        "Users", secondary=subs, back_populates="keywords", lazy="selectin"
    )

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_word_by_name(cls, name: str) -> "KeyWords | None":
        return cls.query.filter(db.func.lower(cls.name) == name.lower()).first()

    def to_dict(self) -> Dict[str, str]:
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
