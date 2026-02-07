import pandas as pd
import os

# --- CẤU HÌNH ---
# 1. Tên file CSV của bạn (Bạn SỬA LẠI tên này cho đúng tên file bạn mới bỏ vào)
ten_file_csv = "Review-Cong-Ty-xlsx-2.csv"  # Ví dụ: file_moi.csv

# Đường dẫn (Máy tự tìm trong thư mục raw)
duong_dan_csv = f"../data/raw/{"glassdoor_reviews.csv"}"
duong_dan_excel = duong_dan_csv.replace(".csv", ".xlsx") # Tự tạo tên file Excel

print(f"🔄 Đang chuyển đổi file: {ten_file_csv} ...")

try:
    # Bước 1: Đọc file CSV (Thử các bảng mã phổ biến để bắt tiếng Việt)
    try:
        # Thử đọc chuẩn UTF-8 (Phổ biến nhất)
        df = pd.read_csv(duong_dan_csv, encoding='utf-8')
    except:
        try:
            # Nếu lỗi, thử đọc UTF-16 (File xuất từ một số tool)
            df = pd.read_csv(duong_dan_csv, encoding='utf-16', sep='\t')
        except:
            # Nếu vẫn lỗi, thử ISO-8859-1 (Ít gặp nhưng có thể)
            df = pd.read_csv(duong_dan_csv, encoding='ISO-8859-1')

    # Bước 2: Lưu sang Excel (.xlsx)
    df.to_excel(duong_dan_excel, index=False)
    
    print("-" * 40)
    print("✅ THÀNH CÔNG! Đã tạo ra file Excel mới.")
    print(f"📁 File mới nằm tại: {duong_dan_excel}")
    print("-" * 40)
    print("👉 Bây giờ bạn có thể dùng code cũ để đọc file Excel này bình thường!")

except Exception as e:
    print("❌ LỖI RỒI: Không tìm thấy file hoặc file bị hỏng.")
    print("Lỗi chi tiết:", e)
    print("💡 Mẹo: Hãy kiểm tra kỹ xem tên file trong code có đúng y hệt tên file trong thư mục data/raw không?")