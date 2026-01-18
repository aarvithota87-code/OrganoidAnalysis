import cv2
import numpy as np
import os
from organoid_analysis_watershed import analyze_organoids_watershed

def analyze_organoids_morphology(image_paths):
    
    results = []

    for day, img_path in image_paths.items():
        if not os.path.exists(img_path):
            continue

        img = cv2.imread(img_path)
        if img is None:
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        if cv2.countNonZero(thresh) > (thresh.size / 2):
            thresh = cv2.bitwise_not(thresh)

        kernel = np.ones((3,3), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
        sure_bg = cv2.dilate(opening, kernel, iterations=3)
        dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
        _, sure_fg = cv2.threshold(dist_transform, 0.5 * dist_transform.max(), 255, 0)
        sure_fg = np.uint8(sure_fg)
        unknown = cv2.subtract(sure_bg, sure_fg)
        ret, markers = cv2.connectedComponents(sure_fg)
        markers = markers + 1
        markers[unknown == 255] = 0
        markers = cv2.watershed(img, markers)

        organoid_features = []
        debug_img = img.copy()
        
        unique_labels = np.unique(markers)
        
        avg_cell_area_projection = 150.0

        for label in unique_labels:
            if label <= 1: continue 
            
            mask = np.uint8(markers == label) * 255
            area = cv2.countNonZero(mask)
            
            if area > 100:
                cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if not cnts: continue
                cnt = cnts[0]
                
                hull = cv2.convexHull(cnt)
                hull_area = cv2.contourArea(hull)
                solidity = float(area) / hull_area if hull_area > 0 else 0
                
                if len(cnt) >= 5:
                    (x,y), (MA, ma), angle = cv2.fitEllipse(cnt)
                    a = ma / 2
                    b = MA / 2
                    if a > 0:
                        eccentricity = np.sqrt(1 - (b**2)/(a**2)) 
                    else:
                        eccentricity = 0
                else:
                    eccentricity = 0
                    
                est_cells = int(area / avg_cell_area_projection)
                
                organoid_features.append({
                    'area': area,
                    'solidity': solidity,
                    'eccentricity': eccentricity,
                    'cells': est_cells
                })
                
                color = (0, int(255*solidity), 255-int(255*solidity))
                cv2.drawContours(debug_img, [cnt], -1, color, 2)

        count = len(organoid_features)
        
        if count > 0:
            avg_size = float(np.mean([f['area'] for f in organoid_features]))
            total_area = float(np.sum([f['area'] for f in organoid_features]))
            avg_solidity = float(np.mean([f['solidity'] for f in organoid_features]))
            avg_eccentricity = float(np.mean([f['eccentricity'] for f in organoid_features]))
            total_cells = int(np.sum([f['cells'] for f in organoid_features]))
        else:
            avg_size = 0.0
            total_area = 0.0
            avg_solidity = 0.0
            avg_eccentricity = 0.0
            total_cells = 0

        debug_dir = os.path.join(os.path.dirname(img_path), "debug_output_morphology")
        os.makedirs(debug_dir, exist_ok=True)
        cv2.imwrite(os.path.join(debug_dir, f"morphology_debug_day{day}.jpg"), debug_img)
        
        h, w = img.shape[:2]

        results.append({
            "day": day,
            "count": int(count),
            "avg_size": avg_size,
            "total_area": total_area,
            "avg_solidity": avg_solidity,
            "avg_eccentricity": avg_eccentricity,
            "est_total_cells": total_cells,
            "resolution": f"{w}x{h}"
        })

    return results