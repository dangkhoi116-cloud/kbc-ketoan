from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.auth import get_current_user
from app.models import JournalEntry, Account, OpeningBalance
from datetime import date
from typing import Optional

router = APIRouter()


@router.get("/journal")
def get_journal(
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    account_code: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Sổ nhật ký chung"""
    query = db.query(JournalEntry).order_by(JournalEntry.entry_date, JournalEntry.id)
    
    if from_date:
        query = query.filter(JournalEntry.entry_date >= from_date)
    if to_date:
        query = query.filter(JournalEntry.entry_date <= to_date)
    if account_code:
        query = query.filter(
            (JournalEntry.debit_account == account_code) |
            (JournalEntry.credit_account == account_code)
        )
    
    entries = query.limit(limit).all()
    total = query.count()
    
    # Tính tổng Nợ/Có
    total_debit = sum(e.amount for e in entries)
    total_credit = total_debit  # luôn cân bằng
    
    return {
        "entries": entries,
        "total": total,
        "summary": {
            "total_debit": total_debit,
            "total_credit": total_credit
        }
    }


@router.get("/ledger/{account_code}")
def get_ledger(
    account_code: str,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    fiscal_year: int = 2026,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Sổ cái của 1 tài khoản"""
    
    # Lấy thông tin tài khoản
    account = db.query(Account).filter(Account.code == account_code).first()
    if not account:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản")
    
    # Số dư đầu kỳ
    opening = db.query(OpeningBalance).filter(
        OpeningBalance.account_code == account_code,
        OpeningBalance.fiscal_year == fiscal_year
    ).first()
    
    opening_debit = opening.debit if opening else 0.0
    opening_credit = opening.credit if opening else 0.0
    
    # Lấy các bút toán phát sinh
    query = db.query(JournalEntry).filter(
        (JournalEntry.debit_account == account_code) |
        (JournalEntry.credit_account == account_code)
    ).order_by(JournalEntry.entry_date, JournalEntry.id)
    
    if from_date:
        query = query.filter(JournalEntry.entry_date >= from_date)
    if to_date:
        query = query.filter(JournalEntry.entry_date <= to_date)
    
    entries = query.all()
    
    # Tính số dư lũy kế
    running_debit = opening_debit
    running_credit = opening_credit
    
    ledger_lines = []
    for entry in entries:
        if entry.debit_account == account_code:
            running_debit += entry.amount
            ledger_lines.append({
                "date": entry.entry_date,
                "description": entry.description,
                "debit": entry.amount,
                "credit": 0.0,
                "contra_account": entry.credit_account,
                "running_debit": running_debit,
                "running_credit": running_credit
            })
        else:  # credit_account == account_code
            running_credit += entry.amount
            ledger_lines.append({
                "date": entry.entry_date,
                "description": entry.description,
                "debit": 0.0,
                "credit": entry.amount,
                "contra_account": entry.debit_account,
                "running_debit": running_debit,
                "running_credit": running_credit
            })
    
    # Số dư cuối kỳ
    closing_debit = running_debit
    closing_credit = running_credit
    
    return {
        "account": {
            "code": account.code,
            "name": account.name,
            "kind": account.kind
        },
        "opening_balance": {
            "debit": opening_debit,
            "credit": opening_credit
        },
        "entries": ledger_lines,
        "closing_balance": {
            "debit": closing_debit,
            "credit": closing_credit,
            "net": closing_debit - closing_credit  # dư Nợ (+) hoặc dư Có (-)
        }
    }


@router.get("/trial-balance")
def get_trial_balance(
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    fiscal_year: int = 2026,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Bảng cân đối số phát sinh"""
    
    # Lấy tất cả tài khoản
    accounts = db.query(Account).filter(Account.is_active == 1).order_by(Account.code).all()
    
    result = []
    
    for account in accounts:
        # Số dư đầu kỳ
        opening = db.query(OpeningBalance).filter(
            OpeningBalance.account_code == account.code,
            OpeningBalance.fiscal_year == fiscal_year
        ).first()
        
        opening_debit = opening.debit if opening else 0.0
        opening_credit = opening.credit if opening else 0.0
        
        # Số phát sinh trong kỳ
        query = db.query(
            func.sum(JournalEntry.amount).label("amount")
        ).filter(JournalEntry.debit_account == account.code)
        
        if from_date:
            query = query.filter(JournalEntry.entry_date >= from_date)
        if to_date:
            query = query.filter(JournalEntry.entry_date <= to_date)
        
        debit_arise = query.scalar() or 0.0
        
        query = db.query(
            func.sum(JournalEntry.amount).label("amount")
        ).filter(JournalEntry.credit_account == account.code)
        
        if from_date:
            query = query.filter(JournalEntry.entry_date >= from_date)
        if to_date:
            query = query.filter(JournalEntry.entry_date <= to_date)
        
        credit_arise = query.scalar() or 0.0
        
        # Số dư cuối kỳ
        closing_debit = opening_debit + debit_arise - credit_arise if (opening_debit + debit_arise) > credit_arise else 0.0
        closing_credit = opening_credit + credit_arise - debit_arise if (opening_credit + credit_arise) > debit_arise else 0.0
        
        # Chỉ hiển thị tài khoản có phát sinh hoặc có số dư
        if opening_debit > 0 or opening_credit > 0 or debit_arise > 0 or credit_arise > 0 or closing_debit > 0 or closing_credit > 0:
            result.append({
                "code": account.code,
                "name": account.name,
                "opening_debit": opening_debit,
                "opening_credit": opening_credit,
                "debit_arise": debit_arise,
                "credit_arise": credit_arise,
                "closing_debit": closing_debit,
                "closing_credit": closing_credit
            })
    
    # Tính tổng
    total_opening_debit = sum(r["opening_debit"] for r in result)
    total_opening_credit = sum(r["opening_credit"] for r in result)
    total_debit_arise = sum(r["debit_arise"] for r in result)
    total_credit_arise = sum(r["credit_arise"] for r in result)
    total_closing_debit = sum(r["closing_debit"] for r in result)
    total_closing_credit = sum(r["closing_credit"] for r in result)
    
    return {
        "accounts": result,
        "summary": {
            "opening_debit": total_opening_debit,
            "opening_credit": total_opening_credit,
            "debit_arise": total_debit_arise,
            "credit_arise": total_credit_arise,
            "closing_debit": total_closing_debit,
            "closing_credit": total_closing_credit
        }
    }
