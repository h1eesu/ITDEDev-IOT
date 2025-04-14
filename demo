import cv2
import face_recognition
import os
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from Adafruit_IO import Client

# ========== GOOGLE SHEETS ==========
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client_gs = gspread.authorize(creds)
sheet = client_gs.open("AttendanceLog").sheet1

# ========== ADAFRUIT IO ==========
aio = Client("your_username", "your_aio_key")  # <-- Điền thông tin

# ========== LOAD FACES ==========
known_face_encodings = []
known_face_names = []

face_folder = "faces"
for filename in os.listdir(face_folder):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        path = os.path.join(face_folder, filename)
        image = face_recognition.load_image_file(path)
        encoding = face_recognition.face_encodings(image)
        if encoding:
            known_face_encodings.append(encoding[0])
            name = os.path.splitext(filename)[0]
            known_face_names.append(name)
        else:
            print(f"[!] Không tìm thấy khuôn mặt trong: {filename}")

# ========== CAMERA ==========
cap = cv2.VideoCapture(0)
detected_users = {}  # tránh ghi đè trong 5s

def mark_attendance(name):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[+] {name} - {now}")

    # Gửi lên Google Sheet
    try:
        sheet.append_row([name, now])
    except:
        print("[!] Lỗi ghi Google Sheet")

    # Gửi lên Adafruit IO
    try:
        aio.send("attendance-log", f"{name} - {now}")
    except:
        print("[!] Lỗi gửi Adafruit IO")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for face_encoding, face_location in zip(face_encodings, face_locations):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
        name = "Unknown"

        if True in matches:
            match_index = matches.index(True)
            name = known_face_names[match_index]

        top, right, bottom, left = [v * 4 for v in face_location]
        cv2.rectangle(frame, (left, top), (right, bottom), (0,255,0), 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,255,255), 2)

        if name not in detected_users or (datetime.now().timestamp() - detected_users[name]) > 5:
            mark_attendance(name)
            detected_users[name] = datetime.now().timestamp()

    cv2.imshow("Face Attendance", frame)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
