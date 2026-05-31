# src/hand_detector.py
import cv2
import mediapipe as mp
import os
import urllib.request

class HandDetector:
    def __init__(self, mode=False, max_hands=2, detection_con=0.7, tracking_con=0.7):
        # 1. Tentukan nama file model lokal
        model_filename = "hand_landmarker.task"
        
        # 2. Otomatis unduh jika file tidak ditemukan
        if not os.path.exists(model_filename):
            print(f"Mengunduh model '{model_filename}'...")
            url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
            urllib.request.urlretrieve(url, model_filename)
            print("Unduhan selesai!")

        # 3. Inisialisasi MediaPipe Tasks API
        BaseOptions = mp.tasks.BaseOptions
        HandLandmarker = mp.tasks.vision.HandLandmarker
        HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        self.options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_filename),
            running_mode=VisionRunningMode.IMAGE,
            num_hands=max_hands,
            min_hand_detection_confidence=detection_con,
            min_hand_presence_confidence=tracking_con
        )
        
        self.detector = HandLandmarker.create_from_options(self.options)
        self.results = None

    def find_hands(self, frame, draw=True):
        """Mendeteksi tangan menggunakan MediaPipe Tasks API."""
        # Konversi BGR ke RGB jika perlu
        if frame.shape[2] == 3:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        else:
            rgb_frame = frame
            
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        self.results = self.detector.detect(mp_image)
        
        # Gambar landmark untuk visualisasi
        if self.results and self.results.hand_landmarks and draw:
            h, w, _ = frame.shape
            for hand_idx, hand_landmarks in enumerate(self.results.hand_landmarks):
                # Dapatkan label tangan
                hand_label = self.results.handedness[hand_idx][0].category_name
                color = (0, 255, 0) if hand_label == "Right" else (255, 0, 0)
                
                for lm in hand_landmarks:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(frame, (cx, cy), 3, color, cv2.FILLED)
        return frame

    def find_position(self, frame, hand_no=0):
        """Mengambil koordinat landmark untuk tangan tertentu."""
        lm_list = []
        if self.results and self.results.hand_landmarks and len(self.results.hand_landmarks) > hand_no:
            my_hand = self.results.hand_landmarks[hand_no]
            h, w, _ = frame.shape
            
            for id, lm in enumerate(my_hand):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append([id, cx, cy])
        return lm_list