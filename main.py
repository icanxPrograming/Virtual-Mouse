# main.py
import cv2
import numpy as np
import os
import time

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['ABSL_LOGGING_MIN_LOG_LEVEL'] = '3'

from config.settings import *
from src.hand_detector import HandDetector
from src.gesture_logic import HandRecog, HLabel, Gest
from src.mouse_controller import MouseController

def main():
    cap = cv2.VideoCapture(CAM_ID)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    detector = HandDetector(max_hands=2, detection_con=MIN_DETECTION_CONFIDENCE, 
                           tracking_con=MIN_TRACKING_CONFIDENCE)
    mouse = MouseController()
    
    hand_major = HandRecog(HLabel.MAJOR)
    hand_minor = HandRecog(HLabel.MINOR)
    
    # Untuk notifikasi
    last_action_time = 0
    last_action_text = ""
    last_action_pos = (0, 0)
    
    print("\n" + "="*50)
    print("AI VIRTUAL MOUSE - ENHANCED EDITION")
    print("="*50)
    print("GESTURE GUIDE:")
    print("  ✌️  Telunjuk + Tengah tegak  -> Move cursor")
    print("  ☝️  Telunjuk tekuk           -> Left Click")
    print("  ✌️  Tengah tekuk             -> Right Click")
    print("  ✊  Tangan mengepal          -> Drag & Drop")
    print("  🤏  Pinch (Kanan)            -> Volume/Brightness")
    print("  🤏  Pinch (Kiri)             -> Scroll")
    print("  ✌️  V-Gesture                -> Double Click")
    print("="*50)
    print("Tekan 'q' untuk keluar\n")

    while cap.isOpened():
        success, frame = cap.read()
        if not success or frame is None:
            continue

        frame = cv2.flip(frame, 1)
        h_cam, w_cam, _ = frame.shape
        
        # Deteksi tangan - SET draw=True untuk melihat landmark dari detector
        frame = detector.find_hands(frame, draw=True)  # <-- UBAH ke True
        
        # Area interaksi
        cv2.rectangle(frame, (FRAME_REDUCTION, FRAME_REDUCTION), 
                      (w_cam - FRAME_REDUCTION, h_cam - FRAME_REDUCTION), (255, 0, 255), 2)
        
        results = detector.results
        lm_major = []
        lm_minor = []

        if results and results.hand_landmarks and len(results.hand_landmarks) > 0:
            # Pisahkan landmark tangan kiri dan kanan
            for idx, hand_landmarks in enumerate(results.hand_landmarks):
                hand_label_str = results.handedness[idx][0].category_name
                
                temp_lm_list = []
                for id_lm, lm in enumerate(hand_landmarks):
                    cx, cy = int(lm.x * w_cam), int(lm.y * h_cam)
                    temp_lm_list.append([id_lm, cx, cy])
                    
                    # Gambar landmark tambahan dengan warna berbeda per jari
                    if id_lm == 4:  # Thumb
                        color = (0, 0, 255)
                        radius = 6
                    elif id_lm == 8:  # Index
                        color = (0, 165, 255)
                        radius = 5
                    elif id_lm == 12:  # Middle
                        color = (0, 255, 255)
                        radius = 5
                    elif id_lm == 16:  # Ring
                        color = (0, 255, 0)
                        radius = 4
                    elif id_lm == 20:  # Pinky
                        color = (255, 0, 0)
                        radius = 4
                    else:
                        color = (0, 255, 0)
                        radius = 3
                    
                    cv2.circle(frame, (cx, cy), radius, color, cv2.FILLED)
                
                if hand_label_str == "Right":
                    lm_major = temp_lm_list
                else:
                    lm_minor = temp_lm_list

            # Update gesture logic
            hand_major.update_hand_result(lm_major)
            hand_minor.update_hand_result(lm_minor)

            # Proses gesture - TAMPILKAN RAW DAN SMOOTHED
            raw_gest_major = hand_major.get_raw_gesture() if hasattr(hand_major, 'get_raw_gesture') else hand_major.get_gesture()
            raw_gest_minor = hand_minor.get_raw_gesture() if hasattr(hand_minor, 'get_raw_gesture') else hand_minor.get_gesture()

            gest_minor = hand_minor.get_gesture()
            gest_major = hand_major.get_gesture()

            # DEBUG: Print ke console untuk monitoring
            if len(lm_major) > 0:
                print(f"\r[MAJOR] Raw: {raw_gest_major.name:15} -> Smoothed: {gest_major.name:15} | I:{hand_major.index_state} M:{hand_major.middle_state} | Dist: {hand_major.get_dist(8,4):.1f}", end="")

            # Tampilkan di frame - BAIK RAW MAUPUN SMOOTHED
            cv2.rectangle(frame, (10, 10), (500, 130), (0, 0, 0), -1)
            cv2.putText(frame, f"Raw Gesture: {raw_gest_major.name}", (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
            cv2.putText(frame, f"Smoothed: {gest_major.name}", (20, 65), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Fingers: T:{hand_major.thumb_state} I:{hand_major.index_state} M:{hand_major.middle_state}", (20, 90), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            cv2.putText(frame, f"Pinch Dist: {hand_major.get_dist(8,4):.1f}", (20, 115), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

            # Prioritas gesture untuk kontrol
            # Gunakan smoothed gesture untuk kontrol
            if gest_minor == Gest.PINCH_MINOR:
                active_hand = "LEFT"
                gesture = gest_minor
                mouse.process_gesture_controls(gesture, lm_minor, w_cam, h_cam, FRAME_REDUCTION)
            else:
                active_hand = "RIGHT"
                gesture = gest_major
                mouse.process_gesture_controls(gesture, lm_major, w_cam, h_cam, FRAME_REDUCTION)
            
            # Tampilkan informasi di layar - PASTIKAN MENGGUNAKAN VARIABLE gesture yang benar
            gesture_names = {
                Gest.INDEX_MID_UP: "👉 MOVE MOUSE",
                Gest.INDEX_FOLDED: "🖱️ LEFT CLICK",
                Gest.MID_FOLDED: "🖱️ RIGHT CLICK",
                Gest.FIST: "✊ DRAG & DROP",
                Gest.PINCH_MAJOR: "🎛️ VOLUME/BRIGHTNESS",
                Gest.PINCH_MINOR: "📜 SCROLL",
                Gest.V_GEST: "🔁 DOUBLE CLICK",
                Gest.PALM: "🖐️ PALM"
            }
            
            action_text = gesture_names.get(gesture, f"Gesture: {gesture.name}")
            
            # Background untuk teks
            cv2.rectangle(frame, (10, 10), (450, 100), (0, 0, 0), -1)
            cv2.putText(frame, f"Tangan: {active_hand}", (20, 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, action_text, (20, 75), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            # Tampilkan status jari (gunakan hand yang aktif)
            if active_hand == "RIGHT":
                hand = hand_major
            else:
                hand = hand_minor
                
            finger_status = f"T:{1 if hand.thumb_state else 0} I:{1 if hand.index_state else 0} M:{1 if hand.middle_state else 0} R:{1 if hand.ring_state else 0} P:{1 if hand.pinky_state else 0}"
            cv2.putText(frame, finger_status, (w_cam - 220, 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            
            # Tampilkan nilai finger bitmap
            cv2.putText(frame, f"Finger: {hand.finger}", (w_cam - 220, 65), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            
            # Tampilkan notifikasi aksi
            if gesture in [Gest.INDEX_FOLDED, Gest.MID_FOLDED, Gest.V_GEST]:
                last_action_time = time.time()
                last_action_text = action_text
                last_action_pos = (w_cam//2 - 100, h_cam//2)
            
            if time.time() - last_action_time < 0.8:
                # Buat background untuk teks notifikasi
                cv2.rectangle(frame, (last_action_pos[0] - 10, last_action_pos[1] - 40), 
                             (last_action_pos[0] + 250, last_action_pos[1] + 10), (0, 0, 0), -1)
                cv2.putText(frame, last_action_text, last_action_pos, 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)
        
        else:
            cv2.putText(frame, "Tidak ada tangan terdeteksi", (20, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            mouse.prev_hand = None
        
        # Panduan singkat
        cv2.rectangle(frame, (10, h_cam - 80), (w_cam - 10, h_cam - 10), (0, 0, 0), -1)
        cv2.putText(frame, "Guide: ✌️ Move | ☝️ Left | ✌️ Right | ✊ Drag | 🤏 Pinch", 
                   (20, h_cam - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        cv2.imshow("AI Virtual Mouse - Enhanced Control", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            print("\n[INFO] Reset mouse controller")
            mouse = MouseController()

    cap.release()
    cv2.destroyAllWindows()
    print("\n[INFO] Program terminated")

if __name__ == "__main__":
    main()