from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "ketoan.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app import models  # noqa
    Base.metadata.create_all(bind=engine)
    _seed_admin()
    _seed_chart_of_accounts()


def _seed_admin():
    from app.models import User
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == "admin").first():
            from app.auth import hash_password
            db.add(User(
                username="admin",
                full_name="Quản trị viên",
                hashed_password=hash_password("kbc2026"),
                role="ke_toan_truong",
            ))
            db.commit()
    finally:
        db.close()


def _seed_chart_of_accounts():
    from app.models import Account
    from app.coa_tt133 import TT133_ACCOUNTS
    db = SessionLocal()
    try:
        if db.query(Account).count() == 0:
            for code, name, parent, kind in TT133_ACCOUNTS:
                db.add(Account(code=code, name=name, parent_code=parent, kind=kind))
            db.commit()
    finally:
        db.close()
