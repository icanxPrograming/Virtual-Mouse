# src/mouse_controller.py
import pyautogui
import numpy as np
import time
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import screen_brightness_control as sbcontrol

class MouseController:
    def __init__(self):
        pyautogui.FAILSAFE = False
        self.screen_w, self.screen_h = pyautogui.size()
        
        # Variabel Redam Jitter Kursor
        self.prev_hand = None
        self.smooth_factor = 0.7  # Smoothing untuk pergerakan yang lebih halus
        
        # Variabel Kendali Pinch
        self.pinch_start_x = None
        self.pinch_start_y = None
        self.pinch_lv = 0
        self.prev_pinch_lv = 0
        self.frame_count = 0
        self.pinch_direction_x = None
        self.pinch_threshold = 0.03
        
        # Status Bendera
        self.drag_active = False
        self.pinch_major_flag = False
        self.pinch_minor_flag = False
        
        # Debounce untuk klik
        self.last_click_time = 0
        self.click_cooldown = 0.2  # 200ms cooldown
        
        # Untuk tracking gesture sebelumnya (mencegah spam)
        self.last_gesture = None
        self.last_gesture_time = 0

    def get_position(self, landmarks_list, cam_w, cam_h, reduction):
        """Mendapatkan posisi kursor dengan smoothing"""
        if len(landmarks_list) == 0: 
            return pyautogui.position()
        
        # Gunakan landmark 9 (MCP jari tengah) untuk stabilitas
        raw_x = landmarks_list[9][1]
        raw_y = landmarks_list[9][2]
        
        # Batasi area
        raw_x = np.clip(raw_x, reduction, cam_w - reduction)
        raw_y = np.clip(raw_y, reduction, cam_h - reduction)
        
        # Mapping ke layar
        inter_w = cam_w - (2 * reduction)
        inter_h = cam_h - (2 * reduction)
        
        target_x = np.interp(raw_x - reduction, (0, inter_w), (0, self.screen_w))
        target_y = np.interp(raw_y - reduction, (0, inter_h), (0, self.screen_h))
        
        # Smoothing posisi
        if self.prev_hand is None:
            self.prev_hand = [target_x, target_y]
        
        smooth_x = self.prev_hand[0] * self.smooth_factor + target_x * (1 - self.smooth_factor)
        smooth_y = self.prev_hand[1] * self.smooth_factor + target_y * (1 - self.smooth_factor)
        
        self.prev_hand = [smooth_x, smooth_y]
        return int(smooth_x), int(smooth_y)

    def safe_click(self, button="left", clicks=1):
        """Klik dengan debounce"""
        current_time = time.time()
        if current_time - self.last_click_time > self.click_cooldown:
            pyautogui.click(button=button, clicks=clicks)
            self.last_click_time = current_time
            print(f"[ACTION] {button.upper()} click x{clicks}")
            return True
        return False

    def pinch_init(self, landmarks_list):
        """Inisialisasi pinch gesture"""
        if len(landmarks_list) == 0: 
            return
        self.pinch_start_x = landmarks_list[8][1]
        self.pinch_start_y = landmarks_list[8][2]
        self.pinch_lv = 0
        self.prev_pinch_lv = 0
        self.frame_count = 0
        self.pinch_direction_x = None

    def execute_pinch_action(self, landmarks_list, action_horizontal, action_vertical):
        """Eksekusi pinch untuk scroll/volume"""
        if len(landmarks_list) == 0: 
            return
        
        current_x = landmarks_list[8][1]
        current_y = landmarks_list[8][2]
        
        # Hitung pergerakan
        delta_x = current_x - self.pinch_start_x
        delta_y = self.pinch_start_y - current_y  # Dibalik untuk natural
        
        # Normalisasi
        lvx = delta_x / 50.0
        lvy = delta_y / 50.0
        
        # Stabilisasi selama 5 frame
        if self.frame_count == 5:
            self.frame_count = 0
            if self.pinch_direction_x is True and abs(self.prev_pinch_lv) > 0.1:
                action_horizontal(self.prev_pinch_lv)
                print(f"[PINCH] Horizontal: {self.prev_pinch_lv:.2f}")
            elif self.pinch_direction_x is False and abs(self.prev_pinch_lv) > 0.1:
                action_vertical(self.prev_pinch_lv)
                print(f"[PINCH] Vertical: {self.prev_pinch_lv:.2f}")
        
        # Tentukan arah
        if abs(lvy) > abs(lvx) and abs(lvy) > self.pinch_threshold:
            self.pinch_direction_x = False
            self.prev_pinch_lv = lvy
            self.frame_count += 1
        elif abs(lvx) > self.pinch_threshold:
            self.pinch_direction_x = True
            self.prev_pinch_lv = lvx
            self.frame_count += 1
        else:
            self.frame_count = 0

    # Action functions
    def change_volume(self, level):
        """Ubah volume sistem"""
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            current = volume.GetMasterVolumeLevelScalar()
            new_volume = np.clip(current + (level * 0.1), 0.0, 1.0)
            volume.SetMasterVolumeLevelScalar(new_volume, None)
            print(f"[VOLUME] {new_volume:.0%}")
        except Exception as e:
            print(f"[ERROR] Volume: {e}")

    def change_brightness(self, level):
        """Ubah kecerahan layar"""
        try:
            current = sbcontrol.get_brightness(display=0)[0] / 100.0
            new_bright = np.clip(current + (level * 0.1), 0.0, 1.0)
            sbcontrol.set_brightness(int(new_bright * 100), display=0)
            print(f"[BRIGHTNESS] {new_bright:.0%}")
        except Exception as e:
            print(f"[ERROR] Brightness: {e}")

    def scroll_vertical(self, level):
        """Scroll vertikal"""
        amount = int(100 if level > 0 else -100)
        pyautogui.scroll(amount)
        print(f"[SCROLL] Vertical: {amount}")

    def scroll_horizontal(self, level):
        """Scroll horizontal"""
        amount = int(100 if level > 0 else -100)
        pyautogui.keyDown('shift')
        pyautogui.scroll(-amount)
        pyautogui.keyUp('shift')
        print(f"[SCROLL] Horizontal: {amount}")

    def process_gesture_controls(self, gesture, landmarks_list, cam_w, cam_h, reduction):
        """Proses gesture dan eksekusi aksi yang sesuai"""
        from src.gesture_logic import Gest
        
        # Rate limiting untuk menghindari spam aksi
        current_time = time.time()
        
        # Gesture yang memerlukan tracking posisi
        if gesture in [Gest.INDEX_MID_UP, Gest.FIST]:
            x, y = self.get_position(landmarks_list, cam_w, cam_h, reduction)
        else:
            x, y = None, None
        
        # === HANDLE DRAG STATE ===
        if gesture != Gest.FIST and self.drag_active:
            self.drag_active = False
            pyautogui.mouseUp(button="left")
            print("[ACTION] Drag ended")
        
        # === EKSEKUSI GESTURE ===
        
        # 1. INDEX_MID_UP: Move mouse
        if gesture == Gest.INDEX_MID_UP:
            if x and y:
                pyautogui.moveTo(x, y)
                # Optional: Tampilkan posisi di console
                # print(f"[MOUSE] Move to ({x}, {y})")
        
        # 2. INDEX_FOLDED: Left click
        elif gesture == Gest.INDEX_FOLDED:
            if current_time - self.last_gesture_time > 0.3:  # Rate limit
                self.safe_click(button="left", clicks=1)
                self.last_gesture_time = current_time
        
        # 3. MID_FOLDED: Right click
        elif gesture == Gest.MID_FOLDED:
            if current_time - self.last_gesture_time > 0.3:
                self.safe_click(button="right", clicks=1)
                self.last_gesture_time = current_time
        
        # 4. FIST: Drag and drop
        elif gesture == Gest.FIST:
            if not self.drag_active:
                self.drag_active = True
                pyautogui.mouseDown(button="left")
                print("[ACTION] Drag started")
            if x and y:
                pyautogui.moveTo(x, y)
        
        # 5. PINCH_MINOR: Scroll (Tangan Kiri)
        elif gesture == Gest.PINCH_MINOR:
            if not self.pinch_minor_flag:
                self.pinch_init(landmarks_list)
                self.pinch_minor_flag = True
                print("[PINCH] Minor initialized")
            self.execute_pinch_action(landmarks_list, self.scroll_horizontal, self.scroll_vertical)
        
        # 6. PINCH_MAJOR: Volume/Brightness (Tangan Kanan)
        elif gesture == Gest.PINCH_MAJOR:
            if not self.pinch_major_flag:
                self.pinch_init(landmarks_list)
                self.pinch_major_flag = True
                print("[PINCH] Major initialized")
            self.execute_pinch_action(landmarks_list, self.change_brightness, self.change_volume)
        
        # 7. V_GEST: Untuk double click (opsional)
        elif gesture == Gest.V_GEST:
            if current_time - self.last_gesture_time > 0.3:
                self.safe_click(button="left", clicks=2)
                self.last_gesture_time = current_time
        
        # Reset flags jika gesture berubah
        if gesture not in [Gest.PINCH_MINOR, Gest.PINCH_MAJOR]:
            self.pinch_minor_flag = False
            self.pinch_major_flag = False
        
        # Simpan gesture terakhir
        self.last_gesture = gesture