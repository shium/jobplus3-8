# -*- coding: utf-8 -*-

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import url_for
from flask_login import UserMixin

from jieba.analyse import ChineseAnalyzer
import flask_whooshalchemyplus as whoosh


db = SQLAlchemy()

jobhunter_job = db.Table(
    'jobhunter_job',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('job_id', db.Integer, db.ForeignKey('job.id', ondelete='CASCADE'))
)


class Base(db.Model):
    __abstract__ = True

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime,
                        default=datetime.utcnow,
                        onupdate=datetime.utcnow)


class User(Base, UserMixin):
    __tablename__ = 'user'

    ROLE_JOBHUNTER = 10
    ROLE_COMPANY = 20
    ROLE_ADMIN = 30

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, index=True, nullable=True)
    _password = db.Column('password', db.String(128), nullable=False)
    phone = db.Column(db.String(18), unique=True, index=True, nullable=True)
    is_enable = db.Column(db.Boolean, default=True)
    job_years = db.Column(db.String(2), nullable=True)
    email = db.Column(db.String(64), unique=True, index=True, nullable=False)
    role = db.Column(db.SmallInteger, default=ROLE_JOBHUNTER)
    job_intention = db.relationship('Job',
                                secondary=jobhunter_job,
                                backref='users')
    detail = db.relationship("Company", uselist=False)
    # 该处是否可以使用外键
    company_id = db.Column(db.Integer)
    # 暂时先用简历地址代替简历存储
    # resume_url = db.Column(db.String(64))

    def __repr__(self):
        return '<User: {}>'.format(self.username)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, orig_password):
        self._password = generate_password_hash(orig_password)

    def check_password(self, password):
        return check_password_hash(self._password, password)

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    @property
    def is_company(self):
        return self.role == self.ROLE_COMPANY

    @property
    def is_jobhunter(self):
        return self.role == self.ROLE_JOBHUNTER


class Company(Base):
    __tablename__ = 'company'
    __searchable__ = ['name', 'address']
    __analyzer__ = ChineseAnalyzer()

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True, nullable=False)
    _password = db.Column('password', db.String(128), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"))
    user = db.relationship("User", uselist=False, backref=db.backref("company_detail", uselist=False))
    website = db.Column(db.String(64), nullable=True)
    address = db.Column(db.String(64), nullable=True)
    logo = db.Column(db.String(64))
    summary = db.Column(db.String(128))
    description = db.Column(db.String(1024))
    company_info = db.Column(db.Text)

    def __repr__(self):
        return '<Company: {}'.format(self.name)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, orig_password):
        self._password = generate_password_hash(orig_password)

    def check_password(self, password):
        return check_password_hash(self._password, password)


class Job(Base):
    __tablename__ = 'job'
    __searchable__ = ['name', 'salary']
    __analyzer__ = ChineseAnalyzer()

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    salary = db.Column(db.String(64), nullable=False)
    address = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text)
    requirement = db.Column(db.String(128))
    # 经验要求
    exp = db.Column(db.String(64), default="经验不限", nullable=False)
    # 学历要求
    degree = db.Column(db.String(64), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id', ondelete='CASCADE'))
    company = db.relationship('Company', uselist=False, backref='jobs')

    def __repr__(self):
        return '<Job: {}'.format(self.name)

    @property
    def url(self):
        return url_for('job.detail', course_id = self.id)
