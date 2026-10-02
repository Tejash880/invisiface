import cv2
import numpy as np
from pathlib import Path

def create_synthetic_face_image(num_faces: int = 1) -> np.ndarray:
    """
    Generate synthetic test image with faces, eyes, and background patterns
    that trigger OpenCV face cascades accurately for automated testing.
    """
    img = np.ones((600, 800, 3), dtype=np.uint8) * 220
    
    # Background texture
    for i in range(0, 800, 40):
        cv2.line(img, (i, 0), (i, 600), (200, 200, 200), 1)

    centers = [(400, 300)] if num_faces == 1 else [(250, 300), (550, 300)]

    for cx, cy in centers:
        # Head contour (Skin tone)
        cv2.ellipse(img, (cx, cy), (90, 120), 0, 0, 360, (180, 205, 235), -1)
        cv2.ellipse(img, (cx, cy), (90, 120), 0, 0, 360, (100, 130, 160), 2)

        # Hair
        cv2.ellipse(img, (cx, cy - 60), (95, 70), 0, 180, 360, (40, 30, 25), -1)

        # Eyes (White + Pupil)
        for eye_x in [cx - 35, cx + 35]:
            cv2.circle(img, (eye_x, cy - 20), 16, (255, 255, 255), -1)
            cv2.circle(img, (eye_x, cy - 20), 7, (40, 20, 10), -1)

        # Eyebrows
        cv2.line(img, (cx - 50, cy - 42), (cx - 20, cy - 40), (40, 30, 25), 4)
        cv2.line(img, (cx + 20, cy - 40), (cx + 50, cy - 42), (40, 30, 25), 4)

        # Nose
        cv2.line(img, (cx, cy - 10), (cx - 8, cy + 20), (140, 165, 195), 3)
        cv2.line(img, (cx - 8, cy + 20), (cx + 8, cy + 20), (140, 165, 195), 3)

        # Mouth
        cv2.ellipse(img, (cx, cy + 50), (30, 15), 0, 0, 180, (100, 80, 190), -1)

    return img

if __name__ == '__main__':
    demo_dir = Path(__file__).parent
    demo_dir.mkdir(exist_ok=True)

    single_img = create_synthetic_face_image(1)
    multi_img = create_synthetic_face_image(2)
    noface_img = np.ones((600, 800, 3), dtype=np.uint8) * 100  # Gray blank canvas

    cv2.imwrite(str(demo_dir / 'test_single_face.png'), single_img)
    cv2.imwrite(str(demo_dir / 'test_multi_face.png'), multi_img)
    cv2.imwrite(str(demo_dir / 'test_no_face.png'), noface_img)

    print("Demo synthetic images generated in demo_images/")
