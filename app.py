import streamlit as st
import pandas as pd
import re
import io

# Cấu hình trang
st.set_page_config(page_title="Tool Chuyển Đổi J&T Pro", layout="centered")
st.title("🚛 Tool Chuyển Đổi Đơn Hàng J&T")

# Hàm xử lý COD an toàn hơn
def extract_cod(product_str):
    # Nếu ô sản phẩm bị trống hoặc không phải chuỗi ký tự -> Trả về 0
    if pd.isna(product_str) or str(product_str).strip() == "":
        return 0
    
    # Tìm giá tiền (số + k/K)
    match = re.search(r'(\d+)[kK]', str(product_str))
    if match:
        try:
            return int(match.group(1)) * 1000
        except:
            return 0
    return 0

# Upload file
uploaded_file = st.file_uploader("Chọn file Excel (Hỗ trợ 1000+ dòng)", type=['xlsx', 'xls'])

if uploaded_file is not None:
    try:
        # Đọc file nguồn
        df_source = pd.read_excel(uploaded_file, header=None)
        
        # --- BƯỚC LỌC RÁC QUAN TRỌNG ---
        # 1. Xóa các dòng mà cả dòng đều trống (thường hay bị ở cuối file)
        df_source = df_source.dropna(how='all')
        
        # 2. Xóa các dòng mà cột Tên (cột 1) hoặc SĐT (cột 2) bị trống
        # Vì đơn hàng không có tên/sđt thì không lên đơn được
        df_source = df_source.dropna(subset=[1, 2])
        
        # Hiển thị số lượng đơn tìm thấy
        row_count = len(df_source)
        st.info(f"Đã tìm thấy {row_count} đơn hàng hợp lệ.")

        if row_count > 0:
            # Chuẩn bị DataFrame kết quả
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
            
            # Xử lý SĐT: Chuyển về chuỗi, xóa .0, xóa khoảng trắng thừa
            df_result['Điện thoại (*)'] = df_source[2].apply(
                lambda x: str(x).replace('.0', '').strip() if pd.notnull(x) else x
            )
            
            df_result['Địa chỉ (*)'] = df_source[3]
            df_result['Tên hàng hóa (*)'] = df_source[4]
            
            # Tính COD
            df_result['Tiền thu hộ\n(COD)'] = df_source[4].apply(extract_cod)
            
            # Mặc định trọng lượng (J&T yêu cầu) - Để 0.2kg để tránh lỗi khi đẩy đơn
            df_result['Trọng lượng\n(kg) (*)'] = 0.5
            
            # Hiển thị kết quả
            st.success("Xử lý thành công!")
            st.dataframe(df_result[['Tên người nhận (*)', 'Điện thoại (*)', 'Tiền thu hộ\n(COD)']].head())
            
            # Tải về
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_result.to_excel(writer, index=False, sheet_name='Đơn hàng')
                
            st.download_button(
                label=f"📥 Tải file {row_count} đơn hàng về",
                data=buffer,
                file_name="File_Import_JnT_Final.xlsx",
                mime="application/vnd.ms-excel"
            )
        else:
            st.warning("File tải lên không có dữ liệu hợp lệ (Trống tên hoặc SĐT).")

    except Exception as e:
        st.error(f"Lỗi khi đọc file: {e}")
