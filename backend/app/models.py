from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, default="")
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="ke_toan_vien")  # ke_toan_truong | ke_toan_vien | giam_doc
    created_at = Column(DateTime, default=datetime.utcnow)


class Account(Base):
    """Tài khoản trong hệ thống tài khoản TT133"""
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    parent_code = Column(String, nullable=True)
    kind = Column(String, default="DC")  # D | C | DC | X
    is_active = Column(Integer, default=1)


class OpeningBalance(Base):
    """Số dư đầu kỳ của tài khoản (01/01/2026)"""
    __tablename__ = "opening_balances"
    id = Column(Integer, primary_key=True, index=True)
    account_code = Column(String, index=True, nullable=False)
    fiscal_year = Column(Integer, default=2026)
    debit = Column(Float, default=0.0)   # dư Nợ đầu kỳ
    credit = Column(Float, default=0.0)  # dư Có đầu kỳ
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Partner(Base):
    """Khách hàng / Nhà cung cấp"""
    __tablename__ = "partners"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    tax_code = Column(String, default="")
    address = Column(String, default="")
    phone = Column(String, default="")
    type = Column(String, default="customer")  # customer | supplier | both


class Product(Base):
    """Hàng hóa (cao sâm KBC)"""
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    unit = Column(String, default="hộp")
    price = Column(Float, default=0.0)        # giá bán (SRP, đã gồm VAT)
    cost_price = Column(Float, default=0.0)   # giá vốn
    vat_rate = Column(Float, default=8.0)
    stock_qty = Column(Float, default=0.0)


class Voucher(Base):
    """Chứng từ kế toán (phiếu thu/chi, hóa đơn bán/mua, nhập/xuất kho)"""
    __tablename__ = "vouchers"
    id = Column(Integer, primary_key=True, index=True)
    voucher_no = Column(String, index=True, nullable=False)   # PT-001, PC-001, HD-001...
    voucher_type = Column(String, nullable=False)
    # voucher_type: thu | chi | ban_hang | mua_hang | nhap_kho | xuat_kho | khac
    voucher_date = Column(Date, nullable=False)
    description = Column(Text, default="")
    partner_id = Column(Integer, ForeignKey("partners.id"), nullable=True)
    partner_name = Column(String, default="")
    total_amount = Column(Float, default=0.0)
    vat_amount = Column(Float, default=0.0)
    status = Column(String, default="posted")  # draft | posted | cancelled
    created_by = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    entries = relationship("JournalEntry", back_populates="voucher",
                           cascade="all, delete-orphan")


class JournalEntry(Base):
    """Bút toán định khoản Nợ/Có (1 dòng = 1 vế của định khoản)"""
    __tablename__ = "journal_entries"
    id = Column(Integer, primary_key=True, index=True)
    voucher_id = Column(Integer, ForeignKey("vouchers.id"), nullable=False)
    entry_date = Column(Date, nullable=False, index=True)
    debit_account = Column(String, index=True, nullable=False)   # TK Nợ
    credit_account = Column(String, index=True, nullable=False)  # TK Có
    amount = Column(Float, nullable=False)
    description = Column(Text, default="")

    voucher = relationship("Voucher", back_populates="entries")
