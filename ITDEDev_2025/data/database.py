import sqlite3
import os
from config import DB_PATH, DB_NAME
import numpy as np

def connect_db(DB_PATH):
    conn = None
    try: 
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"Lỗi kết nối đến cơ sở dữ liệu: {e}")
    return conn

def close_db(DB_PATH):
    conn =None
    try:
        if conn == sqlite3.connect(DB_PATH):
            conn.close()
    except sqlite3.Error as e:
        print(f"Lỗi khi đóng kết nối đến cơ sở dữ liệu: {e}")

def create_database_from_schema():
    from config import SCHEMA_PATH
    # Kết nối với cơ sở dữ liệu SQLite (nếu chưa có thì sẽ tạo mới)
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Đọc nội dung của file schema.sql
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as schema_file:
            schema_sql = schema_file.read()

        # Thực thi các câu lệnh SQL từ file schema.sql
        cursor.executescript(schema_sql)
        if conn:
            print("Cơ sở dữ liệu đã được tạo thành công từ schema.")

        # Commit và đóng kết nối
        conn.commit()
        conn.close()

    except sqlite3.Error as e:
        print(f"Lỗi khi tạo cơ sở dữ liệu từ schema: {e}")

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

# lấy embedding từ db chuyển thành file .npy
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
        cursor.execute("SELECT user_id, name,  embedding FROM Users WHERE embedding IS NOT NULL")
        rows = cursor.fetchall()
        
        known_face_encodings = []
        known_face_user_ids = []
        
        for user_id, name, embedding_blob in rows:
            if embedding_blob:
                # Chuyển đổi BLOB thành numpy array
                face_encoding = np.frombuffer(embedding_blob, dtype=np.float64)
                # face_recognition thường sử dụng 128 chiều cho mỗi encoding
                face_encoding = face_encoding.reshape((1, -1))[0]
                enbedding_file = os.path.join(EMBEDDINGS_NPY_PATH, f"{user_id}_{name}.npy")
                np.save(enbedding_file, face_encoding)
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