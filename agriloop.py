import streamlit as st
import pandas as pd
import random
import time
from datetime import datetime

# Cấu hình trang
st.set_page_config(page_title="AgriLoop - Diamond System", layout="wide", page_icon="🌾")

# --- STYLE ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #2e7d32; color: white; }
    .status-card { padding: 20px; border-radius: 10px; background-color: white; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR (Role Selection) ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2664/2664552.png", width=100)
st.sidebar.title("AgriLoop System")
role = st.sidebar.selectbox("Chọn vai trò người dùng:", ["Quản trị viên (Admin)", "Đại lý (Agent)", "Tài xế (Driver)", "Nhà máy (Factory)"])

# --- MOCK DATA ---
if 'orders' not in st.session_state:
    st.session_state.orders = [
        {"ID": "AL001", "Sản phẩm": "Rơm cuộn", "Khối lượng": 15, "Vị trí": "Tam Nông", "Trạng thái": "Đang vận chuyển", "Chất lượng": "A"},
        {"ID": "AL002", "Sản phẩm": "Vỏ trấu", "Khối lượng": 10, "Vị trí": "Thanh Bình", "Trạng thái": "Chờ lấy hàng", "Chất lượng": "B"},
    ]

# --- MAIN PAGE ---
st.title(f"🚀 AgriLoop Dashboard - {role}")

if role == "Quản trị viên (Admin)":
    # 1. Tổng quan các chỉ số (KPIs)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tổng sản lượng (Tấn)", "12,450", "+12%")
    col2.metric("Doanh thu Margin", "450M VND", "+8%")
    col3.metric("Tỷ lệ xe rỗng (%)", "65%", "-5%")
    col4.metric("Quỹ rủi ro SLA", "85M VND", "Ổn định")

    # 2. Bản đồ điều phối (Giả lập)
    st.subheader("📍 Điều phối Logistics Dặm đầu (First-mile)")
    df_map = pd.DataFrame({
        'lat': [10.6667, 10.6750, 10.6500],
        'lon': [105.5833, 105.6000, 105.5700]
    })
    st.map(df_map)

elif role == "Đại lý (Agent)":
    st.subheader("📦 Tạo đơn hàng & Kiểm định AI")
    
    with st.form("order_form"):
        col_a, col_b = st.columns(2)
        product = col_a.selectbox("Loại phụ phẩm", ["Rơm rạ", "Vỏ trấu", "Bã mía", "Vỏ tôm"])
        weight = col_b.number_input("Khối lượng dự kiến (Tấn)", min_value=1)
        location = st.text_input("Vị trí chi tiết (Xã/Huyện)", "Tam Nông, Đồng Tháp")
        
        uploaded_file = st.file_uploader("Tải ảnh chụp tại ruộng (AI Pre-screen)", type=["jpg", "png"])
        
        submit = st.form_submit_button("Xác nhận & Khớp lệnh Vận chuyển")
        
        if submit:
            with st.spinner('AI đang phân tích độ ẩm và màu sắc...'):
                time.sleep(2)
                quality_score = random.choice(["A (Đạt chuẩn)", "B (Cần phơi thêm)"])
                st.success(f"Phân loại AI: {quality_score}. Đã tìm thấy 3 xe rỗng chiều về phù hợp!")
                st.session_state.orders.append({"ID": f"AL00{len(st.session_state.orders)+1}", "Sản phẩm": product, "Khối lượng": weight, "Vị trí": location, "Trạng thái": "Chờ lấy hàng", "Chất lượng": quality_score[0]})

elif role == "Tài xế (Driver)":
    st.subheader("🚛 Danh sách chuyến hàng phù hợp")
    # Thuật toán Matching ưu tiên xe rỗng chiều về
    st.info("Ưu tiên: 2 đơn hàng 'Xe rỗng chiều về' giúp bạn tối ưu 15% chi phí xăng dầu.")
    
    for order in st.session_state.orders:
        if order["Trạng thái"] == "Chờ lấy hàng":
            with st.expander(f"Đơn hàng {order['ID']} - {order['Vị trí']}"):
                st.write(f"Loại: {order['Sản phẩm']} | Khối lượng: {order['Khối lượng']} Tấn")
                if st.button(f"Nhận đơn {order['ID']}"):
                    st.toast(f"Đã nhận đơn {order['ID']}. Hệ thống đang cập nhật lộ trình GPS...")

# --- HIỂN THỊ DANH SÁCH ĐƠN HÀNG CHUNG ---
st.markdown("---")
st.subheader("📋 Quản lý giao dịch (Escrow Tracking)")
df = pd.DataFrame(st.session_state.orders)
st.table(df)

# --- FOOTER ---
st.caption("AgriLoop v1.0 | Giải pháp Logistics tuần hoàn cho Nông nghiệp Việt Nam")