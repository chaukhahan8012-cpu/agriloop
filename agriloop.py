import streamlit as st
import pandas as pd
import random
from datetime import datetime

st.set_page_config(page_title="AgriLoop - Diamond System", layout="wide", page_icon="🌾")

# ==========================
# CẤU HÌNH CSS & GIAO DIỆN
# ==========================
st.markdown("""
    <style>
    .invoice-box { background-color: #f1f8e9; padding: 20px; border-radius: 10px; border: 1px solid #c5e1a5; margin-bottom: 20px; }
    .invoice-final { background-color: #ffffff; padding: 30px; border-radius: 8px; border: 1px solid #e0e0e0; box-shadow: 0 4px 6px rgba(0,0,0,0.05); position: relative;}
    .watermark { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(-45deg); font-size: 60px; color: rgba(211, 47, 47, 0.1); font-weight: bold; z-index: 0; pointer-events: none; border: 5px solid rgba(211, 47, 47, 0.1); padding: 10px; border-radius: 10px;}
    .farmer-card { border-left: 4px solid #ff9800; padding: 15px; background: #fff8e1; margin-bottom: 10px; border-radius: 5px;}
    .transport-box { border: 2px dashed #1976d2; padding: 15px; background-color: #e3f2fd; border-radius: 8px; margin-top: 15px;}
    .driver-card { border-left: 4px solid #00b14f; padding: 15px; background: #e8f5e9; margin-bottom: 10px; border-radius: 5px;}
    .login-container { max-width: 500px; margin: 0 auto; padding: 30px; background-color: white; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); border-top: 5px solid #2e7d32; }
    .timeline-container { border-left: 3px solid #4caf50; padding-left: 20px; margin-left: 10px; }
    .timeline-item { margin-bottom: 15px; position: relative; }
    .timeline-item::before { content: ''; position: absolute; left: -27.5px; top: 5px; width: 12px; height: 12px; border-radius: 50%; background-color: #4caf50; }
    .timeline-item.past::before { background-color: #bdbdbd; }
    .timeline-item.past { border-left-color: #bdbdbd; color: gray; }
    </style>
""", unsafe_allow_html=True)

# ==========================
# KHỞI TẠO CẤU HÌNH & DỮ LIỆU
# ==========================
if "system_config" not in st.session_state:
    st.session_state.system_config = {
        "price_rom_cuon": 850000, "price_rom_roi": 600000,
        "shipping_short_per_ton": 120000, "shipping_long_per_ton": 200000,
        "platform_fee_rate": 0.05, "risk_fund_rate": 0.01
    }

if "orders" not in st.session_state:
    st.session_state.orders = []
if "farmer_offers" not in st.session_state:
    st.session_state.farmer_offers = [] 
if "agent_points" not in st.session_state:
    st.session_state.agent_points = 250 # Điểm khởi tạo

def get_agent_tier(points):
    if points < 500: return "Đồng 🥉", "#795548"
    elif points < 1000: return "Bạc 🥈", "#9e9e9e"
    elif points < 2000: return "Vàng 🥇", "#ffb300"
    else: return "Kim Cương 💎", "#00bcd4"

# TRẠNG THÁI ĐĂNG NHẬP
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False
    st.session_state.current_role = ""
    st.session_state.username = ""
    st.session_state.agent_address = ""

def logout():
    st.session_state.is_logged_in = False
    st.session_state.current_role = ""

# =====================================================
# MÀN HÌNH ĐĂNG NHẬP
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
            role_select = st.selectbox("Chọn vai trò của bạn:", 
                ["🏭 Nhà máy", "🏪 Đại lý (Hub)", "🌾 Nông dân", "🚜 Tài xế (Chặng ngắn)", "🚛 Tài xế (Chặng dài)", "👑 Admin"]
            )
            agent_loc = ""
            if role_select == "🏪 Đại lý (Hub)":
                agent_loc = st.text_input("📍 Nhập địa chỉ Hub của bạn (Huyện, Tỉnh):", placeholder="VD: Vĩnh Châu, Sóc Trăng...")
            
            if st.form_submit_button("Đăng nhập vào Hệ thống"):
                if username == "": st.error("Vui lòng nhập tên đăng nhập!")
                elif role_select == "🏪 Đại lý (Hub)" and agent_loc == "": st.error("Vui lòng nhập địa chỉ Hub!")
                else:
                    st.session_state.is_logged_in = True
                    st.session_state.username = username
                    st.session_state.current_role = role_select
                    if role_select == "🏪 Đại lý (Hub)": st.session_state.agent_address = agent_loc
                    st.rerun()

# =====================================================
# GIAO DIỆN CHÍNH
# =====================================================
else:
    role = st.session_state.current_role
    cfg = st.session_state.system_config
    
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2664/2664552.png", width=80)
    st.sidebar.title("AgriLoop MVP")
    st.sidebar.markdown(f"**👤 Xin chào:** {st.session_state.username}")
    st.sidebar.markdown(f"**💼 Vai trò:** {role}")
    
    if role == "🏪 Đại lý (Hub)":
        tier_name, tier_color = get_agent_tier(st.session_state.agent_points)
        st.sidebar.markdown(f"**📍 Hub:** {st.session_state.agent_address}")
        st.sidebar.markdown(f"**🌟 Hạng Đại lý:** <span style='color:{tier_color}; font-weight:bold;'>{tier_name} ({st.session_state.agent_points} pt)</span>", unsafe_allow_html=True)
        
    st.sidebar.markdown("---")
    st.sidebar.button("🚪 Đăng xuất", on_click=logout)
    st.title(f"{role}")

    # =====================================================
    # VAI TRÒ: NHÀ MÁY
    # =====================================================
    if role == "🏭 Nhà máy":
        tab_buy, tab_track, tab_history = st.tabs(["🛒 Lên Đơn Mới & Đặt Cọc", "📍 Theo dõi lộ trình", "🧾 Hóa đơn Điện tử"])
        
        with tab_buy:
            st.header("Tạo Lệnh Thu Mua (Báo giá dự kiến)")
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
                    <h4>🧾 Hóa đơn Dự kiến (Tạm tính)</h4>
                    <p>- Tiền rơm: {base_cost:,.0f} đ</p>
                    <p>- Phí vận chuyển dự kiến: {shipping_est:,.0f} đ</p>
                    <p>- Phí sàn AgriLoop: {platform_fee:,.0f} đ</p>
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
                        "Đã_Gom": 0.0, "Hub_Location": "Chưa có", "Tọa_Độ_Hub": [0,0]
                    })
                    st.success("Đã tạo đơn thành công! Vui lòng quét mã QR bên dưới để thanh toán cọc.")
            
            # SHOW MÃ QR NGAY BÊN DƯỚI FORM TẠO ĐƠN
            pending_deposits = [o for o in st.session_state.orders if o["Trạng thái"] == "Chờ quét QR Cọc"]
            if pending_deposits:
                st.markdown("---")
                st.subheader("📲 Mã QR Thanh Toán Đặt Cọc")
                for order in pending_deposits:
                    with st.container(border=True):
                        col_qr, col_info = st.columns([1, 2])
                        with col_qr: 
                            st.image("https://upload.wikimedia.org/wikipedia/commons/d/d0/QR_code_for_mobile_English_Wikipedia.svg", width=150)
                        with col_info:
                            st.write(f"**Mã đơn hàng:** {order['ID']}")
                            st.write(f"**Số tiền cọc (30%):** <span style='color:#d32f2f; font-size:20px; font-weight:bold;'>{order['Tiền_Cọc']:,.0f} VNĐ</span>", unsafe_allow_html=True)
                            st.write("Nội dung CK: `CK COCC AGRILOOP " + order['ID'] + "`")
                            if st.button(f"✅ Mô phỏng: Đã thanh toán xong ({order['ID']})"):
                                order["Trạng thái"] = "Sẵn sàng cho Đại lý"
                                st.rerun()

        with tab_track:
            st.header("Trạng Thái Đơn Hàng Liên Tục")
            active_factory_orders = [o for o in st.session_state.orders if o["Trạng thái"] not in ["Hoàn tất", "Chờ quét QR Cọc"]]
            
            if not active_factory_orders:
                st.info("Hiện không có đơn hàng nào đang trong quá trình vận chuyển/thu gom.")
                
            for order in active_factory_orders:
                with st.expander(f"📦 Đơn {order['ID']} - {order['Khối lượng']} Tấn {order['Sản phẩm']} | Trạng thái: {order['Trạng thái']}", expanded=True):
                                
                    if order["Trạng thái"] in ["Sẵn sàng cho Đại lý", "Đại lý đang gom", "Chờ xe chặng dài"]:
                        st.info("🔄 Hệ thống đang xử lý và thu gom nguyên liệu tại địa phương.")
                        progress = 0
                        if order["Trạng thái"] == "Sẵn sàng cho Đại lý": progress = 20
                        elif order["Trạng thái"] == "Đại lý đang gom": progress = 50
                        elif order["Trạng thái"] == "Chờ xe chặng dài": progress = 80
                        st.progress(progress / 100.0, text=f"Tiến độ tổng thể: {progress}%")
                    
                    elif order["Trạng thái"] == "Đang giao đến Nhà máy":
                        col_map, col_bill = st.columns([1.2, 1])
                        with col_map:
                            st.markdown("### 📍 Live Tracking (Bản đồ xe chạy)")
                            map_data = pd.DataFrame({'lat': [9.7150 + random.uniform(-0.01, 0.01)], 'lon': [105.8150 + random.uniform(-0.01, 0.01)]})
                            st.map(map_data, zoom=10)
                            st.caption(f"Đang di chuyển từ Hub {order['Hub_Location']} đến {order['Địa chỉ']}.")
                            
                        with col_bill:
                            st.markdown("### 📊 Quyết Toán Thực Tế")
                            actual_shipping = order['Chi_Phi_Chặng_Ngắn'] + order['Chi_Phi_Chặng_Dài']
                            actual_subtotal = order['Chi_Phi_Rơm'] + actual_shipping
                            actual_total = actual_subtotal + (actual_subtotal * cfg["platform_fee_rate"])
                            
                            st.write(f"- Tiền rơm: **{order['Chi_Phi_Rơm']:,.0f} đ**")
                            st.write(f"- Vận chuyển thực tế: **{actual_shipping:,.0f} đ**")
                            st.write(f"- **TỔNG THỰC TẾ: <span style='color:#1976d2;'>{actual_total:,.0f} đ</span>**", unsafe_allow_html=True)
                            
                            if st.button(f"✅ ĐÃ NHẬN HÀNG - XUẤT HÓA ĐƠN ({order['ID']})", use_container_width=True):
                                order["Trạng thái"] = "Hoàn tất"
                                order["Tổng_Thực_Tế"] = actual_total
                                order["Phí_Sàn_Thực_Tế"] = actual_subtotal * cfg["platform_fee_rate"]
                                order["Quỹ_Rủi_Ro"] = actual_total * cfg["risk_fund_rate"]
                                st.session_state.agent_points += 100 
                                st.rerun()

        with tab_history:
            st.header("Hóa Đơn Điện Tử (E-Invoice)")
            factory_history = [o for o in st.session_state.orders if o["Trạng thái"] == "Hoàn tất"]
            
            if not factory_history:
                st.info("Chưa có hóa đơn nào được xuất.")
                
            for order in factory_history:
                with st.expander(f"🧾 Hóa đơn số #{order['ID']} - {order['Deadline']}", expanded=False):
                    final_payment = order['Tổng_Thực_Tế'] - order['Tiền_Cọc']
                    st.markdown(f"""
                    <div class="invoice-final">
                        <div class="watermark">ĐÃ THANH TOÁN</div>
                        <h3 style="text-align: center; color: #1976d2; margin-bottom: 0;">HÓA ĐƠN ĐIỆN TỬ (GTGT)</h3>
                        <p style="text-align: center; color: gray;">Đơn vị phát hành: Sàn Giao Dịch AgriLoop</p>
                        <hr>
                        <div style="display:flex; justify-content: space-between;">
                            <div>
                                <p><b>Mã giao dịch:</b> {order['ID']}</p>
                                <p><b>Đơn vị mua:</b> {order['Nhà máy']}</p>
                                <p><b>Đại lý cung cấp:</b> Hub {order['Hub_Location']}</p>
                            </div>
                            <div style="text-align: right;">
                                <p><b>Ngày xuất:</b> {datetime.now().strftime('%d/%m/%Y')}</p>
                                <p><b>Loại hàng:</b> {order['Sản phẩm']}</p>
                            </div>
                        </div>
                        <table style="width: 100%; margin-top: 15px; border-collapse: collapse;">
                            <tr style="background-color: #f5f5f5; border-bottom: 2px solid #ddd;">
                                <th style="padding: 8px; text-align: left;">Diễn giải</th>
                                <th style="padding: 8px; text-align: right;">Thành tiền (VNĐ)</th>
                            </tr>
                            <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;">Tiền hàng ({order['Khối lượng']} Tấn)</td><td style="padding: 8px; text-align: right; border-bottom: 1px solid #ddd;">{order['Chi_Phi_Rơm']:,.0f}</td></tr>
                            <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;">Phí vận chuyển chặng ngắn</td><td style="padding: 8px; text-align: right; border-bottom: 1px solid #ddd;">{order['Chi_Phi_Chặng_Ngắn']:,.0f}</td></tr>
                            <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;">Phí vận chuyển chặng dài</td><td style="padding: 8px; text-align: right; border-bottom: 1px solid #ddd;">{order['Chi_Phi_Chặng_Dài']:,.0f}</td></tr>
                            <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;">Phí dịch vụ nền tảng (Đã gồm thuế)</td><td style="padding: 8px; text-align: right; border-bottom: 1px solid #ddd;">{order['Phí_Sàn_Thực_Tế']:,.0f}</td></tr>
                        </table>
                        <br>
                        <div style="text-align: right; font-size: 18px;">
                            <p>Tổng cộng: <b>{order['Tổng_Thực_Tế']:,.0f} VNĐ</b></p>
                            <p style="color: gray; font-size: 14px;">Trừ Tạm ứng (Cọc 30%): -{order['Tiền_Cọc']:,.0f} VNĐ</p>
                            <h3 style="color: #2e7d32; margin-top: 5px;">Thanh toán đợt cuối: {final_payment:,.0f} VNĐ</h3>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    # =====================================================
    # VAI TRÒ: ĐẠI LÝ
    # =====================================================
    elif role == "🏪 Đại lý (Hub)":
        st.header(f"Chợ Lệnh Thu Mua")
        available_orders = [o for o in st.session_state.orders if o["Trạng thái"] == "Sẵn sàng cho Đại lý"]
        for order in available_orders:
            with st.container(border=True):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.write(f"🏭 **{order['Nhà máy']}** cần **{order['Khối lượng']} Tấn {order['Sản phẩm']}**")
                with col_b:
                    if st.button(f"Nhận thầu (+20đ) | {order['ID']}"):
                        order["Trạng thái"] = "Đại lý đang gom"
                        order["Hub_Location"] = st.session_state.agent_address
                        st.session_state.agent_points += 20
                        st.rerun()

        st.markdown("---")
        st.header("Trung Tâm Thu Gom")
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
                for offer in offers:
                    with st.container(border=True):
                        st.write(f"🧑‍🌾 **{offer['Tên']}** - Cung cấp: **{offer['Khối lượng']} Tấn**")
                        if offer["Trạng thái"] == "Nông dân tự giao":
                            if st.button(f"👉 Xác nhận đã nhập kho ({offer['ID']})"):
                                offer["Trạng thái"] = "Đã nhập kho"
                                order["Đã_Gom"] += offer["Khối lượng"]
                                st.rerun()
                        elif offer["Trạng thái"] == "Chờ Đại lý xác nhận gom":
                            if st.button(f"📡 Chấp nhận & Gọi xe ba gác ({offer['ID']})"):
                                offer["Trạng thái"] = "Chờ Tài xế chặng ngắn"
                                st.rerun()
                        elif offer["Trạng thái"] in ["Chờ Tài xế chặng ngắn", "Tài xế đang đi gom"]:
                            st.info("⏳ Đang điều phối xe chặng ngắn...")
                        elif offer["Trạng thái"] == "Đã nhập kho":
                            st.success(f"✅ Đã nhập kho.")
                
                if order['Đã_Gom'] >= order['Khối lượng']:
                    st.success("✅ Kho đã đầy - Đã chốt chi phí chặng ngắn thực tế!")
                    if st.button(f"🚀 Gọi xe tải Chặng Dài ({order['ID']})"):
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
                f_method = st.radio("Phương thức giao nhận:", ["Đại lý lại gom", "Tôi tự chở lại Hub"])
                if st.form_submit_button("Xác nhận Bán"):
                    initial_status = "Chờ Đại lý xác nhận gom" if "Đại lý lại gom" in f_method else "Nông dân tự giao"
                    st.session_state.farmer_offers.append({
                        "ID": f"FM{random.randint(1000,9999)}", "Order_ID": order["ID"],
                        "Tên": f_name, "Địa chỉ": f_address, "Khối lượng": f_weight,
                        "Phương thức": f_method, "Trạng thái": initial_status
                    })
                    st.success("Đã gửi yêu cầu thành công!")

    # =====================================================
    # VAI TRÒ: TÀI XẾ CHẶNG NGẮN & DÀI
    # =====================================================
    elif role == "🚜 Tài xế (Chặng ngắn)":
        st.subheader("Trạm Nhận Cuốc (Zalo Mini App)")
        is_active = st.toggle("🟢 Bật nhận cuốc (Online)", value=True)
        if is_active:
            short_haul_trips = [f for f in st.session_state.farmer_offers if f["Trạng thái"] in ["Chờ Tài xế chặng ngắn", "Tài xế đang đi gom"]]
            for trip in short_haul_trips:
                st.markdown(f"<div class='driver-card'><h4>📍 Gom {trip['Khối lượng']} Tấn Rơm tại {trip['Tên']}</h4></div>", unsafe_allow_html=True)
                if trip["Trạng thái"] == "Chờ Tài xế chặng ngắn":
                    if st.button(f"✅ Nhận cuốc ({trip['ID']})"):
                        trip["Trạng thái"] = "Tài xế đang đi gom"
                        st.rerun()
                elif trip["Trạng thái"] == "Tài xế đang đi gom":
                    if st.button(f"🏁 Đã hạ tải tại Hub ({trip['ID']})"):
                        trip["Trạng thái"] = "Đã nhập kho"
                        for o in st.session_state.orders:
                            if o["ID"] == trip["Order_ID"]:
                                o["Đã_Gom"] += trip["Khối lượng"]
                                o["Chi_Phi_Chặng_Ngắn"] += (trip["Khối lượng"] * cfg["shipping_short_per_ton"])
                        st.rerun()

    elif role == "🚛 Tài xế (Chặng dài)":
        st.subheader("Sàn Vận Tải Chặng Dài (Middle-Mile)")
        truck_profile = st.selectbox("Hồ sơ xe của bạn:", ["🥇 Xe tải rỗng chiều về (Giảm 20% cước)", "🥈 Xe đối tác 3PL (Giá chuẩn)"])
        long_haul_orders = [o for o in st.session_state.orders if o["Trạng thái"] == "Chờ xe chặng dài"]
        for order in long_haul_orders:
            with st.container(border=True):
                st.write(f"📦 **Đơn hàng {order['ID']}** - {order['Khối lượng']} Tấn về {order['Nhà máy']}")
                if st.button(f"🚛 Nhận chuyến giao hàng ({order['ID']})"):
                    order["Trạng thái"] = "Đang giao đến Nhà máy"
                    order["Loại_Xe"] = truck_profile.split(" ")[1]
                    multiplier = 0.8 if "rỗng" in truck_profile else 1.0
                    order["Chi_Phi_Chặng_Dài"] = order["Khối lượng"] * cfg["shipping_long_per_ton"] * multiplier
                    st.rerun()

    # =====================================================
    # VAI TRÒ: ADMIN
    # =====================================================
    elif role == "👑 Admin":
        st.header("Trạm Điều Hành Trung Tâm AgriLoop")
        tab1, tab2, tab3 = st.tabs(["📊 Dashboard & Escrow", "⚙️ Cấu hình Hệ thống", "🛠️ Quản lý Đơn hàng"])
        
        with tab1:
            completed_orders = [o for o in st.session_state.orders if o.get("Trạng thái") == "Hoàn tất"]
            total_revenue = sum(o.get("Tổng_Thực_Tế", 0) for o in completed_orders)
            total_platform_fee = sum(o.get("Phí_Sàn_Thực_Tế", 0) for o in completed_orders)
            total_risk_fund = sum(o.get("Quỹ_Rủi_Ro", 0) for o in completed_orders)
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Doanh thu GMV", f"{total_revenue / 1000000:,.1f} Tr")
            col2.metric("Doanh thu Sàn", f"{total_platform_fee / 1000000:,.1f} Tr")
            col3.metric("🏦 Quỹ Rủi Ro", f"{total_risk_fund / 1000:,.0f} K")
            col4.metric("Số Đơn Hoàn Tất", len(completed_orders))

        with tab2:
            st.subheader("⚙️ Cấu hình Bộ máy định giá & Quản trị rủi ro")
            col_a, col_b = st.columns(2)
            with col_a:
                cfg["price_rom_cuon"] = st.number_input("Giá Rơm cuộn (VNĐ/Tấn)", value=cfg["price_rom_cuon"])
                cfg["price_rom_roi"] = st.number_input("Giá Rơm rời (VNĐ/Tấn)", value=cfg["price_rom_roi"])
            with col_b:
                cfg["shipping_short_per_ton"] = st.number_input("Đơn giá chặng ngắn (VNĐ/Tấn)", value=cfg["shipping_short_per_ton"])
                cfg["shipping_long_per_ton"] = st.number_input("Đơn giá chặng dài (VNĐ/Tấn)", value=cfg["shipping_long_per_ton"])
                cfg["platform_fee_rate"] = st.slider("Phí nền tảng (%)", 0.01, 0.15, float(cfg["platform_fee_rate"]), 0.01)
                cfg["risk_fund_rate"] = st.slider("Quỹ rủi ro - Escrow (%)", 0.0, 0.05, float(cfg["risk_fund_rate"]), 0.005)

        with tab3:
            st.subheader("🛠️ Can thiệp hệ thống & Điểm Tín Dụng")
            for order in st.session_state.orders:
                with st.expander(f"Mã Lệnh: {order['ID']} | Trạng thái: {order['Trạng thái']}"):
                    col_btn1, col_btn2 = st.columns(2)
                    if col_btn1.button("❌ Hủy bỏ đơn hàng này", key=f"cancel_{order['ID']}"):
                        order["Trạng thái"] = "Đã hủy bởi Admin"
                        st.session_state.agent_points -= 50 # Trừ điểm nặng khi hủy
                        st.rerun()
                    if col_btn2.button("🔁 Reset trạng thái về 'Sẵn sàng'", key=f"reset_{order['ID']}"):
                        order["Trạng thái"] = "Sẵn sàng cho Đại lý"
                        st.session_state.agent_points -= 20
                        st.rerun()

