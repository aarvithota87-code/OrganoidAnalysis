import cv2
import numpy as np
import os

def analyze_arivis_sim(image_paths):
    results = []
    
    for day, img_path in image_paths.items():
        if not os.path.exists(img_path): continue
        img = cv2.imread(img_path)
        if img is None: continue
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        if cv2.countNonZero(thresh) > (thresh.size / 2): thresh = cv2.bitwise_not(thresh)
        
        kernel = np.ones((3,3), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
        dist = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
        _, fg = cv2.threshold(dist, 0.5 * dist.max(), 255, 0)
        fg = np.uint8(fg)
        bg = cv2.dilate(opening, kernel, iterations=3)
        unk = cv2.subtract(bg, fg)
        ret, markers = cv2.connectedComponents(fg)
        markers = markers + 1
        markers[unk == 255] = 0
        markers = cv2.watershed(img, markers)
        
        total_vol = 0
        organoids = []
        debug_img = img.copy()
        
        labels = np.unique(markers)
        for label in labels:
            if label <= 1: continue
            mask = np.uint8(markers == label) * 255
            area = cv2.countNonZero(mask)
            
            if area > 100:
                r = np.sqrt(area / np.pi)
                vol = (4/3) * np.pi * (r**3)
                surf = 4 * np.pi * (r**2)
                total_vol += vol
                
                organoids.append(vol)
                
                cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if cnts:
                    cv2.drawContours(debug_img, cnts, -1, (0, 255, 255), 1)
                    M = cv2.moments(cnts[0])
                    if M["m00"] != 0:
                        cX = int(M["m10"] / M["m00"])
                        cY = int(M["m01"] / M["m00"])
                        cv2.line(debug_img, (cX-5, cY), (cX+5, cY), (0, 165, 255), 1)
                        cv2.line(debug_img, (cX, cY-5), (cX, cY+5), (0, 165, 255), 1)
        
        debug_dir = os.path.join(os.path.dirname(img_path), "debug_output_arivis")
        os.makedirs(debug_dir, exist_ok=True)
        cv2.imwrite(os.path.join(debug_dir, f"arivis_debug_day{day}.jpg"), debug_img)
        
        h, w = img.shape[:2]
        results.append({
            "day": day,
            "count": int(len(organoids)),
            "est_volume": float(total_vol),
            "avg_volume": float(np.mean(organoids)) if organoids else 0.0,
            "resolution": f"{w}x{h}"
        })
        
    return results

def analyze_assayscope_sim(image_paths):
    results = []
    
    for day, img_path in image_paths.items():
        if not os.path.exists(img_path): continue
        img = cv2.imread(img_path)
        if img is None: continue
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.medianBlur(gray, 5)
        circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 1.2, 40, param1=50, param2=30, minRadius=10, maxRadius=150)
        
        radii = []
        debug_img = img.copy()
        
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                center = (i[0], i[1])
                r = i[2]
                radii.append(r)
                
                cv2.rectangle(debug_img, (i[0]-r, i[1]-r), (i[0]+r, i[1]+r), (0, 255, 0), 1)
        
        if radii:
            mean_r = np.mean(radii)
            std_r = np.std(radii)
            cv_r = (std_r / mean_r) * 100 if mean_r > 0 else 0
            
            outliers = [r for r in radii if abs(r - mean_r) > 2*std_r]
            homogeneity = 100 - cv_r
        else:
            mean_r = 0; cv_r = 0; homogeneity = 0
            
        debug_dir = os.path.join(os.path.dirname(img_path), "debug_output_assayscope")
        os.makedirs(debug_dir, exist_ok=True)
        cv2.imwrite(os.path.join(debug_dir, f"assayscope_debug_day{day}.jpg"), debug_img)
        
        h, w = img.shape[:2]
        results.append({
            "day": day,
            "count": int(len(radii)),
            "mean_radius": float(mean_r),
            "homogeneity_score": float(homogeneity),
            "resolution": f"{w}x{h}"
        })
        
    return results