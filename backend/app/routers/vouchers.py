from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models import Voucher, JournalEntry, Product
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

router = APIRouter()


class VoucherLineItem(BaseModel):
    product_id: Optional[int] = None
    description: str = ""
    quantity: float = 0.0
    unit_price: float = 0.0
    amount: float = 0.0


class VoucherCreate(BaseModel):
    voucher_type: str  # thu | chi | ban_hang | mua_hang | nhap_kho | xuat_kho
    voucher_date: date
    description: str = ""
    partner_name: str = ""
    total_amount: float = 0.0
    vat_amount: float = 0.0
    line_items: List[VoucherLineItem] = []


def auto_generate_journal_entries(voucher: Voucher, line_items: List[VoucherLineItem], db: Session):
    """
    Tự động sinh bút toán Nợ/Có dựa vào loại chứng từ
    """
    entries = []
    
    if voucher.voucher_type == "thu":
        # Phiếu thu: Nợ 111/112 (tiền) / Có 131/511 (tùy nghiệp vụ)
        # Đơn giản: Nợ 111 / Có 511 (doanh thu)
        entries.append(JournalEntry(
            voucher_id=voucher.id,
            entry_date=voucher.voucher_date,
            debit_account="111",
            credit_account="511",
            amount=voucher.total_amount,
            description=voucher.description
        ))
    
    elif voucher.voucher_type == "chi":
        # Phiếu chi: Nợ 642/331/... / Có 111/112
        # Đơn giản: Nợ 642 / Có 111
        entries.append(JournalEntry(
            voucher_id=voucher.id,
            entry_date=voucher.voucher_date,
            debit_account="642",
            credit_account="111",
            amount=voucher.total_amount,
            description=voucher.description
        ))
    
    elif voucher.voucher_type == "ban_hang":
        # Bán hàng (có VAT 8%):
        # 1. Nợ 131 (hoặc 111/112) / Có 511 (doanh thu chưa VAT) + Có 3331 (VAT đầu ra)
        amount_before_vat = voucher.total_amount - voucher.vat_amount
        
        # Bút toán 1: ghi nhận doanh thu + VAT
        entries.append(JournalEntry(
            voucher_id=voucher.id,
            entry_date=voucher.voucher_date,
            debit_account="131",  # Phải thu khách hàng
            credit_account="511",  # Doanh thu
            amount=amount_before_vat,
            description=f"Doanh thu bán hàng - {voucher.description}"
        ))
        
        entries.append(JournalEntry(
            voucher_id=voucher.id,
            entry_date=voucher.voucher_date,
            debit_account="131",
            credit_account="33311",  # Thuế GTGT đầu ra
            amount=voucher.vat_amount,
            description=f"VAT đầu ra 8% - {voucher.description}"
        ))
        
        # 2. Giá vốn: Nợ 632 / Có 156
        total_cost = sum(item.quantity * (item.unit_price / 1.08) * 0.7 for item in line_items)  # giả định giá vốn = 70% giá bán
        if total_cost > 0:
            entries.append(JournalEntry(
                voucher_id=voucher.id,
                entry_date=voucher.voucher_date,
                debit_account="632",  # Giá vốn
                credit_account="156",  # Hàng hóa
                amount=total_cost,
                description=f"Giá vốn hàng bán - {voucher.description}"
            ))
    
    elif voucher.voucher_type == "mua_hang":
        # Mua hàng (có VAT):
        # 1. Nợ 156 (hàng hóa) / Có 331 (phải trả NCC)
        # 2. Nợ 133 (thuế GTGT được khấu trừ) / Có 331
        amount_before_vat = voucher.total_amount - voucher.vat_amount
        
        entries.append(JournalEntry(
            voucher_id=voucher.id,
            entry_date=voucher.voucher_date,
            debit_account="156",
            credit_account="331",
            amount=amount_before_vat,
            description=f"Mua hàng hóa - {voucher.description}"
        ))
        
        if voucher.vat_amount > 0:
            entries.append(JournalEntry(
                voucher_id=voucher.id,
                entry_date=voucher.voucher_date,
                debit_account="1331",  # Thuế GTGT được khấu trừ
                credit_account="331",
                amount=voucher.vat_amount,
                description=f"VAT đầu vào 8% - {voucher.description}"
            ))
    
    elif voucher.voucher_type == "nhap_kho":
        # Nhập kho: Nợ 156 / Có 331 (nếu mua) hoặc Có 154 (nếu sản xuất)
        entries.append(JournalEntry(
            voucher_id=voucher.id,
            entry_date=voucher.voucher_date,
            debit_account="156",
            credit_account="331",
            amount=voucher.total_amount,
            description=voucher.description
        ))
    
    elif voucher.voucher_type == "xuat_kho":
        # Xuất kho: Nợ 632 (giá vốn) hoặc 152 (NVL) / Có 156
        entries.append(JournalEntry(
            voucher_id=voucher.id,
            entry_date=voucher.voucher_date,
            debit_account="632",
            credit_account="156",
            amount=voucher.total_amount,
            description=voucher.description
        ))
    
    # Lưu các bút toán
    for entry in entries:
        db.add(entry)
    
    return len(entries)


@router.post("/")
def create_voucher(item: VoucherCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Tạo chứng từ mới + tự động sinh bút toán"""
    
    # Tạo số chứng từ tự động
    prefix_map = {
        "thu": "PT",
        "chi": "PC",
        "ban_hang": "HD",
        "mua_hang": "MH",
        "nhap_kho": "NK",
        "xuat_kho": "XK"
    }
    prefix = prefix_map.get(item.voucher_type, "CT")
    
    # Đếm số chứng từ cùng loại trong năm
    year = item.voucher_date.year
    count = db.query(Voucher).filter(
        Voucher.voucher_type == item.voucher_type,
        Voucher.voucher_date >= date(year, 1, 1),
        Voucher.voucher_date <= date(year, 12, 31)
    ).count()
    
    voucher_no = f"{prefix}-{year}-{count + 1:04d}"
    
    # Tạo chứng từ
    voucher = Voucher(
        voucher_no=voucher_no,
        voucher_type=item.voucher_type,
        voucher_date=item.voucher_date,
        description=item.description,
        partner_name=item.partner_name,
        total_amount=item.total_amount,
        vat_amount=item.vat_amount,
        created_by=current_user["username"]
    )
    db.add(voucher)
    db.flush()  # để lấy voucher.id
    
    # Tự động sinh bút toán
    entries_count = auto_generate_journal_entries(voucher, item.line_items, db)
    
    db.commit()
    db.refresh(voucher)
    
    return {
        "message": f"Đã tạo chứng từ {voucher_no} với {entries_count} bút toán",
        "voucher": voucher
    }


@router.get("/")
def get_vouchers(
    voucher_type: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Lấy danh sách chứng từ"""
    query = db.query(Voucher)
    
    if voucher_type:
        query = query.filter(Voucher.voucher_type == voucher_type)
    if from_date:
        query = query.filter(Voucher.voucher_date >= from_date)
    if to_date:
        query = query.filter(Voucher.voucher_date <= to_date)
    
    vouchers = query.order_by(Voucher.voucher_date.desc(), Voucher.id.desc()).limit(limit).all()
    return {"vouchers": vouchers, "total": len(vouchers)}


@router.get("/{voucher_id}")
def get_voucher_detail(voucher_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Xem chi tiết chứng từ + bút toán"""
    voucher = db.query(Voucher).filter(Voucher.id == voucher_id).first()
    if not voucher:
        raise HTTPException(status_code=404, detail="Không tìm thấy chứng từ")
    
    entries = db.query(JournalEntry).filter(JournalEntry.voucher_id == voucher_id).all()
    
    return {
        "voucher": voucher,
        "entries": entries
    }


@router.delete("/{voucher_id}")
def delete_voucher(voucher_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Xóa chứng từ (chỉ kế toán trưởng)"""
    if current_user["role"] != "ke_toan_truong":
        raise HTTPException(status_code=403, detail="Chỉ kế toán trưởng mới được xóa chứng từ")
    
    voucher = db.query(Voucher).filter(Voucher.id == voucher_id).first()
    if not voucher:
        raise HTTPException(status_code=404, detail="Không tìm thấy chứng từ")
    
    # Xóa cascade (bút toán cũng xóa theo)
    db.delete(voucher)
    db.commit()
    
    return {"message": f"Đã xóa chứng từ {voucher.voucher_no}"}
