# src/gesture_logic.py
import math
from enum import IntEnum

class Gest(IntEnum):
    FIST = 0
    PINKY = 1
    RING = 2
    MID = 4
    LAST3 = 7
    INDEX = 8
    FIRST2 = 12
    LAST4 = 15
    THUMB = 16    
    PALM = 31
    V_GEST = 33
    TWO_FINGER_CLOSED = 34
    PINCH_MAJOR = 35
    PINCH_MINOR = 36
    INDEX_FOLDED = 37
    MID_FOLDED = 38
    INDEX_MID_UP = 39

class HLabel(IntEnum):
    MINOR = 0
    MAJOR = 1

class HandRecog:
    def __init__(self, hand_label):
        self.finger = 0
        self.current_gesture = Gest.PALM
        self.hand_result = None
        self.hand_label = hand_label
        # Individual finger states
        self.thumb_state = False
        self.index_state = False
        self.middle_state = False
        self.ring_state = False
        self.pinky_state = False
        # Untuk stabilisasi
        self.gesture_history = []
        self.history_size = 5
    
    def update_hand_result(self, landmarks_list):
        self.hand_result = landmarks_list

    def get_dist(self, p1, p2):
        if self.hand_result is None or len(self.hand_result) <= max(p1, p2): 
            return 0
        return math.hypot(
            self.hand_result[p1][1] - self.hand_result[p2][1], 
            self.hand_result[p1][2] - self.hand_result[p2][2]
        )

    def set_finger_state(self):
        """Deteksi state masing-masing jari"""
        if self.hand_result is None or len(self.hand_result) == 0:
            return

        # Deteksi jempol (berdasarkan posisi X)
        thumb_tip_x = self.hand_result[4][1]
        thumb_mcp_x = self.hand_result[2][1]
        self.thumb_state = thumb_tip_x > thumb_mcp_x
        
        # Deteksi 4 jari lainnya (tip lebih tinggi dari pip = Y lebih kecil)
        self.index_state = self.hand_result[8][2] < self.hand_result[6][2]
        self.middle_state = self.hand_result[12][2] < self.hand_result[10][2]
        self.ring_state = self.hand_result[16][2] < self.hand_result[14][2]
        self.pinky_state = self.hand_result[20][2] < self.hand_result[18][2]
        
        # Build finger bitmap
        self.finger = 0
        if self.thumb_state:
            self.finger |= 1
        if self.index_state:
            self.finger |= 2
        if self.middle_state:
            self.finger |= 4
        if self.ring_state:
            self.finger |= 8
        if self.pinky_state:
            self.finger |= 16

    def get_raw_gesture(self):
        """Deteksi gesture langsung tanpa smoothing"""
        if self.hand_result is None or len(self.hand_result) == 0:
            return Gest.PALM

        self.set_finger_state()
        
        # Hitung jarak untuk pinch
        pinch_dist = self.get_dist(8, 4)
        hand_size = self.get_dist(5, 17)
        hand_size = hand_size if hand_size > 0 else 1.0
        is_pinching = pinch_dist / hand_size < 0.25
        
        # PRIORITAS 1: Pinch gesture
        if is_pinching:
            if self.hand_label == HLabel.MINOR:
                return Gest.PINCH_MINOR
            else:
                return Gest.PINCH_MAJOR
        
        # PRIORITAS 2: INDEX_MID_UP (Telunjuk + Tengah tegak)
        if self.index_state and self.middle_state and not self.ring_state and not self.pinky_state:
            return Gest.INDEX_MID_UP
        
        # PRIORITAS 3: INDEX_FOLDED (Telunjuk tekuk, Tengah tegak)
        if not self.index_state and self.middle_state and not self.ring_state and not self.pinky_state:
            return Gest.INDEX_FOLDED
        
        # PRIORITAS 4: MID_FOLDED (Telunjuk tegak, Tengah tekuk)
        if self.index_state and not self.middle_state and not self.ring_state and not self.pinky_state:
            return Gest.MID_FOLDED
        
        # PRIORITAS 5: FIST (Semua mengepal)
        if not self.thumb_state and not self.index_state and not self.middle_state and not self.ring_state and not self.pinky_state:
            return Gest.FIST
        
        # PRIORITAS 6: V_GEST
        if self.index_state and self.middle_state and self.ring_state and not self.pinky_state:
            return Gest.V_GEST
        
        # PRIORITAS 7: PALM (Banyak jari terbuka)
        if self.finger >= 15:
            return Gest.PALM
        
        return Gest.PALM

    def get_gesture(self):
        """Get gesture dengan smoothing (majority vote)"""
        raw_gesture = self.get_raw_gesture()
        
        # Simpan ke history
        self.gesture_history.append(raw_gesture)
        if len(self.gesture_history) > self.history_size:
            self.gesture_history.pop(0)
        
        # Ambil gesture yang paling sering muncul dalam history
        if len(self.gesture_history) == self.history_size:
            from collections import Counter
            counter = Counter(self.gesture_history)
            most_common = counter.most_common(1)[0]
            
            # Hanya update jika muncul lebih dari 3 kali
            if most_common[1] >= 3:
                self.current_gesture = most_common[0]
        
        return self.current_gesture