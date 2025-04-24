import numpy as np
from PIL import Image
import face_recognition
from data.query import insert_embedding, get_images

def process_faces():
    """
    lấy đường dẫn từ DB,trích xuất embedding và lưu vào DB
    """
    image_records = get_images()  # Lấy danh sách ảnh từ database
    if not image_records:
        print("⚠️ Không tìm thấy đường dẫn ảnh trong database.")
        return
    print(f"🔍 Đang xử lý {len(image_records)} ảnh trong database...")

    processed_count = 0

    for record in image_records:
        user_id, name, image_path = record
        try:
            image = Image.open(image_path)
            image_array = np.array(image)
        except Exception as e:
            print(f"❌ Lỗi khi đọc ảnh {image_path}: {e}")
            continue

        face_locations = face_recognition.face_locations(image_array)
        face_encodings = face_recognition.face_encodings(image_array, face_locations)

        if not face_encodings:
            print(f"⚠️ Không phát hiện khuôn mặt trong: {image_path}")
            continue

        for i, encoding in enumerate(face_encodings):
            embedding_blob = encoding.tobytes()
            insert_embedding(user_id, embedding_blob)
            processed_count += 1
            print(f"User ID: {user_id} - Tên {name} - Đã lưu embedding cho khuôn mặt thứ {i + 1} trong ảnh: {image_path}")

    print(f"\n✅ Đã xử lý và lưu {processed_count} embedding vào cơ sở dữ liệu")