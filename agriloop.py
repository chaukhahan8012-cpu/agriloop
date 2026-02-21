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
            with st.expander(f"🔥 {order['ID']} - Từ: {order['Nhà máy']}", expanded=True):
                st.write(f"**Yêu cầu:** {order['Khối lượng']} Tấn {order['Sản phẩm']} | **Giá:** {order['Giá trần']:,.0f} đ/tấn")
                if st.button(f"Nhận thầu đơn {order['ID']}"):
                    order["Trạng thái"] = "Đang thu gom (First-mile)"
                    # Tự động tạo cuốc xe chặng ngắn
                    trips_needed = int(order['Khối lượng'] / 2) # Giả sử 1 xe ba gác chở 2 tấn
                    for i in range(trips_needed):
                        st.session_state.first_mile_trips.append({
                            "Trip_ID": f"{order['ID']}-FM{i+1}", "Order_ID": order['ID'],
                            "Trạng thái": "Đang chờ xế", "Khối lượng": 2
                        })
                    st.rerun()

    st.markdown("---")
    st.header("Bước 4: Kiểm tra chất lượng (QC) tại Hub")
    for order in st.session_state.orders:
        if order["Trạng thái"] == "Đang thu gom (First-mile)":
            # Kiểm tra xem các cuốc xe nhỏ đã gom xong chưa
            related_trips = [t for t in st.session_state.first_mile_trips if t["Order_ID"] == order["ID"]]
            completed_trips = [t for t in related_trips if t["Trạng thái"] == "Đã hạ tải tại Hub"]
            
            st.write(f"**Đơn {order['ID']}**: Đã gom {len(completed_trips)}/{len(related_trips)} cuốc chặng ngắn.")
            
            if len(related_trips) > 0 and len(completed_trips) == len(related_trips):
                with st.container(border=True):
                    st.write("📸 **AI Computer Vision Check:** Màu sắc vàng óng (Đạt)")
                    moisture = st.slider(f"Đo độ ẩm lô {order['ID']} bằng Cảm biến (%)", 10, 40, 20)
                    if st.button(f"Ký duyệt xuất kho {order['ID']}"):
                        if moisture <= 25:
                            order["Trạng thái"] = "Chờ xe chặng dài (Middle-mile)"
                            st.success("Đạt chuẩn ESG & Độ ẩm. Đã đẩy lệnh tìm xe tải lớn!")
                            st.rerun()
                        else:
                            st.error("Độ ẩm >25%. Yêu cầu phơi thêm!")

# =====================================================
# VAI TRÒ 3: NÔNG DÂN / HTX (FIRST-MILE - MÔ HÌNH GRAB)
# =====================================================
elif "Nông dân" in role:
    st.header("📱 App Nông dân (Grab cho Máy cày/Ba gác)")
    st.info("💡 Bật app để nhận cuốc vận chuyển rơm từ ruộng về Hub gần nhất.")
    
    available_trips = [t for t in st.session_state.first_mile_trips if t["Trạng thái"] == "Đang chờ xế"]
    
    col1, col2 = st.columns(2)
    col1.metric("Thu nhập hôm nay", "0 đ")
    col2.metric("Điểm tín nhiệm", "4.9/5.0 ⭐")

    if not available_trips:
        st.write("Hiện không có cuốc xe nào quanh khu vực của bạn.")
    else:
        for trip in available_trips:
            st.markdown(f"""
            <div class="grab-card">
                <h4>📍 Cuốc: {trip['Trip_ID']}</h4>
                <p>Khối lượng: {trip['Khối lượng']} Tấn Rơm | Quãng đường: ~3km</p>
                <p style="color: #00b14f; font-weight: bold; font-size: 18px;">Thù lao: {FEE_FIRST_MILE:,.0f} VNĐ</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Nhận cuốc {trip['Trip_ID']}"):
                trip["Trạng thái"] = "Đã hạ tải tại Hub"
                st.toast(f"Đã hoàn thành cuốc {trip['Trip_ID']}. Tiền sẽ cộng vào Ví!")
                st.rerun()

# =====================================================
# VAI TRÒ 4: ĐỐI TÁC VẬN TẢI (MIDDLE-MILE - 3 LAYER LOGISTICS)
# =====================================================
elif "Vận tải" in role:
    st.header("🚛 Sàn Vận tải Chặng dài (Middle-mile)")
    
    for order in st.session_state.orders:
        if order["Trạng thái"] == "Chờ xe chặng dài (Middle-mile)":
            st.subheader(f"Mã hàng: {order['ID']} - {order['Khối lượng']} Tấn về {order['Nhà máy']}")
            
            # Layer 1: Xe rỗng
            st.markdown(f"""
            <div class="layer1-card">
                <b>🥇 Lớp 1: Xe rỗng chiều về (Back-haul)</b> - Ưu tiên hiển thị trước<br>
                <i>Cước phí (80%): {PRICE_MARKET_TRANSPORT * RATE_LAYER_1:,.0f} VNĐ</i>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Nhận chuyến (Layer 1) - {order['ID']}"):
                order["Trạng thái"] = "Đã đến Nhà máy"
                order["Cước_Middle_Mile"] = PRICE_MARKET_TRANSPORT * RATE_LAYER_1
                st.rerun()
            
            # Layer 2: 3PL
            st.markdown(f"""
            <div class="layer2-card">
                <b>🥈 Lớp 2: Đối tác chiến lược (Logivan/EcoTruck)</b><br>
                <i>Cước phí (90%): {PRICE_MARKET_TRANSPORT * RATE_LAYER_2:,.0f} VNĐ</i>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Điều xe Đối tác (Layer 2) - {order['ID']}"):
                order["Trạng thái"] = "Đã đến Nhà máy"
                order["Cước_Middle_Mile"] = PRICE_MARKET_TRANSPORT * RATE_LAYER_2
                st.rerun()

# =====================================================
# VAI TRÒ 5: ADMIN & TÀI CHÍNH (BƯỚC 5: AUTO-SPLIT PAYMENT)
# =====================================================
elif "Admin" in role:
    st.header("Cổng Thanh toán MoMo/VNPay & Quản lý Tín dụng")
    
    ready_to_split = [o for o in st.session_state.orders if o["Trạng thái"] == "Hoàn tất - Chờ Auto-split"]
    
    if not ready_to_split:
        st.info("Chưa có đơn hàng nào chờ quyết toán.")
        
    for order in ready_to_split:
        with st.container(border=True):
            st.subheader(f"Lệnh Giải Ngân Đơn {order['ID']}")
            st.write(f"Tổng tiền từ Nhà máy: **{order['Tổng tiền']:,.0f} VNĐ**")
            
            # Tính toán dòng tiền (Giả lập logic)
            total_first_mile = len([t for t in st.session_state.first_mile_trips if t["Order_ID"] == order["ID"]]) * FEE_FIRST_MILE
            middle_mile_cost = order.get("Cước_Middle_Mile", PRICE_MARKET_TRANSPORT)
            platform_fee = order['Tổng tiền'] * 0.05
            risk_fund = order['Tổng tiền'] * 0.01
            agent_profit = order['Tổng tiền'] - total_first_mile - middle_mile_cost - platform_fee - risk_fund
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("💸 **Auto-split Payment:**")
                st.write(f"- Chuyển Nông dân/HTX (First-mile): `{total_first_mile:,.0f} VNĐ`")
                st.write(f"- Chuyển Đối tác Vận tải (Middle-mile): `{middle_mile_cost:,.0f} VNĐ`")
                st.write(f"- Phí Sàn AgriLoop (5%): `{platform_fee:,.0f} VNĐ`")
                st.write(f"- Trích Quỹ Rủi ro (1%): `{risk_fund:,.0f} VNĐ`")
                st.write(f"- **Thanh toán Đại lý (Lợi nhuận/Tiền rơm):** `{agent_profit:,.0f} VNĐ`")
            
            with col2:
                st.markdown("📈 **Credit Data Provider:**")
                st.success("Dữ liệu dòng tiền của Đại lý này đã được đồng bộ với Ngân hàng. Đủ điều kiện tăng hạn mức vốn lưu động lên 200 Triệu VNĐ.")
                
            if st.button(f"⚡ Thực thi API Giải ngân (MoMo/VNPay) cho {order['ID']}"):
                order["Trạng thái"] = "Đã thanh toán (Closed)"
                st.toast("Dòng tiền đã được phân bổ tự động đến các ví thành viên!")
                st.rerun()

st.markdown("---")
with st.expander("Sổ cái Hệ thống (Toàn bộ dữ liệu)"):
    if st.session_state.orders:
        st.dataframe(pd.DataFrame(st.session_state.orders), use_container_width=True)
