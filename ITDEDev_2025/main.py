from face_recognizer.save_image import save_image_paths
from face_recognizer.embedding import process_faces
from face_recognizer.recognizer import recognize_faces
from config import IP_WEBCAM_URL, DB_PATH, EMBEDDINGS_NPY_PATH, LOG_PATH, SHEET_URL
from cloud.google_sheet import load_data_to_sheet
import os

def main():
    load_data_to_sheet(LOG_PATH, SHEET_URL, worksheet_name="Attendance")
if __name__ == "__main__":
    main()