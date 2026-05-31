# test_camera.py
import cv2
import numpy as np

def test_camera():
    print("="*50)
    print("CAMERA TEST TOOL")
    print("="*50)
    
    # Daftar backend dan ID yang akan dicoba
    test_configs = [
        (0, cv2.CAP_DSHOW, "DirectShow (ID 0)"),
        (0, cv2.CAP_ANY, "Auto (ID 0)"),
        (0, cv2.CAP_MSMF, "Media Foundation (ID 0)"),
        (1, cv2.CAP_DSHOW, "DirectShow (ID 1)"),
        (1, cv2.CAP_ANY, "Auto (ID 1)"),
        (0, cv2.CAP_V4L2, "V4L2 (Linux)"),
    ]
    
    working_cameras = []
    
    for cam_id, backend, desc in test_configs:
        print(f"\nTesting: {desc}")
        try:
            cap = cv2.VideoCapture(cam_id, backend)
            if cap.isOpened():
                # Try to read a frame
                ret, frame = cap.read()
                if ret and frame is not None:
                    print(f"  ✓ SUCCESS - Camera working!")
                    print(f"    Resolution: {frame.shape[1]}x{frame.shape[0]}")
                    working_cameras.append((cam_id, backend, desc))
                else:
                    print(f"  ✗ Failed - Can't read frame")
                cap.release()
            else:
                print(f"  ✗ Failed - Can't open camera")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print("\n" + "="*50)
    if working_cameras:
        print(f"Found {len(working_cameras)} working camera(s):")
        for i, (cam_id, backend, desc) in enumerate(working_cameras):
            print(f"  {i+1}. {desc} (ID:{cam_id}, Backend:{backend})")
        
        # Use first working camera
        cam_id, backend, desc = working_cameras[0]
        print(f"\nUsing: {desc}")
        
        # Test live feed
        print("\nOpening live feed... Press 'q' to quit")
        cap = cv2.VideoCapture(cam_id, backend)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                print("Failed to read frame")
                break
            
            cv2.putText(frame, "Camera Working! Press 'q' to quit", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("Camera Test", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
    else:
        print("No working camera found!")
        print("\nTroubleshooting steps:")
        print("  1. Check if camera is physically connected")
        print("  2. Close other apps using camera (Zoom, Teams, Browser)")
        print("  3. Check Windows Privacy Settings:")
        print("     - Go to Settings > Privacy & Security > Camera")
        print("     - Make sure 'Camera access' is ON")
        print("  4. Try restarting your computer")
        print("  5. Update camera drivers")
    
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_camera()