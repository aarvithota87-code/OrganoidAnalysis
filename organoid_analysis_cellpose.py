import numpy as np
import os
import cv2
from cellpose import models
import time

def analyze_organoids_cellpose(image_paths):
    print("Loading Cellpose model (cyto2)...")
    model = models.Cellpose(gpu=False, model_type='cyto2')
    
    results = []

    for day, img_path in image_paths.items():
        if not os.path.exists(img_path):
            print(f"Error: {img_path} not found.")
            continue

        print(f"Processing {img_path}...")
        
        img = cv2.imread(img_path)
        if img is None:
            print(f"Error: Could not read {img_path}")
            continue
            
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        masks, flows, styles, diams = model.eval(
            img_rgb, 
            diameter=None,
            channels=[0,0],
            flow_threshold=0.4,
            do_3D=False
        )

        organoid_areas = []
        valid_masks = []
        
        num_objects = masks.max()
        for i in range(1, num_objects + 1):
            area = np.sum(masks == i)
            if area > 100:
                organoid_areas.append(area)
                valid_masks.append(i)

        count = len(organoid_areas)
        avg_size = np.mean(organoid_areas) if organoid_areas else 0
        total_area = np.sum(organoid_areas) if organoid_areas else 0
        
        debug_img = img.copy()
        
        for mask_id in valid_masks:
            obj_mask = np.uint8(masks == mask_id)
            contours, _ = cv2.findContours(obj_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(debug_img, contours, -1, (0, 0, 255), 2)

        debug_dir = os.path.join(os.path.dirname(img_path), "debug_output_cellpose")
        os.makedirs(debug_dir, exist_ok=True)
        cv2.imwrite(os.path.join(debug_dir, f"cellpose_debug_day{day}.jpg"), debug_img)
        
        h, w = img.shape[:2]

        results.append({
            "day": day,
            "count": count,
            "avg_size": avg_size,
            "total_area": total_area,
            "resolution": f"{w}x{h}"
        })

    return results

def generate_report(results):
    print("\nOrganoid Growth Analysis Report (Cellpose)")
    print("==========================================")
    
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
    
    if not all(os.path.exists(f) for f in image_files.values()):
        print("Some images are missing. Please check filenames.")
    else:
        results = analyze_organoids_cellpose(image_files)
        generate_report(results)