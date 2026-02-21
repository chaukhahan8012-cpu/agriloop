import streamlit as st
import pandas as pd
import random
from datetime import datetime

st.set_page_config(page_title="AgriLoop - Diamond System", layout="wide", page_icon="🌾")

# ==========================
# CẤU HÌNH CSS
# ==========================
st.markdown("""
    <style>
    .invoice-box { background-color: #f1f8e9; padding: 20px; border-radius: 10px; border: 1px solid #c5e1a5; margin-bottom: 20px; }
    .farmer-card { border-left: 4px solid #ff9800; padding: 15px; background: #fff8e1; margin-bottom: 10px; border-radius: 5px;}
    .transport-box { border: 2px dashed #1976d2; padding: 15px; background-color: #e3f2fd; border-radius: 8px; margin-top: 15px;}
    </style>
""", unsafe_allow_html=True)

# ==========================
# BẢNG GIÁ NIÊM YẾT (AGRILOOP QUY ĐỊNH)
# ==========================
PRICES = {
    "Rơm cuộn": 850000,
    "Rơm rời": 600000
}
SHIPPING_RATE_PER_TON = 200000 # Ước tính vận chuyển
PLATFORM_FEE_RATE = 0.05       # 5% phí sàn

# ==========================
# KHỞI TẠO SESSION STATE
# ==========================
if "orders" not in st.session_state:
    st.session_state.orders = []
if "farmer_offers" not in st.session_state:
    st.session_state.farmer_offers = [] 
if "agent_points" not in st.session_state:
    st.session_state.agent_points = 1250 

# ==========================
# SIDEBAR
# ==========================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2664/2664552.png", width=80)
st.sidebar.title("AgriLoop MVP")
role = st.sidebar.radio(
    "Đăng nhập với vai trò:",
    [
        "🏭 Nhà máy", 
        "🏪 Đại lý (Hub & Điều phối)", 
        "🌾 Nông dân (Zalo Mini App)"
    ]
)

st.title(f"{role}")

# =====================================================
# VAI TRÒ 1: NHÀ MÁY
# =====================================================
if role == "🏭 Nhà máy":
    st.header("1. Tạo Lệnh Thu Mua & Đặt Cọc")
    
    with st.form("factory_order"):
        col1, col2 = st.columns(2)
        factory_name = col1.text_input("Tên Nhà máy", "NM Điện Sinh Khối Hậu Giang")
        address = col2.text_input("Địa chỉ giao hàng", "KCN Sông Hậu, Hậu Giang")
        
        col3, col4, col5 = st.columns(3)
        product = col3.selectbox("Loại phụ phẩm", ["Rơm cuộn", "Rơm rời"])
        weight = col4.number_input("Khối lượng cần mua (Tấn)", min_value=10, value=50)
        deadline = col5.date_input("Hạn chót nhận hàng")
        
        base_cost = weight * PRICES[product]
        shipping_est = weight * SHIPPING_RATE_PER_TON
        subtotal = base_cost + shipping_est
        platform_fee = subtotal * PLATFORM_FEE_RATE
        total_cost = subtotal + platform_fee
        deposit_amount = total_cost * 0.3 
        
        st.markdown(f"""
        <div class="invoice-box">
            <h4>🧾 Hóa đơn Tạm tính (AgriLoop niêm yết)</h4>
            <p>- <b>Tiền rơm ({PRICES[product]:,.0f} đ/tấn):</b> {base_cost:,.0f} đ</p>
            <p>- <b>Phí vận chuyển dự kiến:</b> {shipping_est:,.0f} đ</p>
            <p>- <b>Phí nền tảng (5%):</b> {platform_fee:,.0f} đ</p>
            <hr>
            <h3 style="color: #2e7d32;">Tổng thanh toán: {total_cost:,.0f} đ</h3>
            <p style="color: #d32f2f; font-weight: bold;">⚠️ Yêu cầu thanh toán cọc 30%: {deposit_amount:,.0f} đ</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.form_submit_button("Xác nhận & Chuyển sang thanh toán cọc"):
            new_id = f"AL{len(st.session_state.orders)+1:03}"
            st.session_state.orders.append({
                "ID": new_id, "Nhà máy": factory_name, "Địa chỉ": address,
                "Sản phẩm": product, "Khối lượng": weight, "Deadline": str(deadline),
                "Trạng thái": "Chờ quét QR Cọc", "Tổng tiền": total_cost, 
                "Đã gom": 0, "Tiền cọc": deposit_amount
            })
            st.success("Đã tạo đơn. Vui lòng thanh toán cọc bên dưới!")
            st.rerun()

    for order in st.session_state.orders:
        if order["Trạng thái"] == "Chờ quét QR Cọc":
            st.markdown("---")
            col_qr, col_info = st.columns([1, 2])
            with col_qr:
                st.image("https://upload.wikimedia.org/wikipedia/commons/d/d0/QR_code_for_mobile_English_Wikipedia.svg", width=150)
            with col_info:
                st.subheader(f"Thanh toán cọc Đơn {order['ID']}")
                if st.button(f"Mô phỏng: Đã thanh toán {order['Tiền cọc']:,.0f} VNĐ ({order['ID']})"):
                    order["Trạng thái"] = "Sẵn sàng cho Đại lý"
                    st.rerun()
                    
    st.header("2. Theo dõi & Nhận Hàng")
    for order in st.session_state.orders:
        if order["Trạng thái"] == "Đang giao đến Nhà máy":
            st.warning(f"🚛 Đơn {order['ID']} đang trên đường đến nhà máy của bạn!")
            if st.button(f"✅ Xác nhận đã nhận {order['Khối lượng']} Tấn ({order['ID']})"):
                order["Trạng thái"] = "Hoàn tất"
                st.success("Giao dịch hoàn tất!")
                st.rerun()

# =====================================================
# VAI TRÒ 2: ĐẠI LÝ (HUB & ĐIỀU PHỐI LOGISTICS)
# =====================================================
elif role == "🏪 Đại lý (Hub & Điều phối)":
    st.sidebar.markdown("---")
    st.sidebar.metric("🌟 Điểm tích lũy", f"{st.session_state.agent_points} pt")
    
    st.header("Chợ Lệnh Thu Mua")
    available_orders = [o for o in st.session_state.orders if o["Trạng thái"] == "Sẵn sàng cho Đại lý"]
    for order in available_orders:
        with st.container(border=True):
            st.write(f"🏭 **{order['Nhà máy']}** cần **{order['Khối lượng']} Tấn {order['Sản phẩm']}**")
            if st.button(f"Nhận thầu đơn {order['ID']}"):
                order["Trạng thái"] = "Đại lý đang gom"
                st.session_state.agent_points += 50
                st.rerun()

    st.markdown("---")
    st.header("Trung Tâm Thu Gom & Điều Phối Vận Tải")
    active_orders = [o for o in st.session_state.orders if o["Trạng thái"] == "Đại lý đang gom"]
    
    for order in active_orders:
        st.subheader(f"📦 Đơn {order['ID']} - {order['Nhà máy']}")
        progress_pct = min(order['Đã gom'] / order['Khối lượng'], 1.0)
        st.progress(progress_pct, text=f"Đã gom {order['Đã gom']}/{order['Khối lượng']} Tấn")
        
        # BƯỚC A: Gửi Zalo tìm nguồn rơm
        if st.button(f"📢 Phát tín hiệu tìm rơm qua Zalo cho Nông dân ({order['ID']})"):
            order["Broadcast_Zalo"] = True
            st.toast("Đã gửi tin nhắn Zalo hàng loạt!")
            
        # BƯỚC B: Điều phối chặng ngắn (Xử lý phản hồi từ nông dân)
        offers = [f for f in st.session_state.farmer_offers if f["Order_ID"] == order["ID"]]
        if offers:
            st.markdown("#### 🚜 Quản lý Chặng Ngắn (Gom từ ruộng về Hub)")
            for offer in offers:
                if offer["Trạng thái"] == "Chờ xử lý":
                    with st.container(border=True):
                        st.write(f"🧑‍🌾 **{offer['Tên']}** - Cung cấp: **{offer['Khối lượng']} Tấn**")
                        if offer['Phương thức'] == "Đại lý lại gom":
                            st.info("📍 Nông dân yêu cầu Đại lý đến ruộng thu gom.")
                            if st.button(f"👉 Đặt xe Ba Gác đi gom ngay ({offer['ID']})"):
                                offer["Trạng thái"] = "Đã nhập kho"
                                order["Đã gom"] += offer["Khối lượng"]
                                st.rerun()
                        else:
                            st.success("🚚 Nông dân tự chở rơm đến Hub.")
                            if st.button(f"👉 Xác nhận Nông dân đã giao tới ({offer['ID']})"):
                                offer["Trạng thái"] = "Đã nhập kho"
                                order["Đã gom"] += offer["Khối lượng"]
                                st.rerun()
                elif offer["Trạng thái"] == "Đã nhập kho":
                    st.caption(f"✅ Đã nhập {offer['Khối lượng']} tấn từ {offer['Tên']}")
        
        # BƯỚC C: Điều phối chặng dài (Giao cho Nhà máy)
        if order['Đã gom'] >= order['Khối lượng']:
            st.markdown(f"""
            <div class="transport-box">
                <h4 style="color: #1976d2;">🚛 Kho đã đầy - Điều phối Vận tải Chặng Dài</h4>
                <p>Hệ thống tự động đề xuất phương tiện tối ưu chi phí để giao hàng đến <b>{order['Địa chỉ']}</b>.</p>
            </div>
            """, unsafe_allow_html=True)
            
            truck_type = st.radio("Chọn xe chặng dài:", [
                "🥇 Xe tải rỗng chiều về (Tiết kiệm 20% cước)", 
                "🥈 Xe đối tác 3PL - Logivan (Đúng giờ, giá chuẩn)"
            ], key=f"truck_{order['ID']}")
            
            if st.button(f"🚀 Bắt đầu giao hàng đến Nhà máy ({order['ID']})"):
                order["Trạng thái"] = "Đang giao đến Nhà máy"
                order["Loại_Xe"] = truck_type
                st.success("Đã book xe thành công! Hàng đang trên đường đi.")
                st.rerun()

# =====================================================
# VAI TRÒ 3: NÔNG DÂN (ZALO MINI APP)
# =====================================================
elif role == "🌾 Nông dân (Zalo Mini App)":
    st.header("Tin Nhắn Thu Mua Từ Đại Lý")
    
    broadcasted_orders = [o for o in st.session_state.orders if o.get("Broadcast_Zalo") == True and o["Trạng thái"] == "Đại lý đang gom"]
    
    if not broadcasted_orders:
        st.write("Hiện chưa có Đại lý nào tìm rơm quanh bạn.")
        
    for order in broadcasted_orders:
        st.markdown(f"""
        <div class="farmer-card">
            <h4>🔔 Đại lý đang cần gấp {order['Sản phẩm']}</h4>
            <p>Bà con có rơm vui lòng bấm đăng ký để bán ngay!</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form(f"form_farmer_{order['ID']}"):
            f_name = st.text_input("Tên của bạn", "Chú Ba Thắng")
            f_address = st.text_input("Địa chỉ ruộng", "Xã Vĩnh Bình, Hòa Bình")
            f_weight = st.number_input("Khối lượng có thể cung cấp (Tấn)", min_value=1.0, step=0.5)
            f_method = st.radio("Phương thức giao nhận:", ["Đại lý lại gom", "Tự đem lại Hub"])
            
            if st.form_submit_button("Xác nhận Bán"):
                st.session_state.farmer_offers.append({
                    "ID": f"FM{random.randint(1000,9999)}", "Order_ID": order["ID"],
                    "Tên": f_name, "Địa chỉ": f_address, "Khối lượng": f_weight,
                    "Phương thức": f_method, "Trạng thái": "Chờ xử lý"
                })
                st.success("Đã gửi thông tin cho Đại lý thành công! Vui lòng đợi Đại lý xác nhận.")
