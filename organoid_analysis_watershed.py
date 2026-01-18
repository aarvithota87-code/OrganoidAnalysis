import cv2
import numpy as np
import os

def analyze_organoids_watershed(image_paths):
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
        _, sure_fg = cv2.threshold(dist_transform, 0.4 * dist_transform.max(), 255, 0)

        sure_fg = np.uint8(sure_fg)
        unknown = cv2.subtract(sure_bg, sure_fg)

        ret, markers = cv2.connectedComponents(sure_fg)
        markers = markers + 1
        markers[unknown == 255] = 0

        markers = cv2.watershed(img, markers)
        
        organoid_areas = []
        circularities = []
        valid_contours = []
        
        labels = np.unique(markers)
        
        debug_img = img.copy()
        
        for label in labels:
            if label <= 1: continue
            
            mask = np.zeros(gray.shape, dtype=np.uint8)
            mask[markers == label] = 255
            
            area = cv2.countNonZero(mask)
            
            if area > 100:
                organoid_areas.append(area)
                
                cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if cnts:
                    cnt = cnts[0]
                    perimeter = cv2.arcLength(cnt, True)
                    if perimeter > 0:
                        circ = 4 * np.pi * area / (perimeter * perimeter)
                        circularities.append(circ)
                    
                    cv2.drawContours(debug_img, cnts, -1, (0, 0, 255), 2)

        debug_img[markers == -1] = [0, 255, 255]

        debug_dir = os.path.join(os.path.dirname(img_path), "debug_output_watershed")
        os.makedirs(debug_dir, exist_ok=True)
        cv2.imwrite(os.path.join(debug_dir, f"watershed_debug_day{day}.jpg"), debug_img)

        count = len(organoid_areas)
        avg_size = float(np.mean(organoid_areas)) if organoid_areas else 0.0
        total_area = float(np.sum(organoid_areas)) if organoid_areas else 0.0
        avg_circularity = float(np.mean(circularities)) if circularities else 0.0
        
        h, w = img.shape[:2]

        results.append({
            "day": day,
            "count": int(count),
            "avg_size": avg_size,
            "total_area": total_area,
            "avg_circularity": avg_circularity,
            "resolution": f"{w}x{h}"
        })

    return results

if __name__ == "__main__":
    base_dir = "/Users/kamalakarthota/Downloads/OrganoidAnalysis"
    image_files = {
        1: os.path.join(base_dir, "day1.jpg"),
        2: os.path.join(base_dir, "day2.jpg"),
        3: os.path.join(base_dir, "day3.jpg"),
        4: os.path.join(base_dir, "day4.jpg")
    }
    
    results = analyze_organoids_watershed(image_files)
    print(results)