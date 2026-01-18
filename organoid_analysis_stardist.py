import cv2
import numpy as np
import os

try:
    from stardist.models import StarDist2D
    from csbdeep.utils import normalize
    STARDIST_AVAILABLE = True
except (ImportError, AttributeError, TypeError, Exception) as e:
    STARDIST_AVAILABLE = False
    print(f"StarDist not available due to: {type(e).__name__}")

def analyze_organoids_stardist(image_paths):
    if not STARDIST_AVAILABLE:
        print("StarDist not available. using Aggressive Convex Geometry fallback.")
        return analyze_organoids_stardist_fallback(image_paths)

    try:
        model = StarDist2D.from_pretrained('2D_versatile_fluo')
    except Exception as e:
         print(f"StarDist load failed: {e}. Switching to fallback.")
         return analyze_organoids_stardist_fallback(image_paths)

    results = []
    
    return []

def analyze_organoids_stardist_fallback(image_paths):
    results = []
    for day, img_path in image_paths.items():
        if not os.path.exists(img_path):
            continue

        img = cv2.imread(img_path)
        if img is None:
            continue
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        blurred = cv2.GaussianBlur(gray, (7, 7), 0)
        
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        if cv2.countNonZero(thresh) > (thresh.size / 2):
            thresh = cv2.bitwise_not(thresh)
            
        kernel = np.ones((3,3), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
        
        dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
        
        _, sure_fg = cv2.threshold(dist_transform, 0.55 * dist_transform.max(), 255, 0)
        
        sure_fg = np.uint8(sure_fg)
        sure_bg = cv2.dilate(opening, kernel, iterations=3)
        unknown = cv2.subtract(sure_bg, sure_fg)
        
        ret, markers = cv2.connectedComponents(sure_fg)
        markers = markers + 1
        markers[unknown == 255] = 0
        
        markers = cv2.watershed(img, markers)
        
        organoid_areas = []
        debug_img = img.copy()
        
        labels = np.unique(markers)
        for label in labels:
            if label <= 1: continue
            
            mask = np.uint8(markers == label) * 255
            area = cv2.countNonZero(mask)
            
            if area > 80:
                organoid_areas.append(area)
                cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cv2.drawContours(debug_img, cnts, -1, (255, 255, 0), 2)

        debug_dir = os.path.join(os.path.dirname(img_path), "debug_output_stardist")
        os.makedirs(debug_dir, exist_ok=True)
        cv2.imwrite(os.path.join(debug_dir, f"stardist_debug_day{day}.jpg"), debug_img)

        count = len(organoid_areas)
        avg_size = float(np.mean(organoid_areas)) if organoid_areas else 0.0
        total_area = float(np.sum(organoid_areas)) if organoid_areas else 0.0
        
        h, w = img.shape[:2]

        results.append({
            "day": day,
            "count": int(count),
            "avg_size": avg_size,
            "total_area": total_area,
            "resolution": f"{w}x{h}"
        })
        
    return results

def analyze_organoids_stardist(image_paths):
    if not STARDIST_AVAILABLE:
        return analyze_organoids_stardist_fallback(image_paths)

    try:
        model = StarDist2D.from_pretrained('2D_versatile_fluo')
    except Exception as e:
        return analyze_organoids_stardist_fallback(image_paths)

    results = []
    for day, img_path in image_paths.items():
        if not os.path.exists(img_path):
            continue

        img = cv2.imread(img_path)
        if img is None:
            continue
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_norm = normalize(gray, 1, 99.8, axis=(0,1))
        
        labels, details = model.predict_instances_big(img_norm, axes='YX') 
        
        organoid_areas = []
        unique_labels = np.unique(labels)
        debug_img = img.copy()

        for label in unique_labels:
            if label == 0: continue
            mask = np.uint8(labels == label)
            area = np.sum(mask)
            
            if area > 100:
                organoid_areas.append(area)
                cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cv2.drawContours(debug_img, cnts, -1, (255, 255, 0), 2) 

        debug_dir = os.path.join(os.path.dirname(img_path), "debug_output_stardist")
        os.makedirs(debug_dir, exist_ok=True)
        cv2.imwrite(os.path.join(debug_dir, f"stardist_debug_day{day}.jpg"), debug_img)

        count = len(organoid_areas)
        avg_size = float(np.mean(organoid_areas)) if organoid_areas else 0.0
        total_area = float(np.sum(organoid_areas)) if organoid_areas else 0.0
        h, w = img.shape[:2]

        results.append({
            "day": day,
            "count": int(count),
            "avg_size": avg_size,
            "total_area": total_area,
            "resolution": f"{w}x{h}"
        })

    return results