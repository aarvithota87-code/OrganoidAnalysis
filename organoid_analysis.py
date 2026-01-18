import cv2
import numpy as np
import os

def analyze_organoids(image_paths):
    results = []

    for day, img_path in image_paths.items():
        if not os.path.exists(img_path):
            print(f"Error: {img_path} not found.")
            continue

        img = cv2.imread(img_path)
        if img is None:
            print(f"Error: Could not read {img_path}")
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        if cv2.countNonZero(thresh) > (thresh.size / 2):
            thresh = cv2.bitwise_not(thresh)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        organoid_areas = []
        valid_contours = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 100: 
                organoid_areas.append(area)
                valid_contours.append(cnt)
        
        debug_img = img.copy()
        cv2.drawContours(debug_img, valid_contours, -1, (0, 255, 0), 2)
        debug_dir = os.path.join(os.path.dirname(img_path), "debug_output")
        os.makedirs(debug_dir, exist_ok=True)
        cv2.imwrite(os.path.join(debug_dir, f"debug_day{day}.jpg"), debug_img)

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

def generate_report(results):
    print("Organoid Growth Analysis Report")
    print("===============================")
    
    prev_area = None
    
    for i, res in enumerate(results):
        print(f"Day {res['day']}:")
        print(f"  Resolution: {res.get('resolution', 'N/A')}")
        print(f"  Count: {res['count']}")
        print(f"  Average Size (pixels^2): {res['avg_size']:.2f}")
        print(f"  Total Area (pixels^2): {res['total_area']:.2f}")
        
        if prev_area is not None and prev_area > 0:
            growth_rate = ((res['total_area'] - prev_area) / prev_area) * 100
            print(f"  Daily Expansion Rate: {growth_rate:.2f}%")
        
        prev_area = res['total_area']
        print("-" * 30)

if __name__ == "__main__":
    base_dir = "/Users/kamalakarthota/Downloads/OrganoidAnalysis"
    image_files = {
        1: os.path.join(base_dir, "day1.jpg"),
        2: os.path.join(base_dir, "day2.jpg"),
        3: os.path.join(base_dir, "day3.jpg"),
        4: os.path.join(base_dir, "day4.jpg")
    }

    results = analyze_organoids(image_files)
    generate_report(results)