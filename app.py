from flask import Flask, render_template, request, jsonify, send_file
import os
import shutil
import cv2
import glob

from organoid_analysis import analyze_organoids as analyze_basic
from organoid_analysis_watershed import analyze_organoids_watershed
from organoid_analysis_hough import analyze_organoids_hough
from organoid_analysis_morphology import analyze_organoids_morphology
from organoid_analysis_commercial_sims import analyze_arivis_sim, analyze_assayscope_sim
try:
    from organoid_analysis_unet import analyze_organoids_unet
    UNET_AVAILABLE = True
except Exception as e:
    print(f"Warning: U-Net not available ({type(e).__name__}). U-Net method will use fallback.")
    UNET_AVAILABLE = False
    def analyze_organoids_unet(image_paths):
        from organoid_analysis_unet import analyze_organoids_unet_fallback
        return analyze_organoids_unet_fallback(image_paths)

try:
    from organoid_analysis_stardist import analyze_organoids_stardist
    STARDIST_AVAILABLE = True
except Exception as e:
    print(f"Warning: StarDist not available ({e}). StarDist method will use fallback.")
    STARDIST_AVAILABLE = False
    def analyze_organoids_stardist(image_paths):
        from organoid_analysis_stardist import analyze_organoids_stardist_fallback
        return analyze_organoids_stardist_fallback(image_paths)

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
RESULTS_FOLDER = 'static/results'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

def cleanup_folders():
    for folder in [UPLOAD_FOLDER, RESULTS_FOLDER]:
        if os.path.exists(folder):
            pass

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/methods')
def methods():
    return send_file('methods_explanation.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'images[]' not in request.files:
        return jsonify({'error': 'No images uploaded'}), 400
    
    files = request.files.getlist('images[]')
    method = request.form.get('method', 'basic')
    
    if not files or files[0].filename == '':
        return jsonify({'error': 'No selected file'}), 400

    image_map = {}
    saved_paths = []
    
    files.sort(key=lambda x: x.filename)

    for i, file in enumerate(files):
        if file:
            filename = file.filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            day_label = i + 1
            image_map[day_label] = filepath
            saved_paths.append(filepath)

    print(f"Running {method} analysis on {len(saved_paths)} images...")
    
    try:
        if method == 'watershed':
            results = analyze_organoids_watershed(image_map)
            debug_subfolder = 'debug_output_watershed'
        elif method == 'hough':
            results = analyze_organoids_hough(image_map)
            debug_subfolder = 'debug_output_hough'
        elif method == 'stardist':
            results = analyze_organoids_stardist(image_map)
            if isinstance(results, dict) and "error" in results:
                return jsonify({'error': results["error"]}), 500
            debug_subfolder = 'debug_output_stardist'
        elif method == 'morphology':
            results = analyze_organoids_morphology(image_map)
            debug_subfolder = 'debug_output_morphology'
        elif method == 'arivis':
            results = analyze_arivis_sim(image_map)
            debug_subfolder = 'debug_output_arivis'
        elif method == 'assayscope':
            results = analyze_assayscope_sim(image_map)
            debug_subfolder = 'debug_output_assayscope'
        elif method == 'unet':
            results = analyze_organoids_unet(image_map)
            if isinstance(results, dict) and "error" in results:
                return jsonify({'error': results["error"]}), 500
            debug_subfolder = 'debug_output_unet'
        else:
            results = analyze_organoids_basic_wrapper(image_map)
            debug_subfolder = 'debug_output'
            
        processed_results = []
        for res in results:
            day = res['day']
            
            if method == 'watershed':
                debug_name = f"watershed_debug_day{day}.jpg"
            elif method == 'hough':
                debug_name = f"hough_debug_day{day}.jpg"
            elif method == 'stardist':
                debug_name = f"stardist_debug_day{day}.jpg"
            elif method == 'morphology':
                debug_name = f"morphology_debug_day{day}.jpg"
            elif method == 'arivis':
                debug_name = f"arivis_debug_day{day}.jpg"
            elif method == 'assayscope':
                debug_name = f"assayscope_debug_day{day}.jpg"
            elif method == 'unet':
                debug_name = f"unet_debug_day{day}.jpg"
            else:
                debug_name = f"debug_day{day}.jpg"

            debug_path_abs = os.path.join(UPLOAD_FOLDER, debug_subfolder, debug_name)
            debug_url = f"/{debug_path_abs}"
            orig_url = f"/{image_map[day]}"
            
            res['original_url'] = orig_url
            res['debug_url'] = debug_url
            processed_results.append(res)
            
        return jsonify({
            'success': True,
            'method': method,
            'results': processed_results
        })

    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({'error': str(e)}), 500

def analyze_organoids_basic_wrapper(image_map):
    return analyze_basic(image_map)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5174))
    app.run(host='0.0.0.0', port=port, debug=True)