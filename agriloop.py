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
                col_a, col_b = st.columns(2)
                f_name = col_a.text_input("Tên người bán", profile['username'])
                f_phone = col_b.text_input("Số điện thoại", profile.get('phone', ''))
                f_address = st.text_input("Địa chỉ ruộng", profile.get('address', 'Xã Phú Cường, Tam Nông'))
                f_weight = st.number_input("Nhập số lượng rơm (Tấn):", min_value=0.1, value=5.0, step=0.5, format="%.1f")
                
                f_method = st.radio("Hình thức giao nhận:", ["Đại lý lại gom", "Tôi tự chở lại kho bãi (Hub)"])
                
                if st.form_submit_button("Xác nhận Bán"):
                    # SỬA LỖI TẠI ĐÂY: Nếu chọn 'Đại lý lại gom' -> Đẩy thẳng trạng thái cho Tài xế chặng ngắn!
                    initial_status = "Chờ Tài xế chặng ngắn" if "Đại lý lại gom" in f_method else "Nông dân tự giao"
                    
                    st.session_state.farmer_offers.append({
                        "ID": f"FM{random.randint(1000,9999)}", "Order_ID": order["ID"],
                        "Tên": f_name, "SĐT": f_phone, "Địa chỉ": f_address, "Khối lượng": f_weight,
                        "Phương thức": f_method, "Trạng thái": initial_status
                    })
                    st.success("Đã ghi nhận đơn hàng! Hệ thống đang tự động điều phối xe đến ruộng của bạn.")
