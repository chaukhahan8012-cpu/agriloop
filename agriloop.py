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
    .driver-card { border-left: 4px solid #00b14f; padding: 15px; background: #e8f5e9; margin-bottom: 10px; border-radius: 5px;}
    .metric-card { background-color: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }
    </style>
""", unsafe_allow_html=True)

# ==========================
# BẢNG GIÁ & PHÍ NIÊM YẾT
# ==========================
PRICES = {"Rơm cuộn": 850000, "Rơm rời": 600000}
SHIPPING_RATE_PER_TON = 200000 
PLATFORM_FEE_RATE = 0.05       

# ==========================
# KHỞI TẠO MOCK DATA
# ==========================
if "orders" not in st.session_state:
    st.session_state.orders = [
        {"ID": "AL001", "Nhà máy": "NM Điện Sinh Khối Cần Thơ", "Địa chỉ": "Ô Môn, Cần Thơ", "Sản phẩm": "Rơm cuộn", "Khối lượng": 120.0, "Deadline": "2026-03-01", "Trạng thái": "Hoàn tất", "Tổng tiền": 132300000, "Phí sàn": 6300000, "Đã gom": 120.0, "Tiền cọc": 39690000},
        {"ID": "AL002", "Nhà máy": "NM Phân Bón Sóc Trăng", "Địa chỉ": "KCN An Nghiệp, Sóc Trăng", "Sản phẩm": "Rơm rời", "Khối lượng": 80.5, "Deadline": "2026-03-15", "Trạng thái": "Hoàn tất", "Tổng tiền": 67620000, "Phí sàn": 3220000, "Đã gom": 80.5, "Tiền cọc": 20286000}
    ]
if "farmer_offers" not in st.session_state:
    st.session_state.farmer_offers = [] 
if "agent_points" not in st.session_state:
    st.session_state.agent_points = 1350 

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
        "🌾 Nông dân (Zalo Mini App)",
        "🚛 Tài xế (Chặng ngắn & Dài)",
        "👑 Admin (Tổng quan & Phân tích)"
    ]
)

st.title(f"{role}")

# =====================================================
# VAI TRÒ 1: NHÀ MÁY
# =====================================================
if role == "🏭 Nhà máy":
    st.header("1. Tạo Lệnh Thu Mua")
    with st.form("factory_order"):
        col1, col2 = st.columns(2)
        factory_name = col1.text_input("Tên Nhà máy", "NM Điện Sinh Khối Hậu Giang")
        address = col2.text_input("Địa chỉ giao hàng", "KCN Sông Hậu, Hậu Giang")
        
        col3, col4, col5 = st.columns(3)
        product = col3.selectbox("Loại phụ phẩm", ["Rơm cuộn", "Rơm rời"])
        weight = col4.number_input("Khối lượng cần mua (Tấn)", min_value=1.0, value=50.0, step=0.5, format="%.1f")
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
        
        if st.form_submit_button("Xác nhận & Xuất mã QR Cọc"):
            new_id = f"AL{len(st.session_state.orders)+1:03}"
            st.session_state.orders.append({
                "ID": new_id, "Nhà máy": factory_name, "Địa chỉ": address,
                "Sản phẩm": product, "Khối lượng": weight, "Deadline": str(deadline),
                "Trạng thái": "Chờ quét QR Cọc", "Tổng tiền": total_cost, "Phí sàn": platform_fee,
                "Đã gom": 0.0, "Tiền cọc": deposit_amount
            })
            st.success("Đã tạo đơn. Vui lòng thanh toán cọc bên dưới!")
            st.rerun()

    pending_delivery = [o for o in st.session_state.orders if o["Trạng thái"] in ["Chờ quét QR Cọc", "Đang giao đến Nhà máy"]]
    if pending_delivery:
        st.header("2. Xử lý Đơn hàng hiện tại")
        for order in pending_delivery:
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
            elif order["Trạng thái"] == "Đang giao đến Nhà máy":
                st.warning(f"🚛 Đơn {order['ID']} ({order['Khối lượng']} Tấn) đang trên đường đến nhà máy!")
                if st.button(f"✅ Xác nhận đã nhận hàng & Quyết toán ({order['ID']})"):
                    order["Trạng thái"] = "Hoàn tất"
                    st.success("Giao dịch hoàn tất!")
                    st.rerun()

# =====================================================
# VAI TRÒ 2: ĐẠI LÝ (HUB & ĐIỀU PHỐI)
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
    active_orders = [o for o in st.session_state.orders if o["Trạng thái"] in ["Đại lý đang gom", "Chờ xe chặng dài"]]
    
    for order in active_orders:
        st.subheader(f"📦 Đơn {order['ID']} - {order['Nhà máy']}")
        progress_pct = min(order['Đã gom'] / order['Khối lượng'], 1.0)
        st.progress(progress_pct, text=f"Đã gom {order['Đã gom']}/{order['Khối lượng']} Tấn")
        
        if order["Trạng thái"] == "Đại lý đang gom":
            if st.button(f"📢 Phát tín hiệu tìm rơm qua Zalo cho Nông dân ({order['ID']})"):
                order["Broadcast_Zalo"] = True
                st.toast("Đã gửi tin nhắn Zalo hàng loạt!")
                
            offers = [f for f in st.session_state.farmer_offers if f["Order_ID"] == order["ID"]]
            if offers:
                for offer in offers:
                    if offer["Trạng thái"] == "Chờ xử lý":
                        with st.container(border=True):
                            st.write(f"🧑‍🌾 **{offer['Tên']}** - Cung cấp: **{offer['Khối lượng']} Tấn**")
                            if offer['Phương thức'] == "Đại lý lại gom":
                                if st.button(f"📡 Phát lệnh tìm Tài xế chặng ngắn đi gom ({offer['ID']})"):
                                    offer["Trạng thái"] = "Chờ Tài xế chặng ngắn"
                                    st.toast("Đã đẩy cuốc xe lên App Tài xế Zalo!")
                                    st.rerun()
                            else:
                                if st.button(f"👉 Xác nhận Nông dân đã tự chở tới Hub ({offer['ID']})"):
                                    offer["Trạng thái"] = "Đã nhập kho"
                                    order["Đã gom"] += offer["Khối lượng"]
                                    st.rerun()
                    elif offer["Trạng thái"] == "Chờ Tài xế chặng ngắn":
                        st.info(f"⏳ Đang chờ tài xế nhận cuốc lấy hàng của {offer['Tên']}...")
                    elif offer["Trạng thái"] == "Tài xế đang đi gom":
                        st.warning(f"🚜 Tài xế đang trên đường chở {offer['Khối lượng']} tấn của {offer['Tên']} về Hub.")
            
            # Khi gom đủ hàng, kích hoạt chặng dài
            if order['Đã gom'] >= order['Khối lượng']:
                st.markdown(f"""
                <div class="transport-box">
                    <h4 style="color: #1976d2;">✅ Kho đã đầy - Sẵn sàng giao cho Nhà máy</h4>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"🚀 Đăng tìm xe tải Chặng Dài ({order['ID']})"):
                    order["Trạng thái"] = "Chờ xe chặng dài"
                    st.success("Đã đăng tải yêu cầu lên Sàn Vận Tải AgriLoop!")
                    st.rerun()
                    
        elif order["Trạng thái"] == "Chờ xe chặng dài":
            st.info("⏳ Đang đợi xe tải lớn nhận chuyến trên hệ thống...")

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
        </div>
        """, unsafe_allow_html=True)
        
        with st.form(f"form_farmer_{order['ID']}"):
            f_name = st.text_input("Tên của bạn", "Chú Ba Thắng")
            f_address = st.text_input("Địa chỉ ruộng", "Xã Vĩnh Bình, Hòa Bình")
            f_weight = st.number_input("Nhập số lượng rơm bạn có (Tấn):", min_value=0.1, value=5.0, step=0.5, format="%.1f")
            f_method = st.radio("Phương thức giao nhận:", ["Đại lý lại gom", "Tự đem lại Hub"])
            
            if st.form_submit_button("Xác nhận Bán"):
                st.session_state.farmer_offers.append({
                    "ID": f"FM{random.randint(1000,9999)}", "Order_ID": order["ID"],
                    "Tên": f_name, "Địa chỉ": f_address, "Khối lượng": f_weight,
                    "Phương thức": f_method, "Trạng thái": "Chờ xử lý"
                })
                st.success("Đã gửi thông tin cho Đại lý thành công!")

# =====================================================
# VAI TRÒ 4: TÀI XẾ (CHẶNG NGẮN & CHẶNG DÀI)
# =====================================================
elif role == "🚛 Tài xế (Chặng ngắn & Dài)":
    st.header("Ứng Dụng Tài Xế AgriLoop")
    
    driver_type = st.radio("Chọn không gian làm việc:", ["🚜 Chặng ngắn (Xe ba gác/Máy cày địa phương)", "🚛 Chặng dài (Xe tải lớn/Container)"])
    
    if "Chặng ngắn" in driver_type:
        st.subheader("Trạm Nhận Cuốc (Zalo Mini App)")
        is_active = st.toggle("🟢 Bật nhận cuốc (Online)", value=True)
        
        if is_active:
            # Lọc các cuốc xe chặng ngắn (Đại lý đã phát lệnh)
            short_haul_trips = [f for f in st.session_state.farmer_offers if f["Trạng thái"] in ["Chờ Tài xế chặng ngắn", "Tài xế đang đi gom"]]
            
            if not short_haul_trips:
                st.info("Hiện chưa có cuốc thu gom nào quanh khu vực của bạn.")
                
            for trip in short_haul_trips:
                st.markdown(f"""
                <div class="driver-card">
                    <h4>📍 Cuốc xe: Gom {trip['Khối lượng']} Tấn Rơm</h4>
                    <p><b>Nhận tại:</b> Ruộng {trip['Tên']} ({trip['Địa chỉ']})</p>
                    <p><b>Giao đến:</b> Hub Đại lý gần nhất</p>
                </div>
                """, unsafe_allow_html=True)
                
                if trip["Trạng thái"] == "Chờ Tài xế chặng ngắn":
                    if st.button(f"✅ Nhận cuốc này ({trip['ID']})"):
                        trip["Trạng thái"] = "Tài xế đang đi gom"
                        st.toast("Nhận cuốc thành công! Chạy tới ruộng nông dân ngay nhé.")
                        st.rerun()
                elif trip["Trạng thái"] == "Tài xế đang đi gom":
                    if st.button(f"🏁 Xác nhận đã hạ tải tại Hub Đại lý ({trip['ID']})"):
                        trip["Trạng thái"] = "Đã nhập kho"
                        # Cập nhật số lượng cho Order tổng của Đại lý
                        for o in st.session_state.orders:
                            if o["ID"] == trip["Order_ID"]:
                                o["Đã gom"] += trip["Khối lượng"]
                        st.success("Tuyệt vời! Thu nhập đã được cộng vào ví của bạn.")
                        st.rerun()
        else:
            st.warning("🔴 Bạn đang ở trạng thái Tạm nghỉ. Bật Online để nhận thông báo cuốc xe.")
            
    else:
        st.subheader("Sàn Vận Tải Chặng Dài (Middle-Mile)")
        truck_profile = st.selectbox("Hồ sơ xe của bạn:", ["🥇 Xe tải rỗng chiều về (Ưu tiên khớp lệnh)", "🥈 Xe đối tác 3PL (Hợp đồng)", "🥉 Xe cá nhân tự do"])
        
        long_haul_orders = [o for o in st.session_state.orders if o["Trạng thái"] == "Chờ xe chặng dài"]
        
        if not long_haul_orders:
            st.info("Hiện không có đơn hàng nào cần xe tải lớn.")
            
        for order in long_haul_orders:
            with st.container(border=True):
                st.write(f"📦 **Đơn hàng {order['ID']}** - {order['Khối lượng']} Tấn {order['Sản phẩm']}")
                st.write(f"📍 **Lộ trình:** Hub Đại lý ➡️ {order['Nhà máy']} ({order['Địa chỉ']})")
                
                if st.button(f"🚛 Nhận chuyến giao hàng ({order['ID']})"):
                    order["Trạng thái"] = "Đang giao đến Nhà máy"
                    order["Loại_Xe"] = truck_profile # Lưu lại lịch sử loại xe đã book
                    st.success("Đã nhận chuyến! Mời bác tài đánh xe đến Hub lấy hàng.")
                    st.rerun()

# =====================================================
# VAI TRÒ 5: ADMIN (TỔNG QUAN & PHÂN TÍCH)
# =====================================================
elif role == "👑 Admin (Tổng quan & Phân tích)":
    st.header("Trạm Điều Hành Trung Tâm AgriLoop")
    
    completed_orders = [o for o in st.session_state.orders if o.get("Trạng thái") == "Hoàn tất"]
    total_revenue = sum(o.get("Tổng tiền", 0) for o in completed_orders)
    total_platform_fee = sum(o.get("Phí sàn", 0) for o in completed_orders)
    total_volume = sum(o.get("Khối lượng", 0) for o in completed_orders)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tổng Doanh Thu Giao Dịch", f"{total_revenue / 1000000:,.1f} Tr")
    col2.metric("Doanh Thu Sàn (5%)", f"{total_platform_fee / 1000000:,.1f} Tr", "+12%")
    col3.metric("Tổng Sản Lượng Rơm", f"{total_volume} Tấn")
    col4.metric("Đối tác hoạt động", "12 Hub | 45 NM")

    st.markdown("---")
    col_map, col_chart = st.columns([1, 1])
    
    with col_map:
        st.subheader("📍 Bản đồ Mạng lưới Đối tác ĐBSCL")
        map_data = pd.DataFrame({
            'lat': [10.0451, 9.7803, 9.6000, 9.2941], 
            'lon': [105.7468, 105.4746, 105.9750, 105.7278]
        })
        st.map(map_data)
        
    with col_chart:
        st.subheader("📊 Phân tích Tỷ trọng Sản phẩm")
        if completed_orders:
            df_chart = pd.DataFrame(completed_orders)
            if "Sản phẩm" in df_chart.columns and "Khối lượng" in df_chart.columns:
                chart_data = df_chart.groupby("Sản phẩm")["Khối lượng"].sum()
                st.bar_chart(chart_data) 
        else:
            st.info("Chưa đủ dữ liệu hoàn tất để vẽ biểu đồ.")

    st.markdown("---")
    st.subheader("📜 Sổ Cái Lịch Sử Giao Dịch (Ledger Toàn Hệ Thống)")
    if st.session_state.orders:
        df_all = pd.DataFrame(st.session_state.orders)
        desired_cols = ["ID", "Nhà máy", "Sản phẩm", "Khối lượng", "Trạng thái", "Tổng tiền", "Phí sàn", "Đã gom", "Loại_Xe"]
        existing_cols = [col for col in desired_cols if col in df_all.columns]
        st.dataframe(df_all[existing_cols], use_container_width=True)
    else:
        st.write("Hệ thống chưa có giao dịch.")
