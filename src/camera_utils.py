# src/camera_utils.py
import cv2
import time
import numpy as np

def init_camera(cam_id=0, width=640, height=480, fps=30):
    """Inisialisasi camera dengan multiple fallback options"""
    
    # Daftar backend yang akan dicoba
    backends = [
        cv2.CAP_DSHOW,      # DirectShow (Windows)
        cv2.CAP_MSMF,       # Media Foundation (Windows default)
        cv2.CAP_ANY,        # Any backend
    ]
    
    cap = None
    
    for backend in backends:
        try:
            print(f"Trying backend: {backend}")
            cap = cv2.VideoCapture(cam_id, backend)
            
            if cap.isOpened():
                print(f"Success with backend: {backend}")
                break
            else:
                cap.release()
                cap = None
        except Exception as e:
            print(f"Failed with backend {backend}: {e}")
            cap = None
    
    if cap is None:
        print("Error: Cannot open camera with any backend")
        return None
    
    # Set camera properties
    try:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        cap.set(cv2.CAP_PROP_FPS, fps)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        
        # Verify actual settings
        actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        print(f"Camera resolution: {actual_width}x{actual_height}")
    except Exception as e:
        print(f"Warning: Could not set camera properties: {e}")
    
    # Warm up camera
    for i in range(5):
        ret, frame = cap.read()
        if ret and frame is not None:
            print("Camera warm-up successful")
            break
        time.sleep(0.1)
    
    return cap

def check_camera_health(cap):
    """Cek apakah camera masih berfungsi"""
    if cap is None:
        return False
    
    try:
        if not cap.isOpened():
            return False
        ret, frame = cap.read()
        return ret and frame is not None and frame.size > 0
    except Exception as e:
        print(f"Camera health check failed: {e}")
        return False

def release_camera(cap):
    """Release camera safely"""
    if cap is not None:
        try:
            cap.release()
        except:
            pass