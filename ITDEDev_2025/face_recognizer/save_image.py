from data.query import insert_image_path
from PIL import Image
import os
import hashlib

def save_image_paths(folder_path):
    """
    Lưu đường dẫn ảnh vào database
    :param folder_path: Đường dẫn thư mục chứa ảnh
    """
    supported_extensions = ('.jpg', '.jpeg', '.png')
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(supported_extensions)]

    if not image_files:
        print("⚠️ Không tìm thấy ảnh trong thư mục.")
        return

    print(f"\n🔍 Đang lưu đường dẫn {len(image_files)} ảnh vào database...")

    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        name = os.path.splitext(image_file)[0].split('_')[0]
        
        # Tạo hash để tránh trùng lặp
        with open(image_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        
        insert_image_path(name, image_path)
        print(f"[+] Đã lưu đường dẫn: {image_path} và user_name: {name}")