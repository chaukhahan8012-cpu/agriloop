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
    .invoice-final { background-color: #ffffff; padding: 20px; border-radius: 5px; border: 1px dashed #757575; border-left: 5px solid #1976d2;}
    .farmer-card { border-left: 4px solid #ff9800; padding: 15px; background: #fff8e1; margin-bottom: 10px; border-radius: 5px;}
    .transport-box { border: 2px dashed #1976d2; padding: 15px; background-color: #e3f2fd; border-radius: 8px; margin-top: 15px;}
    .driver-card { border-left: 4px solid #00b14f; padding: 15px; background: #e8f5e9; margin-bottom: 10px; border-radius: 5px;}
    .metric-card { background-color: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }
    .login-container { max-width: 500px; margin: 0 auto; padding: 30px; background-color: white; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); border-top: 5px solid #2e7d32; }
    .timeline-container { border-left: 3px solid #4caf50; padding-left: 20px; margin-left: 10px; }
    .timeline-item { margin-bottom: 15px; position: relative; }
    .timeline-item::before { content: ''; position: absolute; left: -27.5px; top: 5px; width: 12px; height: 12px; border-radius: 50%; background-color: #4caf50; }
    .timeline-item.past::before { background-color: #bdbdbd; }
    .timeline-item.past { border-left-color: #bdbdbd; color: gray; }
    </style>
""", unsafe_allow_html=True)

# ==========================
# KHỞI TẠO CẤU HÌNH HỆ THỐNG (SYSTEM CONFIG)
# ==========================
if "system_config" not in st.session_state:
    st.session_state.system_config = {
        "price_rom_cuon": 850000,
        "price_rom_roi": 600000,
        "shipping_short_per_ton": 120000,
        "shipping_long_per_ton": 200000,
        "platform_fee_rate": 0.05
    }

# ==========================
# KHỞI TẠO MOCK DATA & SESSION STATE
# ==========================
if "orders" not in st.session_state:
    st.session_state.orders = []
if "farmer_offers" not in st.session_state:
    st.session_state.farmer_offers = [] 
if "agent_points" not in st.session_state:
    st.session_state.agent_points = 1350 

# TRẠNG THÁI ĐĂNG NHẬP
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False
    st.session_state.current_role = ""
    st.session_state.username = ""
    st.session_state.agent_address = ""

def logout():
    st.session_state.is_logged_in = False
    st.session_state.current_role = ""
    st.session_state.username = ""
    st.session_state.agent_address = ""

# =====================================================
# MÀN HÌNH ĐĂNG NHẬP (LOGIN PAGE)
# =====================================================
if not st.session_state.is_logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="login-container">
            <h2 style="text-align: center; color: #2e7d32;">🌾 AgriLoop System</h2>
            <p style="text-align: center; color: gray;">Nền tảng Logistics Nông nghiệp Tuần hoàn</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Tên đăng nhập (Demo: nhập bất kỳ)")
            password = st.text_input("Mật khẩu", type="password")
            
            # TÁCH RÕ 2 LUỒNG TÀI XẾ Ở ĐÂY
            role_select = st.selectbox("Chọn vai trò của bạn:", 
                ["🏭 Nhà máy", "🏪 Đại lý (Hub)", "🌾 Nông dân", "🚜 Tài xế (Chặng ngắn)", "🚛 Tài xế (Chặng dài)", "👑 Admin"]
            )
            
            agent_loc = ""
            if role_select == "🏪 Đại lý (Hub)":
                agent_loc = st.text_input("📍 Nhập địa chỉ Hub của bạn (Huyện, Tỉnh):", placeholder="VD: Vĩnh Châu, Sóc Trăng...")
            
            submit_login = st.form_submit_button("Đăng nhập vào Hệ thống")
            
            if submit_login:
                if username == "":
                    st.error("Vui lòng nhập tên đăng nhập!")
                elif role_select == "🏪 Đại lý (Hub)" and agent_loc == "":
                    st.error("Vui lòng nhập địa chỉ Hub để AgriLoop phân bổ đơn hàng phù hợp!")
                else:
                    st.session_state.is_logged_in = True
                    st.session_state.username = username
                    st.session_state.current_role = role_select
                    if role_select == "🏪 Đại lý (Hub)":
                        st.session_state.agent_address = agent_loc
                    st.rerun()

# =====================================================
# GIAO DIỆN CHÍNH (SAU KHI ĐĂNG NHẬP)
# =====================================================
else:
    role = st.session_state.current_role
    cfg = st.session_state.system_config
    
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2664/2664552.png", width=80)
    st.sidebar.title("AgriLoop MVP")
    st.sidebar.markdown(f"**👤 Xin chào:** {st.session_state.username}")
    st.sidebar.markdown(f"**💼 Vai trò:** {role}")
    
    if role == "🏪 Đại lý (Hub)":
        st.sidebar.markdown(f"**📍 Vị trí Hub:** {st.session_state.agent_address}")
        
    st.sidebar.markdown("---")
    st.sidebar.button("🚪 Đăng xuất", on_click=logout)

    st.title(f"{role}")

    # =====================================================
    # VAI TRÒ: NHÀ MÁY
    # =====================================================
    if role == "🏭 Nhà máy":
        st.header("1. Tạo Lệnh Thu Mua (Tầng 1: Báo giá dự kiến)")
        with st.form("factory_order"):
            col1, col2 = st.columns(2)
            factory_name = col1.text_input("Tên Nhà máy", st.session_state.username)
            address = col2.text_input("Địa chỉ giao hàng", "KCN Sông Hậu, Hậu Giang")
            
            col3, col4, col5 = st.columns(3)
            product = col3.selectbox("Loại phụ phẩm", ["Rơm cuộn", "Rơm rời"])
            weight = col4.number_input("Khối lượng cần mua (Tấn)", min_value=1.0, value=50.0, step=0.5, format="%.1f")
            deadline = col5.date_input("Hạn chót nhận hàng")
            
            base_price = cfg["price_rom_cuon"] if product == "Rơm cuộn" else cfg["price_rom_roi"]
            base_cost = weight * base_price
            shipping_est = weight * (cfg["shipping_short_per_ton"] + cfg["shipping_long_per_ton"])
            subtotal = base_cost + shipping_est
            platform_fee = subtotal * cfg["platform_fee_rate"]
            total_est = subtotal + platform_fee
            deposit_amount = total_est * 0.3 
            
            st.markdown(f"""
            <div class="invoice-box">
                <h4>🧾 Hóa đơn Dự kiến (Tạm tính theo trung bình hệ thống)</h4>
                <p>- <b>Tiền rơm ({base_price:,.0f} đ/tấn):</b> {base_cost:,.0f} đ</p>
                <p>- <b>Phí vận chuyển dự kiến (Ngắn + Dài):</b> {shipping_est:,.0f} đ</p>
                <p>- <b>Phí sàn AgriLoop ({cfg['platform_fee_rate']*100}%):</b> {platform_fee:,.0f} đ</p>
                <hr>
                <h3 style="color: #2e7d32;">Tổng dự kiến: {total_est:,.0f} đ</h3>
                <p style="color: #d32f2f; font-weight: bold;">⚠️ Yêu cầu thanh toán cọc 30%: {deposit_amount:,.0f} đ</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.form_submit_button("Xác nhận & Xuất mã QR Cọc"):
                new_id = f"AL{len(st.session_state.orders)+1:03}"
                st.session_state.orders.append({
                    "ID": new_id, "Nhà máy": factory_name, "Địa chỉ": address,
                    "Sản phẩm": product, "Khối lượng": weight, "Deadline": str(deadline),
                    "Trạng thái": "Chờ quét QR Cọc", "Tổng_Dự_Kiến": total_est, "Tiền_Cọc": deposit_amount,
                    "Chi_Phi_Rơm": base_cost, "Chi_Phi_Chặng_Ngắn": 0.0, "Chi_Phi_Chặng_Dài": 0.0,
                    "Đã_Gom": 0.0, "Đã_Đánh_Giá": False, "Hub_Location": "Chưa có"
                })
                st.success("Đã tạo đơn. Vui lòng thanh toán cọc bên dưới!")
                st.rerun()

        pending_delivery = [o for o in st.session_state.orders if o["Trạng thái"] in ["Chờ quét QR Cọc", "Đang giao đến Nhà máy"]]
        if pending_delivery:
            st.header("2. Theo dõi Đơn hàng & Quyết toán (Tầng 2)")
            for order in pending_delivery:
                if order["Trạng thái"] == "Chờ quét QR Cọc":
                    st.markdown("---")
                    col_qr, col_info = st.columns([1, 2])
                    with col_qr:
                        st.image("https://upload.wikimedia.org/wikipedia/commons/d/d0/QR_code_for_mobile_English_Wikipedia.svg", width=150)
                    with col_info:
                        st.subheader(f"Thanh toán cọc Đơn {order['ID']}")
                        if st.button(f"Mô phỏng: Đã thanh toán {order['Tiền_Cọc']:,.0f} VNĐ ({order['ID']})"):
                            order["Trạng thái"] = "Sẵn sàng cho Đại lý"
                            st.rerun()
                
                elif order["Trạng thái"] == "Đang giao đến Nhà máy":
                    with st.expander(f"📍 Lộ trình & Quyết toán thực tế đơn {order['ID']}", expanded=True):
                        st.warning(f"🚛 Đơn hàng {order['Khối lượng']} Tấn đang trên đường đến {order['Địa chỉ']}!")
                        
                        actual_shipping = order['Chi_Phi_Chặng_Ngắn'] + order['Chi_Phi_Chặng_Dài']
                        actual_subtotal = order['Chi_Phi_Rơm'] + actual_shipping
                        actual_platform_fee = actual_subtotal * cfg["platform_fee_rate"]
                        actual_total = actual_subtotal + actual_platform_fee
                        diff = actual_total - order['Tổng_Dự_Kiến']
                        
                        col_timeline, col_bill = st.columns([1, 1.2])
                        
                        with col_timeline:
                            st.markdown("### Lộ trình vận chuyển")
                            st.markdown(f"""
                            <div class="timeline-container">
                                <div class="timeline-item"><b>Đang giao hàng</b><br>Dự kiến giao trong 45 phút nữa.</div>
                                <div class="timeline-item past"><b>Đã xuất kho</b><br>Từ Hub {order.get('Hub_Location', 'Đại lý')}.</div>
                                <div class="timeline-item past"><b>Đóng gói hoàn tất</b></div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown("<br>", unsafe_allow_html=True)
                            if st.button(f"✅ ĐÃ NHẬN HÀNG - CHỐT QUYẾT TOÁN ({order['ID']})", use_container_width=True):
                                order["Trạng thái"] = "Hoàn tất"
                                order["Tổng_Thực_Tế"] = actual_total
                                order["Phí_Sàn_Thực_Tế"] = actual_platform_fee
                                st.success("Giao dịch hoàn tất! Hệ thống đang Auto-split dòng tiền.")
                                st.rerun()
                                
                        with col_bill:
                            st.markdown("### 📊 Bảng Quyết Toán Thực Tế")
                            diff_color = "green" if diff <= 0 else "red"
                            diff_text = "Tiết kiệm được" if diff <= 0 else "Phát sinh thêm"
                            
                            st.markdown(f"""
                            <div style="background:#f9f9f9; padding:15px; border-radius:8px; border:1px solid #ddd;">
                                <p><b>Tiền rơm:</b> {order['Chi_Phi_Rơm']:,.0f} đ</p>
                                <p><b>Vận chuyển chặng ngắn (thực tế gom):</b> {order['Chi_Phi_Chặng_Ngắn']:,.0f} đ</p>
                                <p><b>Vận chuyển chặng dài (Loại xe: {order.get('Loại_Xe', 'N/A')}):</b> {order['Chi_Phi_Chặng_Dài']:,.0f} đ</p>
                                <p><b>Phí sàn ({cfg['platform_fee_rate']*100}%):</b> {actual_platform_fee:,.0f} đ</p>
                                <hr>
                                <h4>TỔNG THỰC TẾ: <span style="color:#1976d2;">{actual_total:,.0f} đ</span></h4>
                                <i>(Báo giá dự kiến ban đầu: {order['Tổng_Dự_Kiến']:,.0f} đ)</i><br>
                                <b style="color:{diff_color};">↳ {diff_text}: {abs(diff):,.0f} đ so với dự kiến</b>
                            </div>
                            """, unsafe_allow_html=True)

        st.markdown("---")
        st.header("3. Lịch sử Mua hàng")
        factory_history = [o for o in st.session_state.orders if o["Trạng thái"] == "Hoàn tất"]
        if factory_history:
            df_history = pd.DataFrame(factory_history)
            st.dataframe(df_history[["ID", "Sản phẩm", "Khối lượng", "Tổng_Thực_Tế", "Trạng thái"]], use_container_width=True)
        else:
            st.info("Chưa có giao dịch nào hoàn tất.")

    # =====================================================
    # VAI TRÒ: ĐẠI LÝ
    # =====================================================
    elif role == "🏪 Đại lý (Hub)":
        st.sidebar.metric("🌟 Điểm uy tín (Rating)", f"{st.session_state.agent_points} pt")
        
        st.header(f"Chợ Lệnh Thu Mua (Gợi ý quanh {st.session_state.agent_address})")
        available_orders = [o for o in st.session_state.orders if o["Trạng thái"] == "Sẵn sàng cho Đại lý"]
        
        for order in available_orders:
            with st.container(border=True):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.write(f"🏭 **{order['Nhà máy']}** cần **{order['Khối lượng']} Tấn {order['Sản phẩm']}**")
                    st.caption(f"📍 Giao đến: {order['Địa chỉ']}")
                with col_b:
                    if st.button(f"Nhận thầu đơn {order['ID']}"):
                        order["Trạng thái"] = "Đại lý đang gom"
                        order["Hub_Location"] = st.session_state.agent_address
                        st.rerun()

        st.markdown("---")
        st.header("Trung Tâm Thu Gom & Điều Phối Vận Tải")
        active_orders = [o for o in st.session_state.orders if o["Trạng thái"] in ["Đại lý đang gom", "Chờ xe chặng dài"]]
        
        for order in active_orders:
            st.subheader(f"📦 Đơn {order['ID']} - {order['Nhà máy']}")
            progress_pct = min(order['Đã_Gom'] / order['Khối lượng'], 1.0)
            st.progress(progress_pct, text=f"Đã gom {order['Đã_Gom']}/{order['Khối lượng']} Tấn")
            
            if order["Trạng thái"] == "Đại lý đang gom":
                if st.button(f"📢 Phát tín hiệu tìm rơm qua Zalo ({order['ID']})"):
                    order["Broadcast_Zalo"] = True
                    st.toast("Đã gửi tin nhắn Zalo hàng loạt!")
                    
                offers = [f for f in st.session_state.farmer_offers if f["Order_ID"] == order["ID"]]
                if offers:
                    for offer in offers:
                        if offer["Trạng thái"] == "Chờ xử lý":
                            with st.container(border=True):
                                st.write(f"🧑‍🌾 **{offer['Tên']}** - Cung cấp: **{offer['Khối lượng']} Tấn**")
                                if offer['Phương thức'] == "Đại lý lại gom":
                                    if st.button(f"📡 Phát lệnh tìm Tài xế chặng ngắn ({offer['ID']})"):
                                        offer["Trạng thái"] = "Chờ Tài xế chặng ngắn"
                                        st.rerun()
                                else:
                                    if st.button(f"👉 Xác nhận Nông dân đã tự chở tới Hub ({offer['ID']})"):
                                        offer["Trạng thái"] = "Đã nhập kho"
                                        order["Đã_Gom"] += offer["Khối lượng"]
                                        st.rerun()
                        elif offer["Trạng thái"] == "Chờ Tài xế chặng ngắn":
                            st.info(f"⏳ Đang chờ tài xế lấy hàng của {offer['Tên']}...")
                        elif offer["Trạng thái"] == "Tài xế đang đi gom":
                            st.warning(f"🚜 Tài xế đang chở rơm của {offer['Tên']} về Hub.")
                
                if order['Đã_Gom'] >= order['Khối lượng']:
                    st.success("✅ Kho đã đầy - Đã chốt chi phí chặng ngắn thực tế!")
                    if st.button(f"🚀 Đăng tìm xe tải Chặng Dài ({order['ID']})"):
                        order["Trạng thái"] = "Chờ xe chặng dài"
                        st.rerun()

    # =====================================================
    # VAI TRÒ: NÔNG DÂN
    # =====================================================
    elif role == "🌾 Nông dân":
        st.header("Tin Nhắn Thu Mua Từ Đại Lý")
        broadcasted_orders = [o for o in st.session_state.orders if o.get("Broadcast_Zalo") == True and o["Trạng thái"] == "Đại lý đang gom"]
        
        for order in broadcasted_orders:
            st.markdown(f"<div class='farmer-card'><h4>🔔 Đại lý đang cần gấp {order['Sản phẩm']}</h4></div>", unsafe_allow_html=True)
            with st.form(f"form_farmer_{order['ID']}"):
                f_name = st.text_input("Tên của bạn", st.session_state.username)
                f_address = st.text_input("Địa chỉ ruộng", "Xã Vĩnh Bình")
                f_weight = st.number_input("Nhập số lượng rơm (Tấn):", min_value=0.1, value=5.0, step=0.5, format="%.1f")
                f_method = st.radio("Phương thức giao nhận:", ["Đại lý lại gom", "Tự đem lại Hub"])
                if st.form_submit_button("Xác nhận Bán"):
                    st.session_state.farmer_offers.append({
                        "ID": f"FM{random.randint(1000,9999)}", "Order_ID": order["ID"],
                        "Tên": f_name, "Địa chỉ": f_address, "Khối lượng": f_weight,
                        "Phương thức": f_method, "Trạng thái": "Chờ xử lý"
                    })
                    st.success("Đã gửi thông tin cho Đại lý thành công!")

    # =====================================================
    # VAI TRÒ: TÀI XẾ CHẶNG NGẮN
    # =====================================================
    elif role == "🚜 Chặng ngắn (Xe ba gác/Máy cày)":
        st.subheader("Trạm Nhận Cuốc (Zalo Mini App)")
        is_active = st.toggle("🟢 Bật nhận cuốc (Online)", value=True)
        
        if is_active:
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
                    if st.button(f"🏁 Xác nhận đã hạ tải tại Hub ({trip['ID']})"):
                        trip["Trạng thái"] = "Đã nhập kho"
                        for o in st.session_state.orders:
                            if o["ID"] == trip["Order_ID"]:
                                o["Đã gom"] += trip["Khối lượng"]
                        st.success("Tuyệt vời! Thu nhập đã được cộng vào ví của bạn.")
                        st.rerun()
        else:
            st.warning("🔴 Bạn đang ở trạng thái Tạm nghỉ. Bật Online để nhận thông báo cuốc xe.")

    # =====================================================
    # VAI TRÒ: TÀI XẾ CHẶNG DÀI
    # =====================================================
    elif role == "🚛 Chặng dài (Xe tải lớn/Container)":
        st.subheader("Sàn Vận Tải Chặng Dài (Middle-Mile)")
        truck_profile = st.selectbox("Hồ sơ xe của bạn:", ["🥇 Xe tải rỗng chiều về", "🥈 Xe đối tác 3PL (Hợp đồng)", "🥉 Xe cá nhân tự do"])
        
        long_haul_orders = [o for o in st.session_state.orders if o["Trạng thái"] == "Chờ xe chặng dài"]
        
        if not long_haul_orders:
            st.info("Hiện không có đơn hàng nào cần xe tải lớn.")
            
        for order in long_haul_orders:
            with st.container(border=True):
                st.write(f"📦 **Đơn hàng {order['ID']}** - {order['Khối lượng']} Tấn {order['Sản phẩm']}")
                st.write(f"📍 **Lộ trình:** Hub Đại lý ➡️ {order['Nhà máy']} ({order['Địa chỉ']})")
                
                if st.button(f"🚛 Nhận chuyến giao hàng ({order['ID']})"):
                    order["Trạng thái"] = "Đang giao đến Nhà máy"
                    order["Loại_Xe"] = truck_profile 
                    st.success("Đã nhận chuyến! Mời bác tài đánh xe đến Hub lấy hàng.")
                    st.rerun()
    # =====================================================
    # VAI TRÒ: ADMIN
    # =====================================================
    elif role == "👑 Admin":
        st.header("Trạm Điều Hành Trung Tâm AgriLoop")
        
        tab1, tab2, tab3 = st.tabs(["📊 Tổng quan Dashboard", "⚙️ Cấu hình Hệ thống", "🛠️ Quản lý Đơn hàng (Control Panel)"])
        
        with tab1:
            completed_orders = [o for o in st.session_state.orders if o.get("Trạng thái") == "Hoàn tất"]
            total_revenue = sum(o.get("Tổng_Thực_Tế", 0) for o in completed_orders)
            total_platform_fee = sum(o.get("Phí_Sàn_Thực_Tế", 0) for o in completed_orders)
            total_shipping = sum((o.get("Chi_Phi_Chặng_Ngắn", 0) + o.get("Chi_Phi_Chặng_Dài", 0)) for o in completed_orders)
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Tổng Doanh Thu (GMV)", f"{total_revenue / 1000000:,.1f} Tr")
            col2.metric("Lợi nhuận Thuần Sàn", f"{total_platform_fee / 1000000:,.1f} Tr", "+15%")
            col3.metric("Tổng Phí Vận Chuyển", f"{total_shipping / 1000000:,.1f} Tr")
            col4.metric("Số Đơn Hoàn Tất", len(completed_orders))
            
            st.subheader("Doanh thu theo Hub Đại lý")
            if completed_orders:
                df_hub = pd.DataFrame(completed_orders)
                if "Hub_Location" in df_hub.columns:
                    hub_rev = df_hub.groupby("Hub_Location")["Phí_Sàn_Thực_Tế"].sum()
                    st.bar_chart(hub_rev)
            else:
                st.info("Chưa đủ dữ liệu để vẽ biểu đồ.")

        with tab2:
            st.subheader("⚙️ Cấu hình Bộ máy định giá AgriLoop")
            st.info("Lưu ý: Thay đổi cấu hình tại đây sẽ áp dụng lập tức cho các đơn hàng mới tạo.")
            
            col_a, col_b = st.columns(2)
            with col_a:
                cfg["price_rom_cuon"] = st.number_input("Giá Rơm cuộn (VNĐ/Tấn)", value=cfg["price_rom_cuon"], step=50000)
                cfg["price_rom_roi"] = st.number_input("Giá Rơm rời (VNĐ/Tấn)", value=cfg["price_rom_roi"], step=50000)
            with col_b:
                cfg["shipping_short_per_ton"] = st.number_input("Đơn giá chặng ngắn (VNĐ/Tấn)", value=cfg["shipping_short_per_ton"], step=10000)
                cfg["shipping_long_per_ton"] = st.number_input("Đơn giá chặng dài tiêu chuẩn (VNĐ/Tấn)", value=cfg["shipping_long_per_ton"], step=10000)
                cfg["platform_fee_rate"] = st.slider("Phí nền tảng (Tỷ lệ %)", 0.01, 0.15, float(cfg["platform_fee_rate"]), step=0.01)

        with tab3:
            st.subheader("🛠️ Can thiệp hệ thống (Emergency Panel)")
            if not st.session_state.orders:
                st.write("Chưa có đơn hàng nào trên hệ thống.")
            
            for order in st.session_state.orders:
                with st.expander(f"Mã Lệnh: {order['ID']} | Trạng thái: {order['Trạng thái']}"):
                    st.write(f"**Nhà máy:** {order['Nhà máy']} | **Hub đang xử lý:** {order.get('Hub_Location', 'Chưa có')}")
                    col_btn1, col_btn2 = st.columns(2)
                    
                    if col_btn1.button("❌ Hủy bỏ đơn hàng này (Force Cancel)", key=f"cancel_{order['ID']}"):
                        order["Trạng thái"] = "Đã hủy bởi Admin"
                        st.toast(f"Đã hủy đơn {order['ID']}!")
                        st.rerun()
                    
                    if col_btn2.button("🔁 Reset trạng thái về 'Sẵn sàng cho Đại lý'", key=f"reset_{order['ID']}"):
                        order["Trạng thái"] = "Sẵn sàng cho Đại lý"
                        st.toast(f"Đã reset đơn {order['ID']}!")
                        st.rerun()

