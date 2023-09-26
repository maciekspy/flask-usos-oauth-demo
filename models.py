

import datetime
from typing import List
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, ForeignKey, Column, text, select, func
from sqlalchemy import Integer, String, Text, Boolean, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    usos_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=True, default=None)
    first_name: Mapped[str] = mapped_column(String(64), nullable=False)
    last_name: Mapped[str] = mapped_column(String(64), nullable=False)
    email: Mapped[str] = mapped_column(String(64), nullable=False)
    student_number: Mapped[str] = mapped_column(String(10), nullable=True)
    
    @property
    def display_name(self):
        return f"{self.first_name} {self.last_name}"