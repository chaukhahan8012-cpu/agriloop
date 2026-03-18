import streamlit as st
import pandas as pd
import random
from datetime import datetime

st.set_page_config(page_title="AgriLoop - Nền tảng Logistics Nông nghiệp", layout="wide", page_icon="🌾")

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
    .qr-box { background-color: #e8eaf6; padding: 15px; border-radius: 8px; border-left: 5px solid #3f51b5; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

# ==========================
# KHỞI TẠO CẤU HÌNH & DỮ LIỆU
# ==========================
if "system_config" not in st.session_state:
    st.session_state.system_config = {
        "price_rom_cuon": 850000, 
        "price_rom_roi": 600000,
        "shipping_short_per_ton": 120000, 
        "shipping_long_per_ton": 200000,
        "fee_transaction": 0.05,      # 5% phí sàn giao dịch
        "fee_logistics": 0.03,        # 3% phí điều phối logistics (chặng dài)
        "fee_qa": 0.01,               # 1% phí đảm bảo chất lượng
        "fee_commitment": 0.02        # 2% phí cam kết giao dịch (có hoàn lại)
    }

if "orders" not in st.session_state:
    st.session_state.orders = []
if "farmer_offers" not in st.session_state:
    st.session_state.farmer_offers = [] 
if "agent_points" not in st.session_state:
    st.session_state.agent_points = 60 # Khởi tạo mặc định ở mức B

def get_agent_tier(points):
    if points <= 50: return "Hạng C (Uy tín thấp)", "#d32f2f"
    elif points <= 100: return "Hạng B (Uy tín trung bình)", "#ff9800"
    else: return "Hạng A (Uy tín cao)", "#4caf50"

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
            <h2 style="text-align: center; color: #2e7d32;">🌾 AgriLoop MVP</h2>
            <p style="text-align: center; color: gray;">Nền tảng logistics số kết nối chuỗi cung ứng phụ phẩm nông nghiệp</p>
        </div>
        """, unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("Tên đăng nhập (Demo: nhập bất kỳ)")
            password = st.text_input("Mật khẩu", type="password")
            role_select = st.selectbox("Chọn vai trò của bạn:", 
                ["🏭 Nhà máy/Doanh nghiệp", "🏪 Đại lý (Hub thu gom)", "🌾 Nông dân", "🚜 Tài xế (Chặng ngắn - Ba gác/Máy cày)", "🚛 Tài xế (Chặng dài - Xe tải)", "👑 Admin"]
            )
            agent_loc = ""
            if role_select == "🏪 Đại lý (Hub thu gom)":
                agent_loc = st.text_input("📍 Nhập địa chỉ Hub của bạn:", placeholder="VD: Tam Nông, Đồng Tháp")
            
            if st.form_submit_button("Đăng nhập hệ thống"):
                if username == "": st.error("Vui lòng nhập tên đăng nhập!")
                elif role_select == "🏪 Đại lý (Hub thu gom)" and agent_loc == "": st.error("Vui lòng nhập địa chỉ Hub!")
                else:
                    st.session_state.is_logged_in = True
                    st.session_state.username = username
                    st.session_state.current_role = role_select
                    if role_select == "🏪 Đại lý (Hub thu gom)": st.session_state.agent_address = agent_loc
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
    
    if role == "🏪 Đại lý (Hub thu gom)":
        tier_name, tier_color = get_agent_tier(st.session_state.agent_points)
        st.sidebar.markdown(f"**📍 Hub:** {st.session_state.agent_address}")
        st.sidebar.markdown(f"**🌟 Hạng Đại lý:** <span style='color:{tier_color}; font-weight:bold;'>{tier_name} ({st.session_state.agent_points} pt)</span>", unsafe_allow_html=True)
        
    st.sidebar.markdown("---")
    st.sidebar.button("🚪 Đăng xuất", on_click=logout)
    st.title(f"{role}")

    # =====================================================
    # VAI TRÒ: NHÀ MÁY / DOANH NGHIỆP
    # =====================================================
    if role == "🏭 Nhà máy/Doanh nghiệp":
        tab_buy, tab_track, tab_history = st.tabs(["🛒 Khởi tạo Lệnh thu mua", "📍 Theo dõi & Đối soát", "🧾 Hóa đơn Điện tử"])
        
        with tab_buy:
            st.header("Khởi tạo Lệnh Thu Mua")
            with st.form("factory_order"):
                col1, col2 = st.columns(2)
                factory_name = col1.text_input("Tên Nhà máy", st.session_state.username)
                address = col2.text_input("Địa chỉ giao hàng", "Nhà máy điện sinh khối, Đồng Tháp")
                
                col3, col4, col5 = st.columns(3)
                product = col3.selectbox("Loại phụ phẩm", ["Rơm cuộn", "Rơm rời"])
                weight = col4.number_input("Khối lượng cần mua (Tấn)", min_value=1.0, value=32.0, step=0.5, format="%.1f")
                deadline = col5.date_input("Hạn chót nhận hàng")
                
                # Thuật toán định giá động cơ bản
                base_price = cfg["price_rom_cuon"] if product == "Rơm cuộn" else cfg["price_rom_roi"]
                base_cost = weight * base_price
                shipping_est = weight * (cfg["shipping_short_per_ton"] + cfg["shipping_long_per_ton"])
                subtotal = base_cost + shipping_est
                
                fee_tx = subtotal * cfg["fee_transaction"]
                fee_log = (weight * cfg["shipping_long_per_ton"]) * cfg["fee_logistics"]
                fee_qa = subtotal * cfg["fee_qa"]
                total_est = subtotal + fee_tx + fee_log + fee_qa
                
                commitment_fee = total_est * cfg["fee_commitment"] 
                
                st.markdown(f"""
                <div class="invoice-box">
                    <h4>🧾 Dự toán cấu trúc chi phí tổng</h4>
                    <p>- Giá trị nguyên liệu cơ sở: {base_cost:,.0f} đ</p>
                    <p>- Chi phí vận tải dự kiến (2 chặng): {shipping_est:,.0f} đ</p>
                    <p>- Phí dịch vụ nền tảng (5%): {fee_tx:,.0f} đ</p>
                    <p>- Phí điều phối logistics (3% chặng dài): {fee_log:,.0f} đ</p>
                    <p>- Phí đảm bảo chất lượng (1%): {fee_qa:,.0f} đ</p>
                    <h3 style="color: #2e7d32;">Tổng chi phí dự kiến: {total_est:,.0f} đ</h3>
                    <p style="color: #d32f2f; font-weight: bold;">⚠️ Phí cam kết giao dịch (2% - có hoàn lại): {commitment_fee:,.0f} đ</p>
                    <small><i>Khoản phí cam kết này nhằm ràng buộc trách nhiệm và sẽ được khấu trừ vào đợt thanh toán cuối.</i></small>
                </div>
                """, unsafe_allow_html=True)
                
                if st.form_submit_button("Xác nhận & Thanh toán Phí cam kết"):
                    new_id = f"AL{len(st.session_state.orders)+1:03}"
                    st.session_state.orders.append({
                        "ID": new_id, "Nhà máy": factory_name, "Địa chỉ": address,
                        "Sản phẩm": product, "Khối lượng": weight, "Deadline": str(deadline),
                        "Trạng thái": "Chờ quét QR Phí cam kết", "Tổng_Dự_Kiến": total_est, "Phí_Cam_Kết": commitment_fee,
                        "Chi_Phi_Rơm": base_cost, "Chi_Phi_Chặng_Ngắn": 0.0, "Chi_Phi_Chặng_Dài": 0.0,
                        "Đã_Gom": 0.0, "Hub_Location": "Chưa có", "Dữ_Liệu_IoT": None
                    })
                    st.success("Đã tạo lệnh! Vui lòng quét mã QR bên dưới để nộp phí cam kết.")
            
            pending_deposits = [o for o in st.session_state.orders if o["Trạng thái"] == "Chờ quét QR Phí cam kết"]
            if pending_deposits:
                st.markdown("---")
                st.subheader("📲 Mã QR Thanh toán Phí cam kết")
                for order in pending_deposits:
                    with st.container(border=True):
                        col_qr, col_info = st.columns([1, 2])
                        with col_qr: 
                            st.image("https://upload.wikimedia.org/wikipedia/commons/d/d0/QR_code_for_mobile_English_Wikipedia.svg", width=150)
                        with col_info:
                            st.write(f"**Mã lệnh:** {order['ID']}")
                            st.write(f"**Phí cam kết (2%):** <span style='color:#d32f2f; font-size:20px; font-weight:bold;'>{order['Phí_Cam_Kết']:,.0f} VNĐ</span>", unsafe_allow_html=True)
                            st.write("Nội dung CK: `CK CAMKET AGRILOOP " + order['ID'] + "`")
                            if st.button(f"✅ Mô phỏng: Đã chuyển khoản ({order['ID']})"):
                                order["Trạng thái"] = "Sẵn sàng cho Đại lý"
                                st.rerun()

        with tab_track:
            st.header("Kiểm soát chất lượng & Thanh toán")
            active_factory_orders = [o for o in st.session_state.orders if o["Trạng thái"] not in ["Hoàn tất", "Chờ quét QR Phí cam kết", "Đã hủy bởi Admin"]]
            
            if not active_factory_orders:
                st.info("Hiện không có đơn hàng nào đang xử lý.")
                
            for order in active_factory_orders:
                with st.expander(f"📦 Lệnh {order['ID']} - {order['Khối lượng']} Tấn {order['Sản phẩm']} | {order['Trạng thái']}", expanded=True):
                                
                    if order["Trạng thái"] in ["Sẵn sàng cho Đại lý", "Đại lý đang gom", "Chờ xe chặng dài"]:
                        st.info("🔄 Hệ thống đang điều phối mạng lưới thu gom và phân rã đơn tại địa phương.")
                        progress = 20 if order["Trạng thái"] == "Sẵn sàng cho Đại lý" else (50 if order["Trạng thái"] == "Đại lý đang gom" else 80)
                        st.progress(progress / 100.0, text=f"Tiến độ tổng thể: {progress}%")
                    
                    elif order["Trạng thái"] == "Đang giao đến Nhà máy":
                        col_map, col_bill = st.columns([1, 1])
                        with col_map:
                            st.markdown("### 📍 Check-in Vận chuyển")
                            st.success(f"Xe đang trên đường từ Hub {order['Hub_Location']} đến {order['Địa chỉ']}.")
                            if order.get("Dữ_Liệu_IoT"):
                                st.markdown("### 🔍 Dữ liệu IoT Định danh lô hàng")
                                iot = order["Dữ_Liệu_IoT"]
                                st.write(f"- Độ ẩm: **{iot['Độ_ẩm']}%**")
                                st.write(f"- Nhiệt độ: **{iot['Nhiệt_độ']}°C**")
                                st.write(f"- Khối lượng chốt: **{iot['Khối_lượng']} Tấn**")
                                st.write(f"- Phương tiện (Biển số): **{iot['Biển_số']}**")
                            
                        with col_bill:
                            st.markdown("### 📊 Đối soát Thanh toán")
                            actual_shipping = order['Chi_Phi_Chặng_Ngắn'] + order['Chi_Phi_Chặng_Dài']
                            actual_subtotal = order['Chi_Phi_Rơm'] + actual_shipping
                            
                            fee_tx = actual_subtotal * cfg["fee_transaction"]
                            fee_log = order['Chi_Phi_Chặng_Dài'] * cfg["fee_logistics"]
                            fee_qa = actual_subtotal * cfg["fee_qa"]
                            
                            actual_total = actual_subtotal + fee_tx + fee_log + fee_qa
                            
                            st.write(f"- Tiền rơm: **{order['Chi_Phi_Rơm']:,.0f} đ**")
                            st.write(f"- Vận chuyển thực tế: **{actual_shipping:,.0f} đ**")
                            st.write(f"- Các loại phí (Sàn, Điều phối, QA): **{(fee_tx+fee_log+fee_qa):,.0f} đ**")
                            st.write(f"- **TỔNG ĐỐI SOÁT: <span style='color:#1976d2;'>{actual_total:,.0f} đ</span>**", unsafe_allow_html=True)
                            
                            if st.button(f"✅ KIỂM TRA ĐẠT - XÁC NHẬN THANH TOÁN ({order['ID']})", use_container_width=True):
                                order["Trạng thái"] = "Hoàn tất"
                                order["Tổng_Thực_Tế"] = actual_total
                                order["Chi_Tiet_Phi"] = {"Fee_Tx": fee_tx, "Fee_Log": fee_log, "Fee_QA": fee_qa}
                                st.session_state.agent_points += 10 # Cộng điểm nhà máy/đại lý thanh toán đúng hạn
                                st.rerun()

        with tab_history:
            st.header("Hóa Đơn Điện Tử (E-Invoice)")
            factory_history = [o for o in st.session_state.orders if o["Trạng thái"] == "Hoàn tất"]
            
            if not factory_history:
                st.info("Chưa có chứng từ đối soát điện tử nào.")
                
            for order in factory_history:
                with st.expander(f"🧾 Chứng từ giao dịch #{order['ID']}", expanded=False):
                    final_payment = order['Tổng_Thực_Tế'] - order['Phí_Cam_Kết']
                    fees = order.get("Chi_Tiet_Phi", {"Fee_Tx": 0, "Fee_Log": 0, "Fee_QA": 0})
                    st.markdown(f"""
                    <div class="invoice-final">
                        <div class="watermark">ĐÃ THANH TOÁN</div>
                        <h3 style="text-align: center; color: #1976d2; margin-bottom: 0;">CHỨNG TỪ ĐỐI SOÁT ĐIỆN TỬ</h3>
                        <p style="text-align: center; color: gray;">Sàn Giao Dịch AgriLoop</p>
                        <hr>
                        <div style="display:flex; justify-content: space-between;">
                            <div>
                                <p><b>Mã giao dịch:</b> {order['ID']}</p>
                                <p><b>Đơn vị mua:</b> {order['Nhà máy']}</p>
                                <p><b>Đại lý cung cấp:</b> Hub {order['Hub_Location']}</p>
                            </div>
                            <div style="text-align: right;">
                                <p><b>Ngày chốt:</b> {datetime.now().strftime('%d/%m/%Y')}</p>
                                <p><b>Loại hàng:</b> {order['Sản phẩm']}</p>
                            </div>
                        </div>
                        <table style="width: 100%; margin-top: 15px; border-collapse: collapse;">
                            <tr style="background-color: #f5f5f5; border-bottom: 2px solid #ddd;">
                                <th style="padding: 8px; text-align: left;">Diễn giải</th>
                                <th style="padding: 8px; text-align: right;">Thành tiền (VNĐ)</th>
                            </tr>
                            <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;">Giá trị nguyên liệu ({order['Khối lượng']} Tấn)</td><td style="padding: 8px; text-align: right; border-bottom: 1px solid #ddd;">{order['Chi_Phi_Rơm']:,.0f}</td></tr>
                            <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;">Phí vận chuyển chặng ngắn</td><td style="padding: 8px; text-align: right; border-bottom: 1px solid #ddd;">{order['Chi_Phi_Chặng_Ngắn']:,.0f}</td></tr>
                            <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;">Phí vận chuyển chặng dài</td><td style="padding: 8px; text-align: right; border-bottom: 1px solid #ddd;">{order['Chi_Phi_Chặng_Dài']:,.0f}</td></tr>
                            <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;">Phí sàn giao dịch (5%)</td><td style="padding: 8px; text-align: right; border-bottom: 1px solid #ddd;">{fees['Fee_Tx']:,.0f}</td></tr>
                            <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;">Phí điều phối Logistics (3%)</td><td style="padding: 8px; text-align: right; border-bottom: 1px solid #ddd;">{fees['Fee_Log']:,.0f}</td></tr>
                            <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;">Phí đảm bảo chất lượng (1%)</td><td style="padding: 8px; text-align: right; border-bottom: 1px solid #ddd;">{fees['Fee_QA']:,.0f}</td></tr>
                        </table>
                        <br>
                        <div style="text-align: right; font-size: 18px;">
                            <p>Tổng cộng: <b>{order['Tổng_Thực_Tế']:,.0f} VNĐ</b></p>
                            <p style="color: gray; font-size: 14px;">Trừ Phí cam kết đã nộp: -{order['Phí_Cam_Kết']:,.0f} VNĐ</p>
                            <h3 style="color: #2e7d32; margin-top: 5px;">Thanh toán đợt cuối: {final_payment:,.0f} VNĐ</h3>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    # =====================================================
    # VAI TRÒ: ĐẠI LÝ (HUB THU GOM)
    # =====================================================
    elif role == "🏪 Đại lý (Hub thu gom)":
        st.header(f"Chợ Lệnh Thu Mua (Khớp lệnh nguồn cung)")
        available_orders = [o for o in st.session_state.orders if o["Trạng thái"] == "Sẵn sàng cho Đại lý"]
        for order in available_orders:
            with st.container(border=True):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.write(f"🏭 **{order['Nhà máy']}** cần **{order['Khối lượng']} Tấn {order['Sản phẩm']}**")
                    st.caption("Cơ chế phân rã đơn cho phép bạn gom một phần hoặc toàn bộ khối lượng.")
                with col_b:
                    # Đại lý nhận thầu sớm được cộng 20 điểm
                    if st.button(f"Nhận thầu (+20đ) | {order['ID']}"):
                        order["Trạng thái"] = "Đại lý đang gom"
                        order["Hub_Location"] = st.session_state.agent_address
                        st.session_state.agent_points += 20
                        st.rerun()

        st.markdown("---")
        st.header("Trung Tâm Thu Gom & Quản trị Chất lượng")
        active_orders = [o for o in st.session_state.orders if o["Trạng thái"] in ["Đại lý đang gom", "Chờ xe chặng dài"]]
        for order in active_orders:
            st.subheader(f"📦 Lệnh {order['ID']} - {order['Nhà máy']}")
            progress_pct = min(order['Đã_Gom'] / order['Khối lượng'], 1.0)
            st.progress(progress_pct, text=f"Đã tập kết tại Hub: {order['Đã_Gom']}/{order['Khối lượng']} Tấn")
            
            if order["Trạng thái"] == "Đại lý đang gom":
                if st.button(f"📢 Phát tín hiệu tìm rơm (Đồng bộ Zalo Mini App) - {order['ID']}"):
                    order["Broadcast_Zalo"] = True
                    st.toast("Đã gửi thông báo đến mạng lưới nông dân lân cận (bán kính 20km)!")
                    
                offers = [f for f in st.session_state.farmer_offers if f["Order_ID"] == order["ID"]]
                for offer in offers:
                    with st.container(border=True):
                        st.write(f"🧑‍🌾 **{offer['Tên']}** - Cung cấp: **{offer['Khối lượng']} Tấn** ({offer['Phương thức']})")
                        if offer["Trạng thái"] == "Nông dân tự giao":
                            if st.button(f"👉 Xác nhận đã nhập kho ({offer['ID']})"):
                                offer["Trạng thái"] = "Đã nhập kho"
                                order["Đã_Gom"] += offer["Khối lượng"]
                                st.session_state.agent_points += 5 # Xác nhận giao dịch đầy đủ
                                st.rerun()
                        elif offer["Trạng thái"] == "Chờ Đại lý xác nhận gom":
                            if st.button(f"📡 Điều phối chặng ngắn (Gọi xe lôi/ba gác) - {offer['ID']}"):
                                offer["Trạng thái"] = "Chờ Tài xế chặng ngắn"
                                st.rerun()
                        elif offer["Trạng thái"] in ["Chờ Tài xế chặng ngắn", "Tài xế đang đi gom"]:
                            st.info("⏳ Thuật toán đang phân bổ đơn cho tài xế địa phương...")
                        elif offer["Trạng thái"] == "Đã nhập kho":
                            st.success(f"✅ Đã nhập kho thành công.")
            
            if order['Đã_Gom'] >= order['Khối lượng'] and order["Trạng thái"] == "Đại lý đang gom":
                st.success("✅ Hub đã đủ sản lượng.")
                
                st.markdown("### 🎛️ Tầng 2: Kiểm tra IoT & Khởi tạo QR Định danh")
                if st.button(f"Đo lường bằng thiết bị IoT & Chốt lô hàng ({order['ID']})"):
                    # Mô phỏng dữ liệu IoT
                    moisture = round(random.uniform(12.0, 15.0), 1)
                    temp = round(random.uniform(28.0, 32.0), 1)
                    plate = f"66C-{random.randint(10000,99999)}"
                    
                    order["Dữ_Liệu_IoT"] = {
                        "Độ_ẩm": moisture,
                        "Nhiệt_độ": temp,
                        "Khối_lượng": order['Đã_Gom'],
                        "Biển_số": plate
                    }
                    order["Trạng thái"] = "Chờ xe chặng dài"
                    st.rerun()
                    
            if order["Trạng thái"] == "Chờ xe chặng dài":
                st.markdown(f"""
                <div class="qr-box">
                    <h4>Mã QR Định danh Lô hàng (Đã đồng bộ)</h4>
                    <p>Độ ẩm: <b>{order['Dữ_Liệu_IoT']['Độ_ẩm']}%</b> | Nhiệt độ: <b>{order['Dữ_Liệu_IoT']['Nhiệt_độ']}°C</b></p>
                    <p>Hệ thống đang ưu tiên điều phối các chuyến xe rỗng chiều về...</p>
                </div>
                """, unsafe_allow_html=True)

    # =====================================================
    # VAI TRÒ: NÔNG DÂN
    # =====================================================
    elif role == "🌾 Nông dân":
        st.header("Zalo Mini App - Bán Phụ Phẩm")
        broadcasted_orders = [o for o in st.session_state.orders if o.get("Broadcast_Zalo") == True and o["Trạng thái"] == "Đại lý đang gom"]
        
        if not broadcasted_orders:
            st.info("Chưa có thông báo thu mua nào quanh khu vực của bạn.")
            
        for order in broadcasted_orders:
            st.markdown(f"<div class='farmer-card'><h4>🔔 Đại lý đang cần thu mua {order['Sản phẩm']}</h4><p>Nhà máy: {order['Nhà máy']}</p></div>", unsafe_allow_html=True)
            with st.form(f"form_farmer_{order['ID']}"):
                f_name = st.text_input("Tên của bạn", st.session_state.username)
                f_address = st.text_input("Địa chỉ ruộng", "Xã Phú Cường, Tam Nông")
                f_weight = st.number_input("Nhập số lượng rơm (Tấn):", min_value=0.1, value=5.0, step=0.5, format="%.1f")
                
                # Nông dân có 2 option giao nhận
                f_method = st.radio("Hình thức giao nhận:", ["Đại lý lại gom", "Tôi tự chở lại kho bãi (Hub)"])
                
                if st.form_submit_button("Xác nhận Bán"):
                    initial_status = "Chờ Đại lý xác nhận gom" if "Đại lý lại gom" in f_method else "Nông dân tự giao"
                    st.session_state.farmer_offers.append({
                        "ID": f"FM{random.randint(1000,9999)}", "Order_ID": order["ID"],
                        "Tên": f_name, "Địa chỉ": f_address, "Khối lượng": f_weight,
                        "Phương thức": f_method, "Trạng thái": initial_status
                    })
                    st.success("Đã ghi nhận đơn hàng! Bạn có thể theo dõi tiến độ ngay trên Zalo.")

    # =====================================================
    # VAI TRÒ: TÀI XẾ CHẶNG NGẮN
    # =====================================================
    elif role == "🚜 Tài xế (Chặng ngắn - Ba gác/Máy cày)":
        st.subheader("Cuốc Xe Nội Vùng (< 20km)")
        st.caption("Cơ chế nhận cuốc tương tự Grab. Bật trạng thái để nhận đơn từ hợp tác xã.")
        
        is_active = st.toggle("🟢 Sẵn sàng nhận chuyến (Online)", value=True)
        if is_active:
            short_haul_trips = [f for f in st.session_state.farmer_offers if f["Trạng thái"] in ["Chờ Tài xế chặng ngắn", "Tài xế đang đi gom"]]
            if not short_haul_trips:
                st.info("Đang dò tìm cuốc xe quanh bạn...")
                
            for trip in short_haul_trips:
                st.markdown(f"<div class='driver-card'><h4>📍 Cần gom {trip['Khối lượng']} Tấn Rơm tại ruộng nhà {trip['Tên']}</h4><p>Khoảng cách ước tính: {round(random.uniform(2, 15), 1)} km</p></div>", unsafe_allow_html=True)
                if trip["Trạng thái"] == "Chờ Tài xế chặng ngắn":
                    if st.button(f"✅ Chấp nhận cuốc ({trip['ID']})"):
                        trip["Trạng thái"] = "Tài xế đang đi gom"
                        st.rerun()
                elif trip["Trạng thái"] == "Tài xế đang đi gom":
                    if st.button(f"🏁 Đã check-in & hạ tải tại Hub ({trip['ID']})"):
                        trip["Trạng thái"] = "Đã nhập kho"
                        for o in st.session_state.orders:
                            if o["ID"] == trip["Order_ID"]:
                                o["Đã_Gom"] += trip["Khối lượng"]
                                o["Chi_Phi_Chặng_Ngắn"] += (trip["Khối lượng"] * cfg["shipping_short_per_ton"])
                        st.rerun()

    # =====================================================
    # VAI TRÒ: TÀI XẾ CHẶNG DÀI
    # =====================================================
    elif role == "🚛 Tài xế (Chặng dài - Xe tải)":
        st.subheader("Sàn Giao Dịch Vận Tải (Back-haul Optimization)")
        truck_profile = st.selectbox("Lựa chọn phương thức chạy:", [
            "🥇 Xe rỗng chiều về (Back-haul) - Hệ thống ưu tiên phân bổ", 
            "🥈 Xe đối tác Doanh nghiệp vận tải (Ký hợp đồng dài hạn)"
        ])
        
        long_haul_orders = [o for o in st.session_state.orders if o["Trạng thái"] == "Chờ xe chặng dài"]
        if not long_haul_orders:
            st.info("Chưa có chuyến hàng lớn nào sẵn sàng từ Hub.")
            
        for order in long_haul_orders:
            with st.container(border=True):
                st.write(f"📦 **Lô hàng {order['ID']}** - {order['Khối lượng']} Tấn về {order['Nhà máy']}")
                st.caption(f"Yêu cầu chất lượng từ QR: Độ ẩm {order['Dữ_Liệu_IoT']['Độ_ẩm']}%")
                
                if st.button(f"🚛 Nhận chuyến vận tải ({order['ID']})"):
                    order["Trạng thái"] = "Đang giao đến Nhà máy"
                    order["Loại_Xe"] = "Back-haul" if "rỗng" in truck_profile else "Đối tác"
                    # Cơ chế giảm chi phí logistics nếu là xe rỗng chiều về
                    multiplier = 0.8 if "rỗng" in truck_profile else 1.0
                    order["Chi_Phi_Chặng_Dài"] = order["Khối lượng"] * cfg["shipping_long_per_ton"] * multiplier
                    st.rerun()

    # =====================================================
    # VAI TRÒ: ADMIN / BAN ĐIỀU HÀNH DỰ ÁN
    # =====================================================
    elif role == "👑 Admin":
        st.header("Bảng Điều Khiển Trung Tâm AgriLoop")
        tab1, tab2, tab3 = st.tabs(["📊 Tổng quan Kinh doanh & Môi trường", "⚙️ Cấu hình Dòng tiền", "🛠️ Sổ cái (Ledger)"])
        
        with tab1:
            completed_orders = [o for o in st.session_state.orders if o.get("Trạng thái") == "Hoàn tất"]
            
            # Tính GMV (Gross Merchandise Value)
            total_gmv = sum(o.get("Tổng_Thực_Tế", 0) for o in completed_orders)
            
            # Tính các nguồn doanh thu
            total_fee_tx = sum(o.get("Chi_Tiet_Phi", {}).get("Fee_Tx", 0) for o in completed_orders)
            total_fee_log = sum(o.get("Chi_Tiet_Phi", {}).get("Fee_Log", 0) for o in completed_orders)
            total_fee_qa = sum(o.get("Chi_Tiet_Phi", {}).get("Fee_QA", 0) for o in completed_orders)
            
            # Tính giá trị môi trường (SDG 13 - 1 Tấn rơm = 1.25 tấn khí thải CO2 theo logic của dự án)
            total_volume = sum(o.get("Khối lượng", 0) for o in completed_orders)
            co2_saved = total_volume * 1.25 
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Tổng GMV", f"{total_gmv / 1000000:,.1f} Tr")
            col2.metric("Doanh thu Sàn (5%)", f"{total_fee_tx / 1000:,.0f} K")
            col3.metric("Doanh thu Dịch vụ (Log/QA)", f"{(total_fee_log + total_fee_qa) / 1000:,.0f} K")
            col4.metric("🌱 Giảm phát thải CO2", f"{co2_saved:,.1f} Tấn", "Mục tiêu ESG")

            st.markdown("---")
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.subheader("Cơ cấu Doanh thu AgriLoop")
                if completed_orders:
                    revenue_data = pd.DataFrame({
                        "Loại Phí": ["Phí Sàn (5%)", "Phí Logistics (3%)", "Phí QA (1%)"],
                        "Giá trị": [total_fee_tx, total_fee_log, total_fee_qa]
                    }).set_index("Loại Phí")
                    st.bar_chart(revenue_data, color="#3f51b5")
                else:
                    st.info("Chưa có giao dịch hoàn tất.")
            
            with col_chart2:
                st.subheader("Sản lượng Phụ phẩm (Tấn)")
                if completed_orders:
                    df_chart = pd.DataFrame(completed_orders)
                    product_data = df_chart.groupby("Sản phẩm")["Khối lượng"].sum()
                    st.bar_chart(product_data, color="#2e7d32")
                else:
                    st.info("Chưa có giao dịch hoàn tất.")
                    
            st.markdown("---")
            st.subheader("📍 Bản đồ Triển khai MVP (Khu vực ĐBSCL)")
            st.caption("Tập trung giai đoạn 1 tại cụm địa lý: Đồng Tháp và các tỉnh lân cận.")
            # Map focus on Dong Thap / Tam Nong area
            map_hubs = pd.DataFrame({
                'lat': [10.7333, 10.4500, 10.2500], # Khu vực Đồng Tháp
                'lon': [105.5333, 105.6333, 105.8167]
            })
            st.map(map_hubs, zoom=8)

        with tab2:
            st.subheader("⚙️ Thiết lập Thuật toán Định giá")
            col_a, col_b = st.columns(2)
            with col_a:
                cfg["price_rom_cuon"] = st.number_input("Giá cơ sở: Rơm cuộn (VNĐ/Tấn)", value=cfg["price_rom_cuon"])
                cfg["price_rom_roi"] = st.number_input("Giá cơ sở: Rơm rời (VNĐ/Tấn)", value=cfg["price_rom_roi"])
                cfg["shipping_short_per_ton"] = st.number_input("Cước vận tải siêu địa phương (VNĐ/Tấn)", value=cfg["shipping_short_per_ton"])
                cfg["shipping_long_per_ton"] = st.number_input("Cước vận tải chặng dài (VNĐ/Tấn)", value=cfg["shipping_long_per_ton"])
            with col_b:
                cfg["fee_transaction"] = st.slider("Phí sàn giao dịch (Transaction Fee %)", 0.01, 0.10, float(cfg["fee_transaction"]), 0.01)
                cfg["fee_logistics"] = st.slider("Phí điều phối Logistics (%)", 0.01, 0.10, float(cfg["fee_logistics"]), 0.01)
                cfg["fee_qa"] = st.slider("Phí đảm bảo chất lượng (%)", 0.005, 0.05, float(cfg["fee_qa"]), 0.005)
                cfg["fee_commitment"] = st.slider("Cơ chế Phí cam kết giao dịch (%)", 0.01, 0.10, float(cfg["fee_commitment"]), 0.01)

        with tab3:
            st.subheader("📜 Sổ cái Giao dịch (Ledger)")
            if not st.session_state.orders:
                st.write("Hệ thống chưa ghi nhận lệnh thu mua.")
            else:
                df_ledger = pd.DataFrame(st.session_state.orders)
                cols = ["ID", "Nhà máy", "Sản phẩm", "Khối lượng", "Trạng thái", "Tổng_Dự_Kiến"]
                existing_cols = [c for c in cols if c in df_ledger.columns]
                st.dataframe(df_ledger[existing_cols], use_container_width=True)
                
                st.markdown("### ⚠️ Can thiệp & Xử lý Tranh chấp")
                for order in st.session_state.orders:
                    with st.expander(f"Mã Lệnh: {order['ID']} | Trạng thái: {order['Trạng thái']}"):
                        col_btn1, col_btn2 = st.columns(2)
                        if col_btn1.button("❌ Hủy/Thu hồi phí cam kết", key=f"cancel_{order['ID']}"):
                            order["Trạng thái"] = "Đã hủy bởi Admin"
                            st.session_state.agent_points -= 15 # Trừ điểm uy tín khi hủy đơn
                            st.rerun()
                        if col_btn2.button("🔁 Reset về 'Sẵn sàng'", key=f"reset_{order['ID']}"):
                            order["Trạng thái"] = "Sẵn sàng cho Đại lý"
                            st.rerun()
