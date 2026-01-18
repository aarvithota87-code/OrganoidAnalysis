import cv2
import numpy as np
import os

def analyze_organoids_hough(image_paths):
    results = []
    
    dp = 1.2
    minDist = 40
    param1 = 50
    param2 = 30
    minRadius = 10
    maxRadius = 150

    for day, img_path in image_paths.items():
        if not os.path.exists(img_path):
            continue

        img = cv2.imread(img_path)
        if img is None:
            continue
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        blurred = cv2.medianBlur(gray, 5)
        
        circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp, minDist,
                                   param1=param1, param2=param2,
                                   minRadius=minRadius, maxRadius=maxRadius)
        
        organoid_circles = []
        
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                organoid_circles.append(i)
        
        count = len(organoid_circles)
        
        total_area = 0
        total_volume = 0
        avg_radius = 0
        
        if count > 0:
            radii = [c[2] for c in organoid_circles]
            avg_radius = float(np.mean(radii))
            
            for r in radii:
                area = np.pi * (r**2)
                vol = (4/3) * np.pi * (r**3)
                total_area += area
                total_volume += vol
        
        debug_img = img.copy()
        if circles is not None:
            for i in circles[0, :]:
                center = (i[0], i[1])
                radius = i[2]
                cv2.circle(debug_img, center, 1, (0, 100, 100), 3)
                cv2.circle(debug_img, center, radius, (255, 0, 255), 2)

        debug_dir = os.path.join(os.path.dirname(img_path), "debug_output_hough")
        os.makedirs(debug_dir, exist_ok=True)
        cv2.imwrite(os.path.join(debug_dir, f"hough_debug_day{day}.jpg"), debug_img)
        
        h, w = img.shape[:2]

        results.append({
            "day": day,
            "count": int(count),
            "avg_size": float(total_area / count) if count > 0 else 0.0,
            "total_area": float(total_area),
            "total_volume": float(total_volume),
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
    
    results = analyze_organoids_hough(image_files)
    
    print("Hough Transform Results")
    for res in results:
        print(f"Day {res['day']}: Count={res['count']}, Vol={res['total_volume']:,.0f}")