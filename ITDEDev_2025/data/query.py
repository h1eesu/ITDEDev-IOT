import sqlite3
import os
from . import database
import numpy as np
from config import DB_PATH

#lấy đường dẫn ảnh trong db
def get_images():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, name, image_path FROM Users")
    images = cursor.fetchall()
    conn.close()
    return images # trả về dạng tuple

# lưu embedding vào database
def insert_embedding(user_id, embedding_blob):
    """
    Lưu embedding dưới dạng BLOB vào database
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE Users SET embedding = ? WHERE user_id = ?",
            (sqlite3.Binary(embedding_blob), user_id)  # Sử dụng sqlite3.Binary cho dữ liệu BLOB
        )
    except sqlite3.Error as e:
        print(f"Lỗi khi lưu embedding vào database: {e}")
    finally:
        conn.commit()
        conn.close()

# lưu đường dẫn ảnh vào database
def insert_image_path(name, image_path):
    """
    Lưu đường dẫn ảnh vào database
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Users (name, image_path) VALUES (?,?)",
            (name, image_path) 
        )
    except sqlite3.Error as e:
        print(f"Lỗi khi lưu đường dẫn ảnh vào database: {e}")
    finally:
        conn.commit()
        conn.close()

# lấy embedding từ db
def get_embeddings(DB_PATH):
    """
    Lấy embeddings từ cơ sở dữ liệu và chuyển từ BLOB thành numpy array
    Lưu thành các file .npy trong *data/embeddings_npy
    Returns:
        tuple: (list của các face_encodings, list của các tên tương ứng)
    """
    # tạo folder nếu chưa có
    from config import EMBEDDINGS_NPY_PATH
    if not os.path.exists(EMBEDDINGS_NPY_PATH):
        os.makedirs(EMBEDDINGS_NPY_PATH)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT user_id, embedding FROM Users WHERE embedding IS NOT NULL")
        rows = cursor.fetchall()
        
        known_face_encodings = []
        known_face_user_ids = []
        
        for user_id, embedding_blob in rows:
            if embedding_blob:
                # Chuyển đổi BLOB thành numpy array
                face_encoding = np.frombuffer(embedding_blob, dtype=np.float64)
                # face_recognition thường sử dụng 128 chiều cho mỗi encoding
                # Kiểm tra và định hình lại nếu cần
                if len(face_encoding) == 128:
                    known_face_encodings.append(face_encoding)
                    known_face_user_ids.append(user_id)
                else:
                    print(f"Bỏ qua embedding không hợp lệ cho {user_id}: kích thước {len(face_encoding)}")
        
        print(f"Đã tải {len(known_face_encodings)} embeddings từ cơ sở dữ liệu")
        return known_face_encodings, known_face_user_ids
    except sqlite3.Error as e:
        print(f"Lỗi khi truy vấn cơ sở dữ liệu: {e}")
        return [], []
    finally:
        conn.close()