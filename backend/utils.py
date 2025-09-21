from ultralytics import YOLO
import os, json, numpy as np

MODEL_WEIGHTS = "yolo11s.pt"
model = YOLO(MODEL_WEIGHTS)

def predict_and_annotate(image_path, output_path, conf_threshold=0.5, iou_threshold=0.45, imgsz=1280):
    
    # Run prediction with stronger settings
    results = model.predict(source=image_path, imgsz=imgsz, conf=conf_threshold, iou=iou_threshold, save=False)
    result = results[0]

    # Save annotated image to output_path
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    result.save(filename=output_path)

    # Build detections list
    detections = []
    confidences = []
    names = result.names if hasattr(result, "names") else {}
    for b in result.boxes:
        cls_id = int(b.cls)
        conf = float(b.conf)
        xyxy = [float(x) for x in b.xyxy[0]]
        label = names.get(cls_id, str(cls_id))
        detections.append({
            "class_id": cls_id,
            "class_name": label,
            "confidence": conf,
            "xyxy": xyxy
        })
        confidences.append(conf)

    avg_conf = float(np.mean(confidences)) if confidences else 0.0
    return detections, avg_conf

