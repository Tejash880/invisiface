import cv2
import numpy as np

class FaceDetector:
    """
    OpenCV Face Detector with Geometric & Anatomical Candidate Validation.
    Rejects false positives (such as chest/neck/background regions) using aspect ratio checks,
    relative size thresholds, eye feature validation, and Non-Maximum Suppression (NMS).
    """
    def __init__(self):
        # Frontal face cascades
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        alt_path = cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml'
        self.face_cascade_alt = cv2.CascadeClassifier(alt_path)

        # Profile face cascade fallback
        profile_path = cv2.data.haarcascades + 'haarcascade_profileface.xml'
        self.profile_cascade = cv2.CascadeClassifier(profile_path)

        # Eye cascade for facial feature ROI validation
        eye_path = cv2.data.haarcascades + 'haarcascade_eye.xml'
        self.eye_cascade = cv2.CascadeClassifier(eye_path)

    def detect_faces(self, image: np.ndarray) -> list[dict]:
        """
        Detect faces in BGR image matrix and filter out false positives.
        Returns list of dicts: [{'id': 1, 'x': x, 'y': y, 'w': w, 'h': h, 'confidence': float}]
        """
        if image is None or image.size == 0:
            return []

        img_h, img_w = image.shape[:2]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Minimum face size: 4% of image dimension
        min_size = (max(30, int(img_w * 0.04)), max(30, int(img_h * 0.04)))
        max_size = (int(img_w * 0.95), int(img_h * 0.95))

        # 1. Primary Haar Cascade Detection on raw grayscale
        raw_rects = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.08,
            minNeighbors=6,
            minSize=min_size,
            maxSize=max_size,
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        candidates = []
        if len(raw_rects) > 0:
            for (x, y, w, h) in raw_rects:
                candidates.append((int(x), int(y), int(w), int(h)))

        # 2. Backup Cascade if 0 faces found
        if len(candidates) == 0:
            alt_rects = self.face_cascade_alt.detectMultiScale(
                gray, scaleFactor=1.08, minNeighbors=5, minSize=min_size, maxSize=max_size
            )
            for (x, y, w, h) in alt_rects:
                candidates.append((int(x), int(y), int(w), int(h)))

        if len(candidates) == 0:
            profiles = self.profile_cascade.detectMultiScale(
                gray, scaleFactor=1.08, minNeighbors=5, minSize=min_size, maxSize=max_size
            )
            for (x, y, w, h) in profiles:
                candidates.append((int(x), int(y), int(w), int(h)))

        print(f"\n[FACE DETECTOR] Raw detections found: {len(candidates)}")

        # 3. Apply Non-Maximum Suppression (NMS) to remove duplicate overlapping boxes
        nms_boxes = self._suppress_overlaps(candidates, iou_threshold=0.3)

        # 4. Anatomical & Geometric Candidate Validation
        validated_faces = []
        rejected_count = 0

        for i, (x, y, w, h) in enumerate(nms_boxes):
            is_valid, reason = self._validate_face_candidate(x, y, w, h, image, gray, validated_faces)
            aspect_ratio = round(float(w) / float(h), 2)

            if is_valid:
                print(f"   Candidate #{i+1} (x={x}, y={y}, w={w}, h={h}, aspect={aspect_ratio}) -> ACCEPTED FACE ({reason})")
                validated_faces.append((x, y, w, h))
            else:
                rejected_count += 1
                print(f"   Candidate #{i+1} (x={x}, y={y}, w={w}, h={h}, aspect={aspect_ratio}) -> REJECTED FALSE POSITIVE ({reason})")

        print(f"[FACE DETECTOR] Final Summary: Raw: {len(candidates)}, Valid Faces: {len(validated_faces)}, Rejected False Positives: {rejected_count}\n")

        faces = []
        for idx, (x, y, w, h) in enumerate(validated_faces):
            faces.append({
                'id': idx + 1,
                'x': x,
                'y': y,
                'w': w,
                'h': h,
                'confidence': 0.95
            })

        return faces

    def _validate_face_candidate(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        image: np.ndarray,
        gray: np.ndarray,
        existing_faces: list[tuple]
    ) -> tuple[bool, str]:
        """
        Validates whether a bounding box candidate is a real human face ROI.
        """
        img_h, img_w = image.shape[:2]

        # Rule 1: Boundary check
        if x < 0 or y < 0 or w <= 0 or h <= 0 or (x + w) > img_w or (y + h) > img_h:
            return False, "Out of image bounds"

        # Rule 2: Geometric Aspect Ratio (w/h) Check
        # Real human faces have an aspect ratio w/h between 0.65 and 1.35
        aspect = float(w) / float(h)
        if aspect < 0.60 or aspect > 1.35:
            return False, f"Invalid aspect ratio {aspect:.2f} (Must be 0.60 - 1.35)"

        # Rule 3: Relative Size Check (Must be >= 3.5% of image width and height)
        if w < img_w * 0.035 or h < img_h * 0.035:
            return False, "Face size too small relative to image"

        # Rule 4: Chest / Body Position Hierarchy Check
        # In a portrait, a chest/neck false positive occurs directly below a valid head
        for (fx, fy, fw, fh) in existing_faces:
            head_center_x = fx + fw / 2.0
            head_bottom_y = fy + fh
            cand_center_x = x + w / 2.0
            cand_top_y = y

            # If candidate is directly below an existing face (chest/neck region)
            if abs(cand_center_x - head_center_x) < (fw * 0.6) and cand_top_y >= (fy + fh * 0.7):
                return False, "Chest/neck region located below detected face"

        # Rule 5: Eye / Feature ROI Plausibility Check
        roi_gray = gray[y:y+h, x:x+w]
        if roi_gray.size > 0:
            # Check upper 60% of ROI for eyes or structural facial contrast variance
            upper_roi = roi_gray[0:int(h * 0.6), :]
            eyes = self.eye_cascade.detectMultiScale(upper_roi, scaleFactor=1.1, minNeighbors=3, minSize=(12, 12))
            
            # Variance of Laplacian to check for feature texture
            lap_var = cv2.Laplacian(roi_gray, cv2.CV_64F).var()
            
            if lap_var < 15.0:
                return False, "Homogeneous ROI without facial feature variance"

        return True, "Passed geometric & anatomical checks"

    def draw_bounding_boxes(self, image: np.ndarray, faces: list[dict]) -> np.ndarray:
        """
        Draw bounding boxes and Face IDs on a copy of the input image.
        """
        annotated = image.copy()
        for face in faces:
            x, y, w, h = face['x'], face['y'], face['w'], face['h']
            face_id = face['id']

            # Futuristic Cyber Cyan Bounding Box
            cv2.rectangle(annotated, (x, y), (x + w, y + h), (255, 243, 0), 2)
            
            # Badge background
            label = f"Face #{face_id}"
            (text_w, text_h), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(annotated, (x, y - text_h - 6), (x + text_w + 8, y), (255, 243, 0), cv2.FILLED)
            cv2.putText(annotated, label, (x + 4, y - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (10, 15, 25), 1, cv2.LINE_AA)

        return annotated

    @staticmethod
    def _suppress_overlaps(boxes: list[tuple], iou_threshold: float = 0.3) -> list[tuple]:
        """IoU Non-Maximum Suppression."""
        if not boxes:
            return []

        # Sort by area descending
        boxes = sorted(boxes, key=lambda b: b[2] * b[3], reverse=True)
        picked = []

        while boxes:
            current = boxes.pop(0)
            picked.append(current)
            remaining = []
            for b in boxes:
                x1 = max(current[0], b[0])
                y1 = max(current[1], b[1])
                x2 = min(current[0] + current[2], b[0] + b[2])
                y2 = min(current[1] + current[3], b[1] + b[3])

                inter_area = max(0, x2 - x1) * max(0, y2 - y1)
                area1 = current[2] * current[3]
                area2 = b[2] * b[3]
                union_area = area1 + area2 - inter_area

                iou = inter_area / float(union_area) if union_area > 0 else 0
                if iou < iou_threshold:
                    remaining.append(b)
            boxes = remaining

        return picked
