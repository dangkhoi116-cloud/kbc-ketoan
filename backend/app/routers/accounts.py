from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models import Account, OpeningBalance
from pydantic import BaseModel
from typing import List, Optional
import json

router = APIRouter()


class OpeningBalanceUpdate(BaseModel):
    account_code: str
    debit: float = 0.0
    credit: float = 0.0


@router.get("/")
def get_accounts(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Lấy danh sách tài khoản"""
    accounts = db.query(Account).filter(Account.is_active == 1).order_by(Account.code).all()
    return {"accounts": accounts}


@router.get("/opening-balances")
def get_opening_balances(fiscal_year: int = 2026, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Lấy số dư đầu kỳ"""
    balances = db.query(OpeningBalance).filter(OpeningBalance.fiscal_year == fiscal_year).all()
    return {"balances": balances}


@router.post("/opening-balances/import")
def import_opening_balances(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Import số dư đầu kỳ 2026 từ file JSON đã parse"""
    if current_user["role"] != "ke_toan_truong":
        raise HTTPException(status_code=403, detail="Chỉ kế toán trưởng mới được import số dư đầu kỳ")
    
    # Đọc file JSON
    import os
    json_path = os.path.join(os.path.dirname(__file__), "../../opening_balances_2026.json")
    if not os.path.exists(json_path):
        raise HTTPException(status_code=404, detail="File opening_balances_2026.json không tồn tại")
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Xóa số dư cũ (nếu có)
    db.query(OpeningBalance).filter(OpeningBalance.fiscal_year == 2026).delete()
    
    # Import
    count = 0
    for item in data:
        if item["code"] == "Cộng":  # bỏ dòng tổng
            continue
        ob = OpeningBalance(
            account_code=item["code"],
            fiscal_year=2026,
            debit=item["debit"],
            credit=item["credit"]
        )
        db.add(ob)
        count += 1
    
    db.commit()
    return {"message": f"Đã import {count} số dư đầu kỳ năm 2026", "count": count}


@router.post("/opening-balances")
def update_opening_balance(item: OpeningBalanceUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Cập nhật số dư đầu kỳ 1 tài khoản"""
    if current_user["role"] not in ["ke_toan_truong", "ke_toan_vien"]:
        raise HTTPException(status_code=403, detail="Không có quyền")
    
    ob = db.query(OpeningBalance).filter(
        OpeningBalance.account_code == item.account_code,
        OpeningBalance.fiscal_year == 2026
    ).first()
    
    if ob:
        ob.debit = item.debit
        ob.credit = item.credit
    else:
        ob = OpeningBalance(
            account_code=item.account_code,
            fiscal_year=2026,
            debit=item.debit,
            credit=item.credit
        )
        db.add(ob)
    
    db.commit()
    db.refresh(ob)
    return {"message": "Đã cập nhật số dư đầu kỳ", "balance": ob}
