import streamlit as st
import pandas as pd
import re
import io

# Cấu hình trang web
st.set_page_config(page_title="Tool Chuyển Đổi J&T", layout="centered")
st.title("🚛 Tool Chuyển Đổi Đơn Hàng J&T")
st.write("Tải file 'IN ĐƠN TÚI LỘC' lên để chuyển đổi sang file mẫu J&T tự động.")

# Hàm xử lý COD (giữ nguyên logic cũ)
def extract_cod(product_str):
    if pd.isna(product_str):
        return 0
    match = re.search(r'(\d+)[kK]', str(product_str))
    if match:
        try:
            return int(match.group(1)) * 1000
        except:
            return 0
    return 0

# Widget để upload file
uploaded_file = st.file_uploader("Chọn file Excel nguồn (IN ĐƠN TÚI LỘC...)", type=['xlsx', 'xls'])

if uploaded_file is not None:
    try:
        # Đọc file nguồn
        df_source = pd.read_excel(uploaded_file, header=None)

        # Tạo DataFrame kết quả theo chuẩn J&T
        # Cấu trúc cột dựa trên file mẫu bạn cung cấp
        jt_columns = [
            'Mã đơn hàng riêng', 'Tên người nhận (*)', 'Điện thoại (*)',
            'Địa chỉ (*)', 'Tỉnh/Thành phố', 'Quận/huyện', 'Phường/xã',
            'Tên hàng hóa (*)', 'Giá trị hàng hóa\n(Nhập nếu mua bảo hiểm)',
            'Tiền thu hộ\n(COD)', 'Trọng lượng\n(kg) (*)', 'Kích thước',
            'Unnamed: 12', 'Unnamed: 13', 'Số kiện hàng (*)', 'Phí giao hàng hộ',
            'Ghi chú'
        ]

        df_result = pd.DataFrame(columns=jt_columns)

        # Mapping dữ liệu
        df_result['Tên người nhận (*)'] = df_source[1]
        df_result['Điện thoại (*)'] = df_source[2].apply(lambda x: str(x).replace('.0', '') if pd.notnull(x) else x)
        df_result['Địa chỉ (*)'] = df_source[3]
        df_result['Tên hàng hóa (*)'] = df_source[4]

        # Xử lý logic COD
        df_result['Tiền thu hộ\n(COD)'] = df_source[4].apply(extract_cod)

        # Hiển thị bản xem trước
        st.success("Đã xử lý xong! Dưới đây là 5 dòng đầu tiên:")
        st.dataframe(df_result[['Tên người nhận (*)', 'Điện thoại (*)', 'Tiền thu hộ\n(COD)']].head())

        # Xử lý để tải file về (Lưu vào bộ nhớ đệm thay vì lưu ra ổ cứng)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_result.to_excel(writer, index=False, sheet_name='Đơn hàng')

        # Nút Download
        st.download_button(
            label="📥 Tải file kết quả về máy",
            data=buffer,
            file_name="File_Import_JnT_Final.xlsx",
            mime="application/vnd.ms-excel"
        )

    except Exception as e:
        st.error(f"Có lỗi xảy ra: {e}")
        st.info("Vui lòng đảm bảo bạn upload đúng file mẫu Excel (.xlsx)")
