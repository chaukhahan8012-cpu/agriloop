import streamlit as st
import pandas as pd
import random
import time
from datetime import datetime

st.set_page_config(page_title="AgriLoop MVP - 5 Steps", layout="wide", page_icon="🌾")

# ==========================
# CẤU HÌNH CSS & STYLE
# ==========================
st.markdown("""
    <style>
    .grab-card { border-left: 5px solid #00b14f; padding: 10px; background: #f9f9f9; margin-bottom: 10px; border-radius: 5px; }
    .layer1-card { border-left: 5px solid #fbbc05; padding: 10px; background: #fffde7; margin-bottom: 10px; }
    .layer2-card { border-left: 5px solid #4285f4; padding: 10px; background: #e8f0fe; margin-bottom: 10px; }
    .metric-box { background-color: #e8f5e9; padding: 15px; border-radius: 8px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# ==========================
# BIẾN HỆ THỐNG (GIẢ LẬP)
# ==========================
FEE_FIRST_MILE = 150000     # 150k/chuyến xe máy cày/ba gác
PRICE_MARKET_TRANSPORT = 3000000 # Giá thị trường chặng dài giả định
RATE_LAYER_1 = 0.8          # Xe rỗng chiều về (80%)
RATE_LAYER_2 = 0.9          # 3PL Đối tác (90%)

if "orders" not in st.session_state:
    st.session_state.orders = []
if "first_mile_trips" not in st.session_state:
    st.session_state.first_mile_trips = []

# ==========================
# SIDEBAR QUẢN LÝ VAI TRÒ
# ==========================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2664/2664552.png", width=80)
st.sidebar.title("AgriLoop Ecosystem")
role = st.sidebar.radio(
    "Đăng nhập với vai trò:",
    [
        "🏭 1. Nhà máy (Đầu ra)", 
        "🏪 2. Đại lý (Hub/QC)", 
        "🚜 3. Nông dân/HTX (First-mile)", 
        "🚛 4. Đối tác Vận tải (Middle-mile)", 
        "🏦 5. Admin & Tài chính"
    ]
)

st.title(f"{role.split('.')[1].strip()}")

# =====================================================
# VAI TRÒ 1: NHÀ MÁY (BƯỚC 1 & BƯỚC 5)
# =====================================================
if "Nhà máy" in role:
    st.header("Bước 1: Kích hoạt nhu cầu (Demand Activation)")
    
    with st.form("factory_order"):
        col1, col2, col3 = st.columns(3)
        factory_name = col1.selectbox("Nhà máy", ["NM Điện sinh khối ĐBSCL", "NM Viên nén Hậu Giang", "NM Phân bón hữu cơ"])
        product = col2.selectbox("Loại phụ phẩm", ["Rơm cuộn", "Rơm rời", "Vỏ trấu"])
        weight = col3.number_input("Khối lượng (Tấn)", min_value=10, value=50)
        
        col4, col5 = st.columns(2)
        max_price = col4.number_input("Giá trần đề xuất (VNĐ/Tấn)", value=850000, step=50000)
        deadline = col5.date_input("Hạn chót giao hàng")
        
        if st.form_submit_button("Khớp lệnh Hệ thống (Matching)"):
            new_id = f"AL{len(st.session_state.orders)+1:03}"
            st.session_state.orders.append({
                "ID": new_id, "Nhà máy": factory_name, "Sản phẩm": product,
                "Khối lượng": weight, "Giá trần": max_price, "Deadline": str(deadline),
                "Trạng thái": "Đang tìm Đại lý", "Tổng tiền": weight * max_price
            })
            st.success(f"Đã phát lệnh {new_id}! AI đang quét Đại lý phù hợp trong bán kính 20km...")

    st.markdown("---")
    st.header("Bước 5: Xác nhận mã QR & Quyết toán")
    for order in st.session_state.orders:
        if order["Trạng thái"] == "Đã đến Nhà máy":
            st.warning(f"Đơn {order['ID']} ({order['Khối lượng']} tấn {order['Sản phẩm']}) đang chờ xác nhận.")
            if st.button(f"Quét QR Nhận hàng {order['ID']}"):
                order["Trạng thái"] = "Hoàn tất - Chờ Auto-split"
                st.rerun()

# =====================================================
# VAI TRÒ 2: ĐẠI LÝ / HUB (BƯỚC 2 & BƯỚC 4)
# =====================================================
elif "Đại lý" in role:
    st.header("Chợ Đơn hàng (Đã lọc theo Rating & Khoảng cách)")
    for order in st.session_state.orders:
        if order["Trạng thái"] == "Đang tìm Đại lý":
            with st.expander(f"🔥 {order['ID']} - Từ: {order['Nhà máy']}", expanded=True
