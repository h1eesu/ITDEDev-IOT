import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from config import SHEET_KEY

def load_data_to_sheet(log_path, sheet_url, worksheet_name=None):
    """
    Đọc dữ liệu từ file JSON và lưu vào Google Sheets
    """
    # Đọc file JSON
    try:
        with open(log_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            print(f"Đã đọc dữ liệu từ {log_path}")
    except Exception as e:
        print(f"Lỗi khi đọc file JSON: {e}")
        return

    # Xác thực với Google Sheets API
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(SHEET_KEY, scope)
        gc = gspread.authorize(credentials)
    except Exception as e:
        print(f"Lỗi khi xác thực: {e}")
        return
    
    try:
        sheet = gc.open_by_url(sheet_url)
    except gspread.exceptions.SpreadsheetNotFound:
        print(f"lỗi khi mở sheet '{e}'")

    try:
        try:
            worksheet = sheet.worksheet(worksheet_name)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = sheet.add_worksheet(title=worksheet_name, rows=1000, cols=26)
    except Exception as e:
        print(f"Lỗi khi mở/tạo worksheet: {e}")
        return
    
    # Xử lý dữ liệu JSON và chuyển thành dạng bảng
    try:
        if isinstance(data, list):
            # Nếu data là một danh sách các đối tượng
            if all(isinstance(item, dict) for item in data):
                df = pd.DataFrame(data)
            else:
                print("Cấu trúc JSON không phù hợp (cần là danh sách các đối tượng)")
                return
        elif isinstance(data, dict):
            # Nếu data là một đối tượng duy nhất
            if 'attendance' in data and isinstance(data['attendance'], list):
                # Trường hợp đặc biệt cho dữ liệu điểm danh
                df = pd.DataFrame(data['attendance'])
            else:
                # Chuyển đổi đối tượng thành DataFrame
                df = pd.DataFrame([data])
        else:
            print("Cấu trúc JSON không được hỗ trợ")
            return
        
        print("Đã chuyển đổi dữ liệu JSON thành DataFrame")
    except Exception as e:
        print(f"Lỗi khi xử lý dữ liệu JSON: {e}")
        return
    
    # Cập nhật Google Sheet
    try:
        # Xóa dữ liệu cũ (nếu cần)
        worksheet.clear()
        
        # Thêm tiêu đề
        headers = df.columns.tolist()
        worksheet.append_row(headers)
        
        # Thêm dữ liệu
        values = df.values.tolist()
        for row in values:
            # Chuyển đổi tất cả các giá trị thành chuỗi để tránh lỗi
            row = [str(cell) if cell is not None else "" for cell in row]
            worksheet.append_row(row)
        
        print(f"Đã cập nhật thành công {len(values)} dòng dữ liệu lên Google Sheet")
    except Exception as e:
        print(f"Lỗi khi cập nhật Google Sheet: {e}")
        return
    
    print("Hoàn thành việc chuyển dữ liệu từ JSON lên Google Sheet")