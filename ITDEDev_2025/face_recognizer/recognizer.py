import cv2
import face_recognition
import numpy as np
from PIL import Image
import urllib.request
import time
import os
import glob
import datetime
from config import LOG_PATH
import json

def get_frame_from_ipcam(ipcam_url):
    """
    Lấy một khung hình từ IP Webcam.
    """
    try:
        resp = urllib.request.urlopen(ipcam_url)
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        frame = cv2.imdecode(image, cv2.IMREAD_COLOR)
        return frame
    except Exception as e:
        print(f"Lỗi khi truy cập IP Webcam: {e}")
        return None

def load_embeddings_from_folder(embeddings_dir):
    """
    Tải các embedding từ thư mục chứa file .npy
    """
    known_face_encodings = []
    known_face_names = []
    
    # Kiểm tra thư mục có tồn tại
    if not os.path.exists(embeddings_dir):
        print(f"Lỗi: Thư mục {embeddings_dir} không tồn tại")
        return known_face_encodings, known_face_names
    
    # Tìm tất cả file .npy trong thư mục
    embedding_files = glob.glob(os.path.join(embeddings_dir, "*.npy"))
    
    if not embedding_files:
        print(f"Không tìm thấy file embedding nào trong thư mục {embeddings_dir}")
        return known_face_encodings, known_face_names
    
    print(f"Đang tải {len(embedding_files)} file embedding...")
    
    # Đọc từng file embedding
    for file_path in embedding_files:
        try:
            # Lấy tên người từ tên file (không bao gồm đường dẫn và phần mở rộng)
            name = os.path.splitext(os.path.basename(file_path))[0]
            
            # Tải embedding từ file
            embedding = np.load(file_path)
            
            # Thêm vào danh sách
            known_face_encodings.append(embedding)
            known_face_names.append(name)
            
            print(f"Đã tải embedding của {name}")
        except Exception as e:
            print(f"Lỗi khi tải file {file_path}: {e}")
    
    return known_face_encodings, known_face_names

def recognize_faces(ipcam_url, embeddings_dir, tolerance=0.6):
    """
    Nhận diện khuôn mặt từ IP Webcam và so sánh với embedding trong thư mục.
    Chỉ nhận diện và xử lý một khuôn mặt duy nhất (khuôn mặt lớn nhất) trong mỗi khung hình.
    Hiển thị khung màu xanh lá khi điểm danh thành công, màu đỏ khi không thành công.
    Hiển thị thêm thời gian điểm danh.
    """
    # Tải các embedding từ thư mục
    known_face_encodings, known_face_names = load_embeddings_from_folder(embeddings_dir)
    
    if not known_face_encodings:
        print("Không có dữ liệu embedding để so sánh.")
        return
    
    print(f"Đang kết nối đến IP Webcam tại {ipcam_url}...")
    print("Đang bắt đầu nhận diện khuôn mặt và điểm danh... Nhấn 'q' để thoát.")
    
    # Lưu trạng thái điểm danh để tránh thông báo liên tục
    attendance_status = {name: False for name in known_face_names}
    attendance_times = {}
    attendance_successful = False
    last_attendance_time = {}
    attendance_log = []
    log_file = LOG_PATH

    if not os.path.exists(log_file):
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)

    while True:
        # Lấy khung hình từ IP Webcam
        frame = get_frame_from_ipcam(ipcam_url)
        
        if frame is None:
            print("Không thể lấy khung hình từ IP Webcam. Đang thử lại...")
            time.sleep(1)
            continue

        #thời gian
        current_time = datetime.datetime.now()
        current_time_str = current_time.strftime("%H:%M:%S")
        current_date_str = current_time.strftime("%d-%m-%Y")

        cv2.putText(frame, f"Thời gian: {current_time_str}", (frame.shape[1] -250, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_small_frame)
        current_frame_attendance = False

        # Hiển thị thông tin debug
        cv2.putText(frame, f"Faces detected: {len(face_locations)}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Hiển thị thông tin điểm danh
        attendance_text = "Đã điểm danh: " + ", ".join([name for name, status in attendance_status.items() if status])
        cv2.putText(frame, attendance_text, (10, frame.shape[0] - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Nếu có khuôn mặt được phát hiện
        if len(face_locations) > 0:
            # tìm khuôn mặt lớn nhất trong khung hình(người gần cam nhất)
            face_areas = [(right - left) * (bottom - top) for (top, right, bottom, left) in face_locations]
            largest_face_index = face_areas.index(max(face_areas))
            face_location = face_locations[largest_face_index]

            # mã hóa khuôn mặt đã chọn
            face_encodings = face_recognition.face_encodings(rgb_small_frame, [face_location])
            
            if face_encodings:
                face_encoding = face_encodings[0]
                top, right, bottom, left = face_location
                # So sánh với khuôn mặt đã biết
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance)
                name = "Unknown"
                
                # Tìm khuôn mặt giống nhất
                if len(known_face_encodings) > 0:
                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    confidence = 1 - face_distances[best_match_index]

                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]                        
                        # Kiểm tra xem người này đã được điểm danh chưa
                        current_time = time.time()

                        if not attendance_status[name]:
                            # Đánh dấu đã điểm danh
                            user_id, user_name = name.split("_", 1)
                            attendance_status[name] = True
                            last_attendance_time[name] = current_time
                            attendance_times[name] = f"{current_time_str} - {current_date_str}"

                            attendance_log.append({
                                "user_id": user_id,
                                "name": user_name,
                                "time": current_time_str,
                                "date": current_date_str
                            })
                            with open(log_file, "w", encoding="utf-8") as f:
                                json.dump(attendance_log, f, indent=4, ensure_ascii=False)
                            print(f"\n✅ {name} đã được điểm danh! (Độ tin cậy: {confidence:.2f})")
                        elif current_time - last_attendance_time.get(name, 0) > 60:  # Thông báo lại sau 60 giây
                            print(f"\n🔄 {name} đã được phát hiện lại! (Độ tin cậy: {confidence:.2f})")
                            last_attendance_time[name] = current_time
                            current_frame_attendance = True
                        else:
                            current_frame_attendance = True
                
                # Nhân tọa độ lên vì đã thu nhỏ khung hình
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4
                
                # Chọn màu dựa trên việc đã điểm danh hay chưa
                if name != "Unknown" and attendance_status[name]:
                    color = (0, 255, 0)  # Xanh lá cho người đã điểm danh
                else:
                    color = (0, 0, 255)  # Đỏ cho người chưa nhận diện được
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                
                # Vẽ nhãn tên với độ tin cậy nếu nhận diện được
                label = name
                if name != "Unknown":
                    label = f"{name} ({confidence:.2f})"
                    
                    # Vẽ trạng thái điểm danh
                    status = "Đã điểm danh" if attendance_status[name] else "Chưa điểm danh"
                    cv2.putText(frame, status, (left, top - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
                #Hiển thị thời gian nếu đã điểm danh
                if attendance_status[name] and name in attendance_times:
                    time_text = f"Thời gian: {attendance_times[name]}"
                    cv2.putText(frame, time_text, (left, top - 10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                cv2.putText(frame, label, (left + 6, bottom - 6), 
                           cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

                if len(face_locations) > 1:
                    cv2.putText(frame, f"Chỉ nhận diện khuôn mặt lớn nhất!", 
                              (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 140, 255), 2)
                attendance_successful= current_frame_attendance
        
        # border_thickness = 15
        # border_color = (0, 255, 0) if attendance_successful else (0, 0, 255)  # Xanh lá nếu điểm danh thành công, đỏ nếu không
        # cv2.line(frame, (0, 0), (frame.shape[1], 0), border_color, border_thickness)
        # cv2.line(frame, (0, frame.shape[0]-1), (frame.shape[1], frame.shape[0]-1), border_color, border_thickness)
        # cv2.line(frame, (0, 0), (0, frame.shape[0]), border_color, border_thickness)
        # cv2.line(frame, (frame.shape[1]-1, 0), (frame.shape[1]-1, frame.shape[0]), border_color, border_thickness)
        cv2.imshow('Face Recognition & Attendance', frame)
        
        # Thoát nếu nhấn phím 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Dọn dẹp
    cv2.destroyAllWindows()
    
    # Hiển thị báo cáo điểm danh cuối cùng
    print("\n===== BÁO CÁO ĐIỂM DANH =====")
    for name, status in attendance_status.items():
        status_text = "Có mặt" if status else "Vắng mặt"
        print(f"{name}: {status_text}")
    print("=============================")