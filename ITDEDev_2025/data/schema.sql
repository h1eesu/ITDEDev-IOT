-- Tạo bảng Users để lưu thông tin người dùng
CREATE TABLE IF NOT EXISTS Users (
    user_id INTEGER PRIMARY KEY,       -- ID người dùng
    name TEXT NOT NULL,                 -- Tên người dùng
    image_path TEXT NOT NULL,           -- Đường dẫn đến ảnh người dùng
    embedding BLOB                      -- Dữ liệu embedding (nếu có)
);