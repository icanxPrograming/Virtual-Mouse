# test_all_gestures.py
import cv2
import os
import time
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from src.hand_detector import HandDetector
from src.gesture_logic import HandRecog, HLabel, Gest

def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    detector = HandDetector(max_hands=1, detection_con=0.5, tracking_con=0.5)
    hand = HandRecog(HLabel.MAJOR)
    
    print("\n" + "="*60)
    print("TEST SEMUA GESTURE")
    print("="*60)
    print("Coba gesture berikut dan lihat deteksinya:")
    print("  1. Telunjuk + Tengah tegak        -> INDEX_MID_UP")
    print("  2. Telunjuk tekuk, tengah tegak   -> INDEX_FOLDED")
    print("  3. Telunjuk tegak, tengah tekuk   -> MID_FOLDED")
    print("  4. Tangan mengepal                -> FIST")
    print("  5. Telunjuk + Jempol rapat        -> PINCH_MAJOR")
    print("  6. Buka semua jari                -> PALM")
    print("  7. V gesture (2 jari)             -> V_GEST")
    print("="*60)
    print("Tekan 'q' untuk keluar\n")
    
    # Untuk tracking history
    gesture_history = []
    
    while True:
        success, frame = cap.read()
        if not success:
            continue
            
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        
        # Deteksi
        frame = detector.find_hands(frame, draw=True)
        lm_list = detector.find_position(frame)
        
        if lm_list:
            hand.update_hand_result(lm_list)
            raw_gesture = hand.get_raw_gesture()
            smoothed_gesture = hand.get_gesture()
            
            # Simpan history
            gesture_history.append(raw_gesture.name)
            if len(gesture_history) > 10:
                gesture_history.pop(0)
            
            # Tampilkan informasi lengkap
            # Background
            cv2.rectangle(frame, (10, 10), (500, 200), (0, 0, 0), -1)
            
            # Raw gesture
            cv2.putText(frame, f"RAW Gesture: {raw_gesture.name}", (20, 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            # Smoothed gesture
            color = (0, 255, 0) if raw_gesture == smoothed_gesture else (0, 165, 255)
            cv2.putText(frame, f"SMOOTHED: {smoothed_gesture.name}", (20, 75), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            
            # Finger states
            finger_text = f"Thumb:{1 if hand.thumb_state else 0} Index:{1 if hand.index_state else 0} Middle:{1 if hand.middle_state else 0} Ring:{1 if hand.ring_state else 0} Pinky:{1 if hand.pinky_state else 0}"
            cv2.putText(frame, finger_text, (20, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            
            # Finger bitmap
            cv2.putText(frame, f"Finger Bitmap: {hand.finger}", (20, 135), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            
            # Pinch distance
            pinch_dist = hand.get_dist(8, 4)
            hand_size = hand.get_dist(5, 17)
            ratio = pinch_dist / hand_size if hand_size > 0 else 1
            cv2.putText(frame, f"Pinch Distance: {pinch_dist:.1f} (Ratio: {ratio:.2f})", (20, 160), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            
            # History
            history_text = "History: " + " ".join(gesture_history[-5:])
            cv2.putText(frame, history_text, (20, 185), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
            
            # Visual feedback berdasarkan gesture
            if smoothed_gesture == Gest.INDEX_MID_UP:
                cv2.circle(frame, (w-50, 50), 30, (0, 255, 0), -1)
                cv2.putText(frame, "MOVE", (w-80, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            elif smoothed_gesture == Gest.INDEX_FOLDED:
                cv2.circle(frame, (w-50, 50), 30, (0, 255, 255), -1)
                cv2.putText(frame, "L-CLICK", (w-95, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            elif smoothed_gesture == Gest.MID_FOLDED:
                cv2.circle(frame, (w-50, 50), 30, (0, 165, 255), -1)
                cv2.putText(frame, "R-CLICK", (w-95, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            elif smoothed_gesture == Gest.FIST:
                cv2.circle(frame, (w-50, 50), 30, (0, 0, 255), -1)
                cv2.putText(frame, "DRAG", (w-85, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            elif smoothed_gesture in [Gest.PINCH_MAJOR, Gest.PINCH_MINOR]:
                cv2.circle(frame, (w-50, 50), 30, (255, 0, 255), -1)
                cv2.putText(frame, "PINCH", (w-85, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        cv2.imshow("Test All Gestures", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            gesture_history.clear()
            print("History cleared!")
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()