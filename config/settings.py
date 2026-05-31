# config/settings.py

# Konfigurasi Kamera (Gunakan resolusi default agar FPS tinggi, jangan dipaksa 640x480 jika berat)
CAM_ID = 0  # Sesuaikan dengan kamera yang aktif (0 atau 1)

# Konfigurasi Deteksi MediaPipe Tasks API
# Diturunkan sedikit ke 0.5 agar deteksi tangan tidak gampang hilang (luplep) saat tangan bergerak cepat
MIN_DETECTION_CONFIDENCE = 0.5
MIN_TRACKING_CONFIDENCE = 0.5

# FAKTOR PERATAAN KURSOR (Smoothing) untuk mengatasi Jitter
# Semakin BESAR nilainya, kursor semakin mulus (getaran hilang), tapi akan ada sedikit efek lambat (delay).
# Naikkan ke angka 7.0 atau 10.0 jika tanganmu masih bergetar.
SMOOTHING_FACTOR = 8.0 

# Batas Jarak Jari untuk Deteksi Klik (dalam piksel)
CLICK_THRESHOLD = 25

# Area Pembatas (Bounding Box) di Kamera
# Tambahkan ini di config/settings.py jika belum ada
PINCH_THRESHOLD = 0.3
FRAME_REDUCTION = 40  # Kotak batas interaksi kamera

# Mouse sensitivity
MOUSE_SMOOTHING = 0.5
MOUSE_SPEED = 1.5