import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="AgriLoop MVP", layout="wide", page_icon="🌾")

# ================== HẰNG SỐ ==================
PRICE_SELL = 800000        # Giá bán cho nhà máy / tấn
PRICE_BUY = 650000         # Giá đại lý mua từ nông dân / tấn
SHIPPING_PER_TON = 200000
PLATFORM_FEE_RATE = 0.05

# ================== SESSION STATE ==================
if "orders" not in st.session_state:
    st.session_state.orders = []

# ================== SIDEBAR ==================
st.sidebar.title("AgriLoop MVP")
role = st.sidebar.selectbox(
    "Chọn vai trò:",
    ["Nhà máy", "Đại lý", "Tài xế", "Admin"]
)

st.title(f"🚀 AgriLoop Dashboard - {role}")

# ====================================================
# ================== NHÀ MÁY =========================
# ====================================================

if role == "Nhà máy":

    st.subheader("🏭 Tạo đơn mua rơm")

    col1, col2 = st.columns([2,1])

    with col1:
        product = st.selectbox("Loại rơm", ["Rơm cuộn", "Rơm rời"])
        weight = st.number_input("Khối lượng (Tấn)", min_value=1, value=10)
        factory_name = st.text_input("Tên nhà máy", "NM Sinh học Hậu Giang")

    with col2:
        base_cost = weight * PRICE_SELL
        shipping = weight * SHIPPING_PER_TON
        subtotal = base_cost + shipping
        platform_fee = subtotal * PLATFORM_FEE_RATE
        total = subtotal + platform_fee

        st.markdown("### 🧾 Hóa đơn tạm tính")
        st.write(f"Tiền rơm: {base_cost:,.0f} đ")
        st.write(f"Phí vận chuyển: {shipping:,.0f} đ")
        st.write(f"Phí sàn (5%): {platform_fee:,.0f} đ")
        st.success(f"TỔNG: {total:,.0f} đ")

    if st.button("Đăng đơn lên hệ thống"):
        new_order = {
            "ID": f"AL{len(st.session_state.orders)+1:03}",
            "Sản phẩm": product,
            "Khối lượng": weight,
            "Nhà máy": factory_name,
            "Trạng thái": "Chờ đại lý",
            "Tổng tiền": total,
            "Phí sàn": platform_fee,
            "Lợi nhuận đại lý": weight * (PRICE_SELL - PRICE_BUY)
        }
        st.session_state.orders.append(new_order)
        st.success("Đã tạo đơn thành công!")

# ====================================================
# ================== ĐẠI LÝ ==========================
# ====================================================

elif role == "Đại lý":

    st.subheader("🤝 Danh sách đơn chờ nhận")

    pending = [o for o in st.session_state.orders if o["Trạng thái"] == "Chờ đại lý"]

    if not pending:
        st.info("Chưa có đơn mới.")
    else:
        for order in pending:
            with st.expander(f"Mã {order['ID']} - {order['Nhà máy']}"):
                st.write(f"Khối lượng: {order['Khối lượng']} tấn")
                st.write(f"Lợi nhuận dự kiến: {order['Lợi nhuận đại lý']:,.0f} đ")

                if st.button(f"Nhận đơn {order['ID']}", key=order["ID"]):
                    order["Trạng thái"] = "Đang gom"
                    st.rerun()

# ====================================================
# ================== TÀI XẾ ==========================
# ====================================================

elif role == "Tài xế":

    st.subheader("🚛 Đơn đã gom đủ")

    ready = [o for o in st.session_state.orders if o["Trạng thái"] == "Đang gom"]

    if not ready:
        st.info("Chưa có chuyến sẵn sàng.")
    else:
        for order in ready:
            st.write(f"{order['ID']} - {order['Khối lượng']} tấn - {order['Nhà máy']}")

            if st.button(f"Nhận chuyến {order['ID']}"):
                order["Trạng thái"] = "Đang vận chuyển"
                st.rerun()

# ====================================================
# ================== ADMIN ===========================
# ====================================================

elif role == "Admin":

    st.subheader("📊 Tổng quan hệ thống")

    total_volume = sum(o["Khối lượng"] for o in st.session_state.orders)
    total_value = sum(o["Tổng tiền"] for o in st.session_state.orders)
    total_platform_revenue = sum(o["Phí sàn"] for o in st.session_state.orders)
    total_agent_profit = sum(o["Lợi nhuận đại lý"] for o in st.session_state.orders)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Tổng sản lượng (Tấn)", total_volume)
    col2.metric("Tổng giá trị giao dịch", f"{total_value:,.0f} đ")
    col3.metric("Doanh thu nền tảng", f"{total_platform_revenue:,.0f} đ")
    col4.metric("Tổng lợi nhuận đại lý", f"{total_agent_profit:,.0f} đ")

# ====================================================
# ================== LEDGER ==========================
# ====================================================

st.markdown("---")
st.subheader("📋 Sổ cái giao dịch")
df = pd.DataFrame(st.session_state.orders)
st.dataframe(df, use_container_width=True)
