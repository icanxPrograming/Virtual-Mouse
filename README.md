# 🖱️ AI Virtual Mouse - Hand Gesture Control

Sistem kontrol mouse berbasis AI yang menggunakan webcam untuk mendeteksi gesture tangan dan mengontrol kursor komputer secara real-time. Dibangun menggunakan MediaPipe untuk deteksi landmark tangan, OpenCV untuk pemrosesan citra, dan PyAutoGUI untuk kontrol mouse.

## ✨ Fitur Utama

| Fitur | Gesture | Fungsi |
|-------|---------|--------|
| **Move Mouse** | Telunjuk + Tengah tegak (tangan kiri) | Menggerakkan kursor ke posisi yang diinginkan |
| **Left Click** | Telunjuk tekuk, Tengah tegak (tangan kiri) | Klik kiri pada objek |
| **Right Click** | Telunjuk tegak, Tengah tekuk (tangan kiri) | Klik kanan untuk menu konteks |
| **Drag & Drop** | Tangan mengepal (FIST -> tangan kiri) | Menyeret file atau objek |
| **Double Click** | V-Gesture (2 jari -> tangan kiri) | Membuka file atau program |
| **Scroll** | Pinch (Tangan Kanan) | Scroll vertikal dan horizontal |
| **Volume/Brightness** | Pinch (Tangan Kiri) | Mengatur volume dan kecerahan layar |
| **Mode Standby** | PALM (buka semua jari) -> (kiri dan kanan) | Tidak melakukan aksi apapun |

## 📋 Persyaratan Sistem

### Minimal Requirements:
- **OS**: Windows 10/11, Linux (Ubuntu 20.04+), macOS 11+
- **Python**: 3.8 - 3.11
- **RAM**: 4GB (8GB direkomendasikan)
- **Webcam**: Minimal 720p @ 30fps

## 🚀 Cara Instalasi

### 1. Clone Repository
```bash
git clone https://github.com/icanxPrograming/Virtual-Mouse.git
cd Virtual-mouse
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

Atau install manual satu per satu:
```bash
pip install opencv-python==4.8.1.78
pip install mediapipe==0.10.8
pip install numpy==1.24.3
pip install pyautogui==0.9.54
pip install pycaw==20230407
pip install comtypes==1.2.0
pip install screen-brightness-control==0.22.0
```

### 3. Unduh Model MediaPipe (Otomatis)
Program akan secara otomatis mengunduh file model `hand_landmarker.task` dari Google saat pertama kali dijalankan. Pastikan koneksi internet aktif.

## 🎮 Cara Menjalankan

### Menjalankan Program Utama
```bash
python main.py
```

### Menjalankan Debug Gesture (Testing)
```bash
cd test
python test_gesture.py
```

### Menjalankan Test Kamera
```bash
cd test
python test_camera.py
```

## 🎯 Panduan Penggunaan

### Persiapan Awal
1. **Posisi Kamera**
   - Letakkan webcam menghadap tangan Anda
   - Jarak ideal: 30-50 cm dari kamera
   - Pastikan pencahayaan cukup

2. **Area Interaksi**
   - Kotak ungu di layar menunjukkan area aktif
   - Gerakkan tangan di dalam area tersebut

3. **Posisi Tangan**
   - Telapak tangan menghadap kamera
   - Jari sedikit terbuka untuk deteksi optimal

### Gesture Guide

| Gesture | Gambar | Cara Melakukan | Fungsi |
|---------|--------|----------------|--------|
| Move Mouse | ✌️ | Tegakkan telunjuk dan jari tengah, tekuk jari lainnya | Menggerakkan kursor |
| Left Click | ☝️ | Tekuk telunjuk, tegakkan jari tengah | Klik kiri |
| Right Click | ✌️ | Tegakkan telunjuk, tekuk jari tengah | Klik kanan |
| Drag & Drop | ✊ | Kepalkan semua jari | Menyeret objek |
| Double Click | ✌️✌️ | Gestur V (telunjuk+tengah tegak) | Klik ganda |
| Scroll | 🤏 | Rapatkan telunjuk dan jempol (tangan kiri) | Scroll halaman |
| Volume | 🤏 | Rapatkan telunjuk dan jempol (tangan kanan) | Atur volume |
| Standby | 🖐️ | Buka semua jari | Mode tidak melakukan aksi |

### Keluar Program
- Tekan tombol **`q`** pada keyboard
- Atau tutup jendela OpenCV

## ⚙️ Konfigurasi

Edit file `config/settings.py` untuk menyesuaikan parameter:

```python
# Camera settings
CAM_ID = 0                      # ID kamera (0 untuk webcam default)

# Detection confidence
MIN_DETECTION_CONFIDENCE = 0.5  # Turunkan untuk lebih sensitif
MIN_TRACKING_CONFIDENCE = 0.5   # Turunkan untuk lebih sensitif

# Frame reduction (area interaksi)
FRAME_REDUCTION = 50            # Piksel dari tepi frame
```

## 🐛 Troubleshooting

### Kamera Tidak Terdeteksi
```bash
# Jalankan test camera terlebih dahulu
python test_camera.py

# Solusi:
1. Tutup aplikasi lain yang menggunakan kamera (Zoom, Teams, Discord)
2. Cek permission kamera di Windows Settings > Privacy > Camera
3. Ganti CAM_ID di settings.py menjadi 1 atau 2
```

### Gesture Tidak Terdeteksi
```
Penyebab:
- Pencahayaan kurang
- Jarak terlalu jauh/dekat (ideal 30-50cm)
- Background terlalu ramai
- Gerakan terlalu cepat

Solusi:
1. Pastikan pencahayaan cukup (minimal 50 lux)
2. Atur jarak tangan 30-50 cm dari kamera
3. Gunakan background polos
4. Lakukan gerakan dengan jelas dan perlahan
```

### Kursor Bergerak Tidak Stabil
```python
# Edit src/mouse_controller.py
self.smooth_factor = 0.7  # Kurangi untuk respons lebih cepat (0.5)
                         # Tambah untuk lebih halus (0.9)
```

### FPS Rendah
```python
# Edit config/settings.py
# Turunkan resolusi di main.py
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)   # dari 640
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)  # dari 480

# Atau turunkan confidence threshold
MIN_DETECTION_CONFIDENCE = 0.5  # dari 0.7
```

## 📊 Performa

| Resolusi | FPS | CPU Usage | Latensi |
|----------|-----|-----------|---------|
| 640x480 | 28-32 | 25-35% | ~50ms |
| 1280x720 | 18-22 | 45-55% | ~70ms |
| 1920x1080 | 10-14 | 70-85% | ~100ms |

**Rekomendasi:** Gunakan resolusi 640x480 untuk performa terbaik.

## 📝 Catatan Penting
1. **Pencahayaan**: Sistem bekerja optimal pada kondisi pencahayaan yang cukup. Hindari cahaya dari belakang (backlight).
2. **Background**: Background polos memberikan hasil deteksi terbaik. Hindari background dengan banyak objek bergerak.
3. **Rotasi Tangan**: Deteksi paling akurat saat telapak tangan menghadap kamera. Rotasi >45° akan menurunkan akurasi.
4. **Model Download**: File model `hand_landmarker.task` (≈ 10MB) akan diunduh otomatis saat pertama kali program dijalankan.

## 🔧 Pengembangan Lebih Lanjut

Saran untuk pengembangan selanjutnya:

1. **Penambahan Gesture**: Swipe kiri/kanan untuk navigasi, circle gesture untuk refresh
2. **Multi-user Support**: Pengenalan pengguna yang berbeda
3. **Mode Kalibrasi**: Pengguna dapat menyesuaikan threshold deteksi
4. **GPU Acceleration**: Implementasi CUDA untuk performa lebih baik

## 🙏 Acknowledgements

- [MediaPipe](https://mediapipe.dev/) - Hand landmark detection by Google
- [OpenCV](https://opencv.org/) - Computer vision library
- [PyAutoGUI](https://pyautogui.readthedocs.io/) - Mouse control library

---

**Dibuat dengan ❤️ untuk memudahkan interaksi manusia-komputer**
