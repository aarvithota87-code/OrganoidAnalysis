import cv2
import numpy as np
import os

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    TENSORFLOW_AVAILABLE = True
except (ImportError, AttributeError, TypeError, Exception) as e:
    TENSORFLOW_AVAILABLE = False

def build_unet_model(input_shape=(256, 256, 1)):
    inputs = keras.Input(shape=input_shape)
    
    conv1 = layers.Conv2D(64, 3, activation='relu', padding='same')(inputs)
    conv1 = layers.Conv2D(64, 3, activation='relu', padding='same')(conv1)
    pool1 = layers.MaxPooling2D(pool_size=(2, 2))(conv1)
    
    conv2 = layers.Conv2D(128, 3, activation='relu', padding='same')(pool1)
    conv2 = layers.Conv2D(128, 3, activation='relu', padding='same')(conv2)
    pool2 = layers.MaxPooling2D(pool_size=(2, 2))(conv2)
    
    conv3 = layers.Conv2D(256, 3, activation='relu', padding='same')(pool2)
    conv3 = layers.Conv2D(256, 3, activation='relu', padding='same')(conv3)
    pool3 = layers.MaxPooling2D(pool_size=(2, 2))(conv3)
    
    conv4 = layers.Conv2D(512, 3, activation='relu', padding='same')(pool3)
    conv4 = layers.Conv2D(512, 3, activation='relu', padding='same')(conv4)
    
    up5 = layers.UpSampling2D(size=(2, 2))(conv4)
    up5 = layers.Conv2D(256, 2, activation='relu', padding='same')(up5)
    merge5 = layers.concatenate([conv3, up5], axis=3)
    conv5 = layers.Conv2D(256, 3, activation='relu', padding='same')(merge5)
    conv5 = layers.Conv2D(256, 3, activation='relu', padding='same')(conv5)
    
    up6 = layers.UpSampling2D(size=(2, 2))(conv5)
    up6 = layers.Conv2D(128, 2, activation='relu', padding='same')(up6)
    merge6 = layers.concatenate([conv2, up6], axis=3)
    conv6 = layers.Conv2D(128, 3, activation='relu', padding='same')(merge6)
    conv6 = layers.Conv2D(128, 3, activation='relu', padding='same')(conv6)
    
    up7 = layers.UpSampling2D(size=(2, 2))(conv6)
    up7 = layers.Conv2D(64, 2, activation='relu', padding='same')(up7)
    merge7 = layers.concatenate([conv1, up7], axis=3)
    conv7 = layers.Conv2D(64, 3, activation='relu', padding='same')(merge7)
    conv7 = layers.Conv2D(64, 3, activation='relu', padding='same')(conv7)
    
    outputs = layers.Conv2D(1, 1, activation='sigmoid')(conv7)
    
    model = keras.Model(inputs=inputs, outputs=outputs)
    return model

def analyze_organoids_unet_fallback(image_paths):
    results = []
    
    for day, img_path in image_paths.items():
        if not os.path.exists(img_path):
            continue

        img = cv2.imread(img_path)
        if img is None:
            continue
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        blurred1 = cv2.GaussianBlur(gray, (5, 5), 0)
        blurred2 = cv2.GaussianBlur(gray, (9, 9), 0)
        blurred3 = cv2.GaussianBlur(gray, (15, 15), 0)
        
        combined = cv2.addWeighted(blurred1, 0.5, blurred2, 0.3, 0)
        combined = cv2.addWeighted(combined, 0.7, blurred3, 0.3, 0)
        
        thresh = cv2.adaptiveThreshold(
            combined, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        if cv2.countNonZero(thresh) > (thresh.size / 2):
            thresh = cv2.bitwise_not(thresh)
            
        kernel = np.ones((3,3), np.uint8)
        mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=3)
        
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5,5), np.uint8), iterations=1)
        
        organoids = []
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 80:
                organoids.append(area)
        
        dist_transform = cv2.distanceTransform(mask, cv2.DIST_L2, 5)
        
        if dist_transform.max() > 0:
            dist_disp = cv2.normalize(dist_transform, None, 0, 255, cv2.NORM_MINMAX)
            dist_disp = np.uint8(dist_disp)
        else:
            dist_disp = np.zeros(mask.shape, dtype=np.uint8)
            
        heatmap = cv2.applyColorMap(dist_disp, cv2.COLORMAP_JET)
        heatmap[mask == 0] = [0, 0, 0]
        
        cv2.drawContours(heatmap, contours, -1, (255, 255, 255), 2)
        
        debug_img = cv2.addWeighted(img, 0.4, heatmap, 0.6, 0)
        cv2.drawContours(debug_img, contours, -1, (0, 255, 0), 2)
        
        debug_dir = os.path.join(os.path.dirname(img_path), "debug_output_unet")
        os.makedirs(debug_dir, exist_ok=True)
        cv2.imwrite(os.path.join(debug_dir, f"unet_debug_day{day}.jpg"), debug_img)
        
        count = len(organoids)
        avg_size = float(np.mean(organoids)) if organoids else 0.0
        total_area = float(np.sum(organoids)) if organoids else 0.0
        
        h, w = img.shape[:2]
        
        results.append({
            "day": day,
            "count": int(count),
            "avg_size": avg_size,
            "total_area": total_area,
            "resolution": f"{w}x{h}"
        })
    
    return results

def analyze_organoids_unet(image_paths):
    if not TENSORFLOW_AVAILABLE:
        print("TensorFlow not available. Using advanced image processing fallback.")
        return analyze_organoids_unet_fallback(image_paths)
    
    model = None
    model_path = None
    
    possible_model_paths = [
        'models/unet_organoid_model.h5',
        'unet_organoid_model.h5',
        'models/unet_weights.h5'
    ]
    
    for path in possible_model_paths:
        if os.path.exists(path):
            model_path = path
            break
    
    try:
        if model_path and os.path.exists(model_path):
            print(f"Loading pre-trained U-Net model from {model_path}...")
            model = keras.models.load_model(model_path)
        else:
            print("Building U-Net architecture (using untrained weights - results may vary)...")
            print("For best results, train the model on organoid data and save weights.")
            model = build_unet_model(input_shape=(None, None, 1))
            model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    except Exception as e:
        print(f"U-Net model initialization failed: {e}. Using fallback.")
        return analyze_organoids_unet_fallback(image_paths)
    
    results = []
    
    for day, img_path in image_paths.items():
        if not os.path.exists(img_path):
            continue

        img = cv2.imread(img_path)
        if img is None:
            continue
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        original_shape = gray.shape
        
        target_size = (256, 256)
        gray_resized = cv2.resize(gray, target_size)
        
        gray_normalized = gray_resized.astype(np.float32) / 255.0
        
        input_tensor = np.expand_dims(np.expand_dims(gray_normalized, axis=0), axis=-1)
        
        try:
            prediction = model.predict(input_tensor, verbose=0)
            
            prob_map = prediction[0, :, :, 0]
            
            threshold = 0.5
            mask_resized = (prob_map > threshold).astype(np.uint8) * 255
            
            mask = cv2.resize(mask_resized, (original_shape[1], original_shape[0]), 
                            interpolation=cv2.INTER_NEAREST)
            
            kernel = np.ones((3, 3), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
            
        except Exception as e:
            print(f"U-Net prediction failed for {img_path}: {e}. Using fallback for this image.")
            fallback_result = analyze_organoids_unet_fallback({day: img_path})
            if fallback_result:
                results.extend(fallback_result)
            continue
        
        organoids = []
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 80:
                organoids.append(area)
        
        prob_map_resized = cv2.resize(prob_map, (original_shape[1], original_shape[0]), 
                                     interpolation=cv2.INTER_LINEAR)
        prob_map_uint8 = (prob_map_resized * 255).astype(np.uint8)
        
        heatmap = cv2.applyColorMap(prob_map_uint8, cv2.COLORMAP_JET)
        
        debug_img = cv2.addWeighted(img, 0.5, heatmap, 0.5, 0)
        
        cv2.drawContours(debug_img, contours, -1, (0, 255, 0), 2)
        
        debug_dir = os.path.join(os.path.dirname(img_path), "debug_output_unet")
        os.makedirs(debug_dir, exist_ok=True)
        cv2.imwrite(os.path.join(debug_dir, f"unet_debug_day{day}.jpg"), debug_img)
        
        count = len(organoids)
        avg_size = float(np.mean(organoids)) if organoids else 0.0
        total_area = float(np.sum(organoids)) if organoids else 0.0
        
        h, w = img.shape[:2]
        
        results.append({
            "day": day,
            "count": int(count),
            "avg_size": avg_size,
            "total_area": total_area,
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
    
    results = analyze_organoids_unet(image_files)
    print("\nOrganoid Growth Analysis Report (U-Net)")
    print("=" * 40)
    for res in results:
        print(f"Day {res['day']}: Count={res['count']}, Avg Size={res['avg_size']:.2f}, Total Area={res['total_area']:.2f}")