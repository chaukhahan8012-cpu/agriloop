import streamlit as st
import pandas as pd

st.set_page_config(page_title="AgriLoop MVP", layout="wide")

# ========================
# CẤU HÌNH GIÁ
# ========================
PRICE_PER_TON = 800000
PRICE_BUY_PER_TON = 650000
PLATFORM_FEE_RATE = 0.05

# ========================
# SESSION
# ========================
if "orders" not in st.session_state:
    st.session_state.orders = []

# ========================
# SIDEBAR
# ========================
st.sidebar.title("AgriLoop MVP")
role = st.sidebar.radio(
    "Chọn vai trò:",
    ["Nhà máy", "Đại lý", "HTX vận tải", "Admin"]
)

st.title(f"AgriLoop - {role}")

# =================================================
# NHÀ MÁY
# =================================================
if role == "Nhà máy":

    st.subheader("Tạo đơn thu mua")

    factory = st.text_input("Tên nhà máy")
    weight = st.number_input("Khối lượng (tấn)", min_value=1, value=10)

    base_cost = weight * PRICE_PER_TON
    platform_fee = base_cost * PLATFORM_FEE_RATE
    total = base_cost + platform_fee

    st.write("Tiền rơm:", f"{base_cost:,.0f} đ")
    st.write("Phí sàn:", f"{platform_fee:,.0f} đ")
    st.success(f"Tổng thanh toán: {total:,.0f} đ")

    if st.button("Đăng đơn"):

        new_order = {
            "ID": f"AL{len(st.session_state.orders)+1}",
            "Nhà máy": factory,
            "Khối lượng": weight,
            "Trạng thái": "Chờ xác nhận",
            "Tổng tiền": total,
            "Phí sàn": platform_fee,
            "Lợi nhuận đại lý": weight * (PRICE_PER_TON - PRICE_BUY_PER_TON)
        }

        st.session_state.orders.append(new_order)
        st.success("Đã tạo đơn!")

# =================================================
# ĐẠI LÝ
# =================================================
elif role == "Đại lý":

    st.subheader("Đơn chờ xác nhận")

    for i, order in enumerate(st.session_state.orders):

        if order["Trạng thái"] == "Chờ xác nhận":

            st.write(f"{order['ID']} - {order['Khối lượng']} tấn")

            if st.button(f"Xác nhận {order['ID']}", key=f"confirm_{i}"):
                st.session_state.orders[i]["Trạng thái"] = "Đang thu gom"
                st.experimental_rerun()

        elif order["Trạng thái"] == "Đang thu gom":

            st.write(f"{order['ID']} - Đang thu gom")

            if st.button(f"Hoàn tất {order['ID']}", key=f"finish_{i}"):
                st.session_state.orders[i]["Trạng thái"] = "Chờ kiểm định"
                st.experimental_rerun()

# =================================================
# HTX
# =================================================
elif role == "HTX vận tải":

    st.subheader("Kiểm định")

    for i, order in enumerate(st.session_state.orders):

        if order["Trạng thái"] == "Chờ kiểm định":

            st.write(f"{order['ID']} - {order['Khối lượng']} tấn")

            moisture = st.slider(
                f"Độ ẩm {order['ID']}",
                10, 40, 20,
                key=f"moist_{i}"
            )

            if st.button(f"Kiểm tra {order['ID']}", key=f"qc_{i}"):

                if moisture <= 25:
                    st.session_state.orders[i]["Trạng thái"] = "Đang vận chuyển"
                else:
                    st.session_state.orders[i]["Trạng thái"] = "Không đạt"

                st.experimental_rerun()

# =================================================
# ADMIN
# =================================================
elif role == "Admin":

    st.subheader("Tổng quan")

    total_volume = 0
    total_value = 0
    total_platform = 0

    for i, order in enumerate(st.session_state.orders):

        if order["Trạng thái"] == "Đang vận chuyển":

            if st.button(f"Xác nhận giao {order['ID']}", key=f"deliver_{i}"):
                st.session_state.orders[i]["Trạng thái"] = "Hoàn tất"
                st.experimental_rerun()

        if order["Trạng thái"] == "Hoàn tất":
            total_volume += order["Khối lượng"]
            total_value += order["Tổng tiền"]
            total_platform += order["Phí sàn"]

    st.metric("Tổng sản lượng", total_volume)
    st.metric("Tổng giao dịch", f"{total_value:,.0f} đ")
    st.metric("Doanh thu nền tảng", f"{total_platform:,.0f} đ")

# =================================================
# LEDGER
# =================================================
st.markdown("---")
st.subheader("Sổ cái")

if st.session_state.orders:
    df = pd.DataFrame(st.session_state.orders)
    st.dataframe(df, use_container_width=True)
else:
    st.write("Chưa có đơn nào.")
