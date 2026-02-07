import pandas as pd
import sqlite3
import os

# ==========================================
# CẤU HÌNH ĐƯỜNG DẪN (Đã sửa để trỏ vào folder notebooks/data)
# ==========================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SỬA DÒNG NÀY: Thêm 'notebooks' vào đường dẫn
INPUT_FILE = os.path.join(BASE_DIR, 'notebooks', 'data', 'final_data_for_app.xlsx')

# DB vẫn để ở folder data gốc cho gọn
DB_FILE = os.path.join(BASE_DIR, 'data', 'job_radar.db')
def run_import():
    print(" BẮT ĐẦU QUY TRÌNH NẠP DỮ LIỆU VÀO SQL...")
    
    # 1. KIỂM TRA FILE ĐẦU VÀO
    if not os.path.exists(INPUT_FILE):
        print(f" Lỗi: Không tìm thấy file đầu vào tại: {INPUT_FILE}")
        print(" Hãy chạy Notebook bước 6 (Gán nhãn) trước!")
        return

    # 2. ĐỌC DỮ LIỆU (EXTRACT)
    print(f" Đang đọc dữ liệu từ: {os.path.basename(INPUT_FILE)}...")
    try:
        df = pd.read_excel(INPUT_FILE)
        print(f"   -> Đã đọc {len(df)} dòng dữ liệu.")
    except Exception as e:
        print(f"Lỗi đọc Excel: {e}")
        return

    # 3. LÀM SẠCH LẦN CUỐI (TRANSFORM - OPTIONAL)
    # Đảm bảo các cột quan trọng không bị NULL để tránh lỗi App
    df['Ten_Cong_Ty'] = df['Ten_Cong_Ty'].fillna('Unknown Company')
    df['Noi_Dung_Review'] = df['Noi_Dung_Review'].fillna('')
    df['Tags'] = df['Tags'].fillna('')
    
    # 4. NẠP VÀO SQL (LOAD)
    print(f" Đang ghi vào Database: {os.path.basename(DB_FILE)}...")
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Tối ưu hóa: Tạo Index cho cột Ten_Cong_Ty để App tìm kiếm nhanh hơn
        df.to_sql('reviews', conn, if_exists='replace', index=False)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ten_cong_ty ON reviews (Ten_Cong_Ty)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_khu_vuc ON reviews (Khu_Vuc)")
        
        conn.commit()
        conn.close()
        print(" THÀNH CÔNG! Dữ liệu đã sẵn sàng trong SQL.")
        
    except Exception as e:
        print(f" Lỗi ghi Database: {e}")

if __name__ == "__main__":
    run_import()