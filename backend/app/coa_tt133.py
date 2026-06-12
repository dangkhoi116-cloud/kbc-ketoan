# -*- coding: utf-8 -*-
"""
Hệ thống tài khoản kế toán theo Thông tư 133/2016/TT-BTC
(Doanh nghiệp nhỏ và vừa)

Mỗi dòng: (mã TK, tên TK, mã TK cha, loại số dư)
loại số dư (kind):
  'D'  = dư Nợ (tài sản, chi phí)
  'C'  = dư Có (nguồn vốn, doanh thu)
  'DC' = lưỡng tính (có thể dư Nợ hoặc Có)
  'X'  = không số dư cuối kỳ (loại 5,6,7,8,9 - kết chuyển)
"""

TT133_ACCOUNTS = [
    # ===== LOẠI 1: TÀI SẢN NGẮN HẠN =====
    ("111", "Tiền mặt", None, "D"),
    ("1111", "Tiền Việt Nam", "111", "D"),
    ("1112", "Ngoại tệ", "111", "D"),
    ("112", "Tiền gửi ngân hàng", None, "D"),
    ("1121", "Tiền Việt Nam", "112", "D"),
    ("1122", "Ngoại tệ", "112", "D"),
    ("121", "Chứng khoán kinh doanh", None, "D"),
    ("128", "Đầu tư nắm giữ đến ngày đáo hạn", None, "D"),
    ("131", "Phải thu của khách hàng", None, "DC"),
    ("133", "Thuế GTGT được khấu trừ", None, "D"),
    ("1331", "Thuế GTGT được khấu trừ của hàng hóa, dịch vụ", "133", "D"),
    ("1332", "Thuế GTGT được khấu trừ của TSCĐ", "133", "D"),
    ("136", "Phải thu nội bộ", None, "DC"),
    ("138", "Phải thu khác", None, "DC"),
    ("141", "Tạm ứng", None, "D"),
    ("151", "Hàng mua đang đi đường", None, "D"),
    ("152", "Nguyên liệu, vật liệu", None, "D"),
    ("153", "Công cụ, dụng cụ", None, "D"),
    ("154", "Chi phí sản xuất, kinh doanh dở dang", None, "D"),
    ("155", "Thành phẩm", None, "D"),
    ("156", "Hàng hóa", None, "D"),
    ("157", "Hàng gửi đi bán", None, "D"),
    ("211", "Tài sản cố định", None, "D"),
    ("2111", "TSCĐ hữu hình", "211", "D"),
    ("2112", "TSCĐ thuê tài chính", "211", "D"),
    ("2113", "TSCĐ vô hình", "211", "D"),
    ("214", "Hao mòn tài sản cố định", None, "C"),
    ("217", "Bất động sản đầu tư", None, "D"),
    ("228", "Đầu tư góp vốn vào đơn vị khác", None, "D"),
    ("229", "Dự phòng tổn thất tài sản", None, "C"),
    ("241", "Xây dựng cơ bản dở dang", None, "D"),
    ("242", "Chi phí trả trước", None, "D"),

    # ===== LOẠI 3: NỢ PHẢI TRẢ =====
    ("331", "Phải trả cho người bán", None, "DC"),
    ("333", "Thuế và các khoản phải nộp Nhà nước", None, "DC"),
    ("3331", "Thuế GTGT phải nộp", "333", "DC"),
    ("33311", "Thuế GTGT đầu ra", "3331", "DC"),
    ("33312", "Thuế GTGT hàng nhập khẩu", "3331", "DC"),
    ("3332", "Thuế tiêu thụ đặc biệt", "333", "C"),
    ("3333", "Thuế xuất, nhập khẩu", "333", "C"),
    ("3334", "Thuế thu nhập doanh nghiệp", "333", "DC"),
    ("3335", "Thuế thu nhập cá nhân", "333", "C"),
    ("3336", "Thuế tài nguyên", "333", "C"),
    ("3338", "Thuế bảo vệ môi trường và các loại thuế khác", "333", "C"),
    ("3339", "Phí, lệ phí và các khoản phải nộp khác", "333", "C"),
    ("334", "Phải trả người lao động", None, "C"),
    ("335", "Chi phí phải trả", None, "C"),
    ("336", "Phải trả nội bộ", None, "DC"),
    ("338", "Phải trả, phải nộp khác", None, "DC"),
    ("3382", "Kinh phí công đoàn", "338", "C"),
    ("3383", "Bảo hiểm xã hội", "338", "C"),
    ("3384", "Bảo hiểm y tế", "338", "C"),
    ("3385", "Bảo hiểm thất nghiệp", "338", "C"),
    ("341", "Vay và nợ thuê tài chính", None, "C"),
    ("352", "Dự phòng phải trả", None, "C"),
    ("353", "Quỹ khen thưởng, phúc lợi", None, "C"),
    ("356", "Quỹ phát triển khoa học và công nghệ", None, "C"),

    # ===== LOẠI 4: VỐN CHỦ SỞ HỮU =====
    ("411", "Vốn đầu tư của chủ sở hữu", None, "C"),
    ("4111", "Vốn góp của chủ sở hữu", "411", "C"),
    ("4112", "Thặng dư vốn cổ phần", "411", "C"),
    ("4118", "Vốn khác", "411", "C"),
    ("413", "Chênh lệch tỷ giá hối đoái", None, "DC"),
    ("418", "Các quỹ thuộc vốn chủ sở hữu", None, "C"),
    ("419", "Cổ phiếu quỹ", None, "D"),
    ("421", "Lợi nhuận sau thuế chưa phân phối", None, "DC"),
    ("4211", "Lợi nhuận sau thuế chưa phân phối năm trước", "421", "DC"),
    ("4212", "Lợi nhuận sau thuế chưa phân phối năm nay", "421", "DC"),

    # ===== LOẠI 5: DOANH THU =====
    ("511", "Doanh thu bán hàng và cung cấp dịch vụ", None, "X"),
    ("5111", "Doanh thu bán hàng hóa", "511", "X"),
    ("5112", "Doanh thu bán thành phẩm", "511", "X"),
    ("5113", "Doanh thu cung cấp dịch vụ", "511", "X"),
    ("515", "Doanh thu hoạt động tài chính", None, "X"),
    ("521", "Các khoản giảm trừ doanh thu", None, "X"),

    # ===== LOẠI 6: CHI PHÍ SẢN XUẤT, KINH DOANH =====
    ("611", "Mua hàng", None, "X"),
    ("621", "Chi phí nguyên liệu, vật liệu trực tiếp", None, "X"),
    ("622", "Chi phí nhân công trực tiếp", None, "X"),
    ("627", "Chi phí sản xuất chung", None, "X"),
    ("631", "Giá thành sản xuất", None, "X"),
    ("632", "Giá vốn hàng bán", None, "X"),
    ("635", "Chi phí tài chính", None, "X"),
    ("642", "Chi phí quản lý kinh doanh", None, "X"),
    ("6421", "Chi phí bán hàng", "642", "X"),
    ("6422", "Chi phí quản lý doanh nghiệp", "642", "X"),

    # ===== LOẠI 7: THU NHẬP KHÁC =====
    ("711", "Thu nhập khác", None, "X"),

    # ===== LOẠI 8: CHI PHÍ KHÁC =====
    ("811", "Chi phí khác", None, "X"),
    ("821", "Chi phí thuế thu nhập doanh nghiệp", None, "X"),

    # ===== LOẠI 9: XÁC ĐỊNH KẾT QUẢ KINH DOANH =====
    ("911", "Xác định kết quả kinh doanh", None, "X"),
]
