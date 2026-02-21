import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="AgriLoop - Diamond System", layout="wide", page_icon="🌾")

# ==========================
# CẤU HÌNH CSS
# ==========================
st.markdown("""
    <style>
    .invoice-box { background-color: #f1f8e9; padding: 20px; border-radius: 10px; border: 1px solid #c5e1a5; margin-bottom: 20px; }
    .status-badge { background-color: #e0f2f1; padding: 5px 10px; border-radius: 15px; font-weight: bold; color: #00695c; }
    .farmer-card { border-left: 4px solid #ff9800; padding: 15px; background: #fff8e1; margin-bottom: 10px; border-radius: 5px;}
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
# KHỞI TẠO SESSION STATE (DATABASE GIẢ LẬP)
# ==========================
if "orders" not in st.session_state:
    st.session_state.orders = []
if "farmer_offers" not in st.session_state:
    st.session_state.farmer_offers = [] # Chứa các phản hồi của nông dân
if "agent_points" not in st.session_state:
    st.session_state.agent_points = 1250 # Điểm tích lũy giả lập của Đại lý

# ==========================
# SIDEBAR QUẢN LÝ VAI TRÒ
# ==========================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2664/2664552.png", width=80)
st.sidebar.title("AgriLoop Ecosystem")
role = st.sidebar.radio(
    "Đăng nhập với vai trò:",
    [
        "🏭 Nhà máy", 
        "🏪 Đại lý (Hub)", 
        "🌾 Nông dân (Zalo Mini App)", 
        "🚜 Vận tải chặng ngắn", 
        "🚛 Vận tải chặng dài"
    ]
)

st.title(f"{role}")

# =====================================================
# VAI TRÒ 1: NHÀ MÁY
# =====================================================
if role == "🏭 Nhà máy":
    st.header("Tạo Lệnh Thu Mua & Đặt Cọc")
    
    with st.form("factory_order"):
        col1, col2 = st.columns(2)
        factory_name = col1.text_input("Tên Nhà máy", "NM Điện Sinh Khối Hậu Giang")
        address = col2.text_input("Địa chỉ giao hàng", "KCN Sông Hậu, Hậu Giang")
        
        col3, col4, col5 = st.columns(3)
        product = col3.selectbox("Loại phụ phẩm (AgriLoop niêm yết)", ["Rơm cuộn", "Rơm rời"])
        weight = col4.number_input("Khối lượng cần mua (Tấn)", min_value=10, value=50)
        deadline = col5.date_input("Hạn chót nhận hàng")
        
        # Hệ thống tự động tính toán minh bạch
        base_cost = weight * PRICES[product]
        shipping_est = weight * SHIPPING_RATE_PER_TON
        subtotal = base_cost + shipping_est
        platform_fee = subtotal * PLATFORM_FEE_RATE
        total_cost = subtotal + platform_fee
        deposit_amount = total_cost * 0.3 # Cọc 30%
        
        st.markdown(f"""
        <div class="invoice-box">
            <h4>🧾 Hóa đơn Tạm tính (Hệ thống định giá)</h4>
            <p>- <b>Tiền rơm ({PRICES[product]:,.0f} đ/tấn):</b> {base_cost:,.0f} đ</p>
            <p>- <b>Phí vận chuyển dự kiến:</b> {shipping_est:,.0f} đ</p>
            <p>- <b>Phí nền tảng (5%):</b> {platform_fee:,.0f} đ</p>
            <hr>
            <h3 style="color: #2e7d32;">Tổng thanh toán: {total_cost:,.0f} đ</h3>
            <p style="color: #d32f2f; font-weight: bold;">⚠️ Yêu cầu thanh toán cọc 30%: {deposit_amount:,.0f} đ</p>
        </div>
        """, unsafe_allow_html=True)
        
        submitted = st.form_submit_button("Xác nhận & Chuyển sang thanh toán cọc")
        
        if submitted:
            new_id = f"AL{len(st.session_state.orders)+1:03}"
            st.session_state.orders.append({
                "ID": new_id, "Nhà máy": factory_name, "Địa chỉ": address,
                "Sản phẩm": product, "Khối lượng": weight, "Deadline": str(deadline),
                "Trạng thái": "Chờ quét QR Cọc", "Tổng tiền": total_cost, 
                "Đã gom": 0, "Tiền cọc": deposit_amount
            })
            st.success("Đã tạo đơn. Vui lòng thanh toán cọc bên dưới!")
            st.rerun()

    # Hiển thị QR cọc cho các đơn vừa tạo
    for order in st.session_state.orders:
        if order["Trạng thái"] == "Chờ quét QR Cọc":
            st.markdown("---")
            col_qr, col_info = st.columns([1, 2])
            with col_qr:
                # Hình QR giả lập
                st.image("https://upload.wikimedia.org/wikipedia/commons/d/d0/QR_code_for_mobile_English_Wikipedia.svg", width=150)
            with col_info:
                st.subheader(f"Thanh toán cọc cho Đơn {order['ID']}")
                st.write(f"Số tiền: **{order['Tiền cọc']:,.0f} VNĐ**")
                if st.button(f"Mô phỏng: Đã quét QR & Thanh toán {order['ID']}"):
                    order["Trạng thái"] = "Sẵn sàng cho Đại lý"
                    st.rerun()

# =====================================================
# VAI TRÒ 2: ĐẠI LÝ (HUB)
# =====================================================
elif role == "🏪 Đại lý (Hub)":
    # 1. Dashboard Điểm & Lịch sử
    st.sidebar.markdown("---")
    st.sidebar.metric("🌟 Điểm tích lũy", f"{st.session_state.agent_points} pt", "+50 pt")
    st.sidebar.caption("Hạng: Đại lý Kim Cương 💎 (Ưu tiên hiển thị đơn)")
    
    st.header("Chợ Lệnh Thu Mua Từ Nhà Máy")
    available_orders = [o for o in st.session_state.orders if o["Trạng thái"] == "Sẵn sàng cho Đại lý"]
    if not available_orders:
        st.info("Hiện không có đơn mới từ Nhà máy khu vực của bạn.")
        
    for order in available_orders:
        with st.container(border=True):
            st.write(f"🏭 **{order['Nhà máy']}** cần **{order['Khối lượng']} Tấn {order['Sản phẩm']}**")
            st.write(f"📍 Giao đến: {order['Địa chỉ']}")
            if st.button(f"Nhận đơn {order['ID']} & Tích 50 điểm"):
                order["Trạng thái"] = "Đại lý đang gom"
                st.session_state.agent_points += 50
                st.rerun()

    st.markdown("---")
    st.header("Quản Lý Thu Gom (Giao việc cho Nông dân)")
    active_orders = [o for o in st.session_state.orders if o["Trạng thái"] == "Đại lý đang gom"]
    
    for order in active_orders:
        st.subheader(f"📦 Đơn {order['ID']} - Tiến độ thu gom")
        progress_pct = min(order['Đã gom'] / order['Khối lượng'], 1.0)
        st.progress(progress_pct, text=f"Đã gom {order['Đã gom']}/{order['Khối lượng']} Tấn")
        
        # Gửi Zalo Broadcast
        if st.button(f"📢 Phát tín hiệu thu mua qua Zalo Mini App cho Đơn {order['ID']}"):
            order["Broadcast_Zalo"] = True
            st.toast("Đã gửi tin nhắn Zalo hàng loạt đến 50 nông dân quanh bán kính 5km!")
            
        # Hiển thị phản hồi từ Nông dân
        offers = [f for f in st.session_state.farmer_offers if f["Order_ID"] == order["ID"]]
        if offers:
            st.write("**Phản hồi từ Nông dân:**")
            for offer in offers:
                if offer["Trạng thái"] == "Chờ xử lý":
                    with st.container(border=True):
                        st.write(f"🧑‍🌾 **{offer['Tên']}** - 📍 {offer['Địa chỉ']}")
                        st.write(f"Cung cấp: **{offer['Khối lượng']} Tấn** | Phương thức: **{offer['Phương thức']}**")
                        
                        col_btn1, col_btn2 = st.columns(2)
                        if offer['Phương thức'] == "Đại lý lại gom":
                            if col_btn1.button(f"🚜 Đặt xe Ba Gác đi gom ({offer['ID']})"):
                                offer["Trạng thái"] = "Đang điều xe chặng ngắn"
                                st.toast("Đã đẩy lệnh cho tài xế Ba gác địa phương!")
                                st.rerun()
                        else: # Nông dân tự chở lại
                            if col_btn1.button(f"✅ Xác nhận đã nhập kho ({offer['ID']})"):
                                offer["Trạng thái"] = "Đã nhập kho"
                                order["Đã gom"] += offer["Khối lượng"]
                                st.rerun()
                elif offer["Trạng thái"] == "Đã nhập kho":
                    st.success(f"🧑‍🌾 {offer['Tên']}: Đã thu {offer['Khối lượng']} tấn (Lưu kho)")
        
        # Kích hoạt chặng dài khi đủ hàng
        if order['Đã gom'] >= order['Khối lượng']:
            st.success("🎉 Đã gom đủ số lượng yêu cầu của Nhà máy!")
            if st.button(f"🚛 Xác nhận Đủ rơm & Đặt xe tải chặng dài ({order['ID']})"):
                order["Trạng thái"] = "Chờ xe chặng dài"
                st.rerun()

# =====================================================
# VAI TRÒ 3: NÔNG DÂN (ZALO MINI APP)
# =====================================================
elif role == "🌾 Nông dân (Zalo Mini App)":
    st.header("Tin Nhắn Thu Mua Từ Đại Lý")
    
    # Tìm các đơn Đại lý đã bấm "Phát tín hiệu"
    broadcasted_orders = [o for o in st.session_state.orders if o.get("Broadcast_Zalo") == True and o["Trạng thái"] == "Đại lý đang gom"]
    
    if not broadcasted_orders:
        st.write("Hiện chưa có Đại lý nào gửi thông báo thu mua.")
        
    for order in broadcasted_orders:
        st.markdown(f"""
        <div class="farmer-card">
            <h4>🔔 Thông báo: Đại lý đang cần gấp {order['Sản phẩm']}</h4>
            <p>Bà con có rơm vui lòng đăng ký để xuất bán ngay hôm nay!</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form(f"form_farmer_{order['ID']}"):
            f_name = st.text_input("Tên của bạn", "Chú Ba Thắng")
            f_address = st.text_input("Địa chỉ ruộng", "Xã Vĩnh Bình, Hòa Bình")
            f_weight = st.number_input("Khối lượng có thể bán (Tấn)", min_value=1.0, step=0.5)
            f_method = st.radio("Phương thức giao nhận:", ["Đại lý lại gom", "Tự đem lại Hub"])
            
            if st.form_submit_button("Xác nhận Bán"):
                st.session_state.farmer_offers.append({
                    "ID": f"FM{random.randint(1000,9999)}", "Order_ID": order["ID"],
                    "Tên": f_name, "Địa chỉ": f_address, "Khối lượng": f_weight,
                    "Phương thức": f_method, "Trạng thái": "Chờ xử lý"
                })
                st.success("Đã gửi thông tin cho Đại lý thành công!")

# =====================================================
# VAI TRÒ 4: VẬN TẢI CHẶNG NGẮN
# =====================================================
elif role == "🚜 Vận tải chặng ngắn":
    st.header("Cuốc Xe Ba Gác / Máy Cày")
    
    trips = [f for f in st.session_state.farmer_offers if f["Trạng thái"] == "Đang điều xe chặng ngắn"]
    if not trips:
        st.info("Chưa có lệnh gom hàng nào tại ruộng.")
        
    for trip in trips:
        with st.container(border=True):
            st.write(f"📍 **Điểm lấy hàng:** Ruộng {trip['Tên']} ({trip['Địa chỉ']})")
            st.write(f"📦 **Hàng hóa:** {trip['Khối lượng']} Tấn Rơm")
            if st.button(f"Đã gom xong & Hạ tải tại Hub Đại lý ({trip['ID']})"):
                trip["Trạng thái"] = "Đã nhập kho"
                # Cập nhật số lượng kho cho order tương ứng
                for o in st.session_state.orders:
                    if o["ID"] == trip["Order_ID"]:
                        o["Đã gom"] += trip["Khối lượng"]
                st.success("Đã hoàn thành cuốc chặng ngắn!")
                st.rerun()

# =====================================================
# VAI TRÒ 5: VẬN TẢI CHẶNG DÀI
# =====================================================
elif role == "🚛 Vận tải chặng dài":
    st.header("Sàn Điều Xe Tải Giao Nhà Máy")
    
    ready_orders = [o for o in st.session_state.orders if o["Trạng thái"] == "Chờ xe chặng dài"]
    if not ready_orders:
        st.info("Các Hub đang thu gom, chưa có hàng sẵn sàng lên xe.")
        
    for order in ready_orders:
        with st.container(border=True):
            st.subheader(f"Chuyến hàng {order['ID']}")
            st.write(f"📦 Khối lượng: {order['Khối lượng']} Tấn {order['Sản phẩm']}")
            st.write(f"🏭 Trả hàng tại: {order['Nhà máy']} ({order['Địa chỉ']})")
            
            if st.button(f"Nhận chuyến ({order['ID']})"):
                order["Trạng thái"] = "Đang giao đến Nhà máy"
                st.toast("Nhận chuyến thành công! Khởi hành thôi.")
                st.rerun()
