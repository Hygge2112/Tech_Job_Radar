import streamlit as st
import pandas as pd
import plotly.express as px
import os

# -----------------------------------------------------------------------------
# 1. CẤU HÌNH TRANG & CSS
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Tech Job Radar", page_icon="radar", layout="wide")

st.markdown("""
<style>
    .main {background-color: #f8f9fa;}
    
    /* Card Review Styling */
    .review-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border: 1px solid #eee;
        transition: transform 0.2s;
    }
    .review-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
    }
    
    /* Border colors */
    .card-toxic {border-left: 5px solid #dc3545;}
    .card-good {border-left: 5px solid #28a745;}
    .card-normal {border-left: 5px solid #6c757d;}

    /* Badge Styles */
    .tag-badge {
        display: inline-block;
        padding: 3px 10px;
        margin: 2px;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .tag-red {background-color: #ffe6e6; color: #cc0000;}
    .tag-green {background-color: #e6fffa; color: #006600;}
    .tag-blue {background-color: #e6f7ff; color: #0050b3;}
    .tag-gray {background-color: #f8f9fa; color: #666; border: 1px solid #ddd;}
    
    /* AI Badge */
    .ai-badge {
        display: inline-block;
        font-size: 0.75rem;
        font-weight: bold;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        margin-bottom: 8px;
    }
    .ai-pos {background-color: #28a745;}
    .ai-neg {background-color: #dc3545;}
    .ai-neu {background-color: #6c757d;}

    .company-name { font-size: 1.4rem; font-weight: 800; color: #2c3e50; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. HÀM XỬ LÝ DỮ LIỆU
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    possible_paths = [
        "data/processed/final_data_for_app.xlsx",
        "data/final_data_for_app.xlsx",
        "../data/final_data_for_app.xlsx",
        "final_data_for_app.xlsx"
    ]
    df = None
    for path in possible_paths:
        if os.path.exists(path):
            try:
                df = pd.read_excel(path)
                break
            except: continue
    
    if df is not None:
        if 'Tags' not in df.columns: df['Tags'] = ""
        if 'Khu_Vuc' not in df.columns: df['Khu_Vuc'] = "Việt Nam"
        if 'AI_Cam_Xuc' not in df.columns: df['AI_Cam_Xuc'] = 'NEU'
        if 'AI_Diem_So' not in df.columns: df['AI_Diem_So'] = 0.5
        # Chuẩn hóa dữ liệu để tìm kiếm dễ hơn
        df['Full_Text'] = df['Ten_Cong_Ty'].astype(str) + " " + df['Noi_Dung_Review'].astype(str) + " " + df['Tags'].astype(str)
        df['Full_Text'] = df['Full_Text'].str.lower()
        return df
    return None

def render_tags(tags_str):
    if not isinstance(tags_str, str): return ""
    tags = tags_str.split(", ")
    html = ""
    red_keys = ['toxic', 'tệ', 'thấp', 'nợ', 'quỵt', 'drama', 'bào', 'xấu', 'ép', 'nghỉ việc']
    green_keys = ['cao', 'tốt', 'thưởng', 'nice', 'support', 'vui', 'bảo hiểm', 'phúc lợi', 'xịn']
    
    for t in tags:
        if t in ["Chưa phân loại", "nan", ""]: continue
        t_lower = t.lower()
        style = "tag-gray"
        
        if any(k in t_lower for k in red_keys) and 'không' not in t_lower: style = "tag-red"
        elif any(k in t_lower for k in green_keys): style = "tag-green"
        elif 'phỏng vấn' in t_lower or 'công nghệ' in t_lower or 'đào tạo' in t_lower: style = "tag-blue"
        
        html += f'<span class="tag-badge {style}">{t}</span>'
    return html

def render_ai_badge(sentiment, score):
    label, style = "😐 Trung lập", "ai-neu"
    if sentiment == 'POS': label, style = "😊 Tích cực", "ai-pos"
    elif sentiment == 'NEG': label, style = "😡 Tiêu cực", "ai-neg"
    return f'<span class="ai-badge {style}">AI: {label} ({score:.0%})</span>'

# -----------------------------------------------------------------------------
# 3. GIAO DIỆN & BỘ LỌC NÂNG CAO
# -----------------------------------------------------------------------------
df = load_data()

if df is None:
    st.error("❌ Không tìm thấy dữ liệu. Vui lòng kiểm tra thư mục 'data'.")
    st.stop()

# === SIDEBAR NÂNG CAO ===
with st.sidebar:
    st.title("🌪️ Bộ Lọc Radar")
    st.caption("Tìm kiếm insight công ty IT")
    
    # 1. Tìm kiếm từ khóa
    search_query = st.text_input("🔍 Từ khóa:", placeholder="VD: Java, OT, lương...")
    
    st.divider()
    
    # 2. Khu vực (Multiselect - Chọn nhiều nơi)
    st.markdown("##### 📍 Khu vực làm việc")
    unique_regions = sorted([str(x) for x in df['Khu_Vuc'].dropna().unique()])
    selected_regions = st.multiselect("Chọn địa điểm:", unique_regions, default=[])
    
    st.divider()

    # 3. Lọc theo nhóm TAGS (Chi tiết hơn)
    st.markdown("##### 🏷️ Tiêu chí quan tâm")
    
    with st.expander("💰 Lương & Phúc lợi", expanded=True):
        salary_opts = ['Lương Cao', 'Thưởng Tốt', 'Bảo Hiểm Full', 'Review Lương Tốt', 'Lương Thấp', 'Nợ Lương']
        selected_salary = st.multiselect("Chọn tiêu chí lương:", salary_opts)
        
    with st.expander("working Môi trường & Văn hóa"):
        env_opts = ['Môi trường Tốt', 'Sếp Nice', 'Đồng nghiệp Vui', 'Toxic', 'Drama', 'Gia đình trị', 'OT Nhiều']
        selected_env = st.multiselect("Chọn môi trường:", env_opts)
        
    with st.expander("🎓 Phỏng vấn & Khác"):
        other_opts = ['Quy Trình Phỏng Vấn', 'Đào tạo', 'Cơ hội thăng tiến', 'Tiếng Anh']
        selected_other = st.multiselect("Chọn tiêu chí khác:", other_opts)

    # 4. Checkbox "Hot Keywords" (Quét trong nội dung review)
    st.divider()
    st.markdown("##### 🔥 Hình thức & Từ khóa hot")
    col_a, col_b = st.columns(2)
    with col_a:
        filter_remote = st.checkbox("🏠 Remote")
        filter_hybrid = st.checkbox("🔄 Hybrid")
    with col_b:
        filter_fresher = st.checkbox("🌱 Fresher")
        filter_english = st.checkbox("🇬🇧 English")

    # 5. Lọc AI
    st.divider()
    filter_sentiment = st.multiselect("🤖 Đánh giá bởi AI:", ['Tích cực (POS)', 'Tiêu cực (NEG)', 'Trung lập (NEU)'])

# === LOGIC LỌC DỮ LIỆU (MẠNH MẼ) ===
df_show = df.copy()

# 1. Lọc Khu vực (Cho phép chọn nhiều)
if selected_regions:
    df_show = df_show[df_show['Khu_Vuc'].isin(selected_regions)]

# 2. Lọc Từ khóa (Tìm trong mọi cột)
if search_query:
    q = search_query.strip().lower()
    df_show = df_show[df_show['Full_Text'].str.contains(q, na=False)]

# 3. Lọc Tags (Kết hợp các nhóm tags lại)
all_selected_tags = selected_salary + selected_env + selected_other
if all_selected_tags:
    # Logic: Chỉ cần chứa 1 trong các tag đã chọn là hiển thị
    pattern = '|'.join([t.lower().replace(' ', '.*') for t in all_selected_tags]) # Regex linh hoạt
    df_show = df_show[df_show['Tags'].str.lower().str.contains(pattern, na=False, regex=True)]

# 4. Lọc Hot Keywords (Tìm trong nội dung review nếu Tag không có)
if filter_remote:
    df_show = df_show[df_show['Full_Text'].str.contains('remote|làm việc tại nhà', na=False)]
if filter_hybrid:
    df_show = df_show[df_show['Full_Text'].str.contains('hybrid|linh hoạt', na=False)]
if filter_fresher:
    df_show = df_show[df_show['Full_Text'].str.contains('fresher|thực tập|intern|mới ra trường', na=False)]
if filter_english:
    df_show = df_show[df_show['Full_Text'].str.contains('tiếng anh|english|nước ngoài', na=False)]

# 5. Lọc AI
if filter_sentiment:
    codes = []
    if 'Tích cực (POS)' in filter_sentiment: codes.append('POS')
    if 'Tiêu cực (NEG)' in filter_sentiment: codes.append('NEG')
    if 'Trung lập (NEU)' in filter_sentiment: codes.append('NEU')
    df_show = df_show[df_show['AI_Cam_Xuc'].isin(codes)]

# === MAIN CONTENT ===
st.title("📡 TECH JOB RADAR")
st.markdown("##### Hệ thống phân tích minh bạch thị trường tuyển dụng IT")

# Metrics
c1, c2, c3, c4 = st.columns(4)
c1.metric("🏢 Công ty", f"{df_show['Ten_Cong_Ty'].nunique():,}")
c2.metric("📝 Review hiển thị", f"{len(df_show):,}")
neg_count = len(df_show[df_show['AI_Cam_Xuc'] == 'NEG'])
pos_count = len(df_show[df_show['AI_Cam_Xuc'] == 'POS'])
c3.metric("🚩 Tiêu cực", f"{neg_count:,}", delta_color="inverse")
c4.metric("💎 Tích cực", f"{pos_count:,}")

# Biểu đồ phân tích (Chỉ hiện khi có dữ liệu lọc)
if not df_show.empty:
    with st.expander("📊 Phân tích kết quả lọc", expanded=False):
        c_chart1, c_chart2 = st.columns(2)
        with c_chart1:
            ai_stats = df_show['AI_Cam_Xuc'].value_counts().reset_index()
            ai_stats.columns = ['Cảm xúc', 'Số lượng']
            fig1 = px.pie(ai_stats, values='Số lượng', names='Cảm xúc', title='Tỷ lệ cảm xúc', 
                          color_discrete_sequence=['#dc3545', '#28a745', '#6c757d'])
            st.plotly_chart(fig1, use_container_width=True)
        with c_chart2:
            # Tách tags để đếm tần suất các từ khóa hot trong tập lọc
            tags_series = df_show['Tags'].str.split(', ').explode()
            tags_stats = tags_series.value_counts().head(8).reset_index()
            tags_stats.columns = ['Chủ đề', 'Số lượng']
            fig2 = px.bar(tags_stats, x='Số lượng', y='Chủ đề', orientation='h', title='Chủ đề nổi bật',
                          color='Số lượng', color_continuous_scale='Blues')
            st.plotly_chart(fig2, use_container_width=True)

st.divider()

# Danh sách Review
if df_show.empty:
    st.warning("🕵️ Không tìm thấy kết quả nào với bộ lọc hiện tại.")
else:
    limit = 50
    df_display = df_show.head(limit)
    if len(df_show) > limit:
        st.caption(f"⚠️ Đang hiển thị {limit}/{len(df_show)} kết quả mới nhất.")
        
    for i, row in df_display.iterrows():
        tags_str = str(row['Tags'])
        ai_sent = row.get('AI_Cam_Xuc', 'NEU')
        ai_score = row.get('AI_Diem_So', 0.5)

        # Logic viền card
        card_class = "card-normal"
        if ai_sent == 'NEG' or any(x in tags_str.lower() for x in ['toxic', 'tệ', 'nợ']):
            card_class = "card-toxic"
        elif ai_sent == 'POS' or any(x in tags_str.lower() for x in ['tốt', 'cao', 'nice']):
            card_class = "card-good"

        st.markdown(f"""
        <div class="review-card {card_class}">
            <div style="display:flex; justify-content:space-between; align-items:start;">
                <div>
                    <div class="company-name">{row['Ten_Cong_Ty']}</div>
                    <div style="font-size:0.9em; color:#666;">📍 {row['Khu_Vuc']}</div>
                </div>
                <div style="text-align:right;">
                    {render_ai_badge(ai_sent, ai_score)}
                </div>
            </div>
            
            <div style="margin-top: 10px;">
                {render_tags(tags_str)}
            </div>
            
            <hr style="margin: 12px 0; border-top: 1px solid #f0f0f0;">
            
            <div style="color: #333; line-height: 1.6; font-size: 0.95rem;">
                {str(row['Noi_Dung_Review'])[:350]}...
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander(f"📖 Xem chi tiết review"):
            st.write(row['Noi_Dung_Review'])

st.markdown("---")
st.markdown("<center>Tech Job Radar © 2026</center>", unsafe_allow_html=True)