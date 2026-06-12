# KBC Kế Toán

Phần mềm kế toán cho Công ty CP Đầu tư và Phát triển Sâm KBC theo **Thông tư 133/2016/TT-BTC** (Doanh nghiệp nhỏ và vừa).

## 🎯 Tính năng (Giai đoạn 1)

- ✅ Hệ thống tài khoản TT133 (100+ tài khoản)
- ✅ Số dư đầu kỳ 01/01/2026 (27 tài khoản, đã import từ BCĐTK 2025)
- ✅ Nhập chứng từ: Thu | Chi | Bán hàng | Mua hàng | Nhập kho | Xuất kho
- ✅ Tự động sinh bút toán Nợ/Có theo chuẩn TT133
- ✅ Sổ nhật ký chung
- ✅ Sổ cái từng tài khoản
- ✅ Bảng cân đối số phát sinh

## 📊 Số liệu đầu kỳ 2026

- **Tài sản:** 1.4 tỷ (tiền 24.7tr, thuế GTGT khấu trừ 109tr, hàng tồn 946tr, chi phí trả trước 240tr)
- **Nợ phải trả:** 1.04 tỷ (vay NH 770tr, phải trả NCC 253tr, khác 17tr)
- **Vốn chủ:** 3 tỷ
- **Lỗ lũy kế:** -2.33 tỷ ⚠️

## 🚀 API Endpoints

### Auth
- `POST /auth/token` - Đăng nhập (admin / kbc2026)

### Accounts
- `GET /accounts/` - Danh sách tài khoản
- `GET /accounts/opening-balances?fiscal_year=2026` - Số dư đầu kỳ
- `POST /accounts/opening-balances/import` - Import số dư từ JSON

### Vouchers
- `POST /vouchers/` - Tạo chứng từ mới
- `GET /vouchers/?voucher_type=ban_hang&from_date=2026-01-01` - Danh sách chứng từ
- `GET /vouchers/{id}` - Chi tiết chứng từ + bút toán
- `DELETE /vouchers/{id}` - Xóa chứng từ (kế toán trưởng)

### Reports
- `GET /reports/journal?from_date=2026-01-01&to_date=2026-12-31` - Sổ nhật ký chung
- `GET /reports/ledger/111?from_date=2026-01-01` - Sổ cái TK 111
- `GET /reports/trial-balance?fiscal_year=2026` - Bảng cân đối số phát sinh

## 🛠️ Tech Stack

- **Backend:** FastAPI + SQLAlchemy + SQLite
- **Auth:** JWT (bcrypt)
- **Deploy:** Docker container trên VPS Hostinger

## 📦 Cài đặt

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8002
```

## 🔗 Links

- **Backend API:** http://76.13.209.75:8002
- **GitHub:** https://github.com/dangkhoi116-cloud/kbc-ketoan
- **Docs:** http://76.13.209.75:8002/docs (Swagger UI)

## 📝 Giai đoạn 2 (Tương lai)

- [ ] Tờ khai thuế GTGT (mẫu 01/GTGT)
- [ ] Báo cáo tài chính (CĐKT, KQKD, LCTT)
- [ ] Frontend Next.js hoàn chỉnh
- [ ] Kết chuyển cuối kỳ tự động
- [ ] Quyết toán thuế TNDN

---

**Công ty CP Đầu tư và Phát triển Sâm KBC**  
MST: 6101298538 | ĐC: 222 Bà Triệu, P.Kon Tum, Quảng Ngãi
