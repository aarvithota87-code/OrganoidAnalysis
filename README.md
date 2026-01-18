# Organoid Analysis Web Application

A comprehensive web application for analyzing organoid cell growth using multiple computer vision and deep learning methods.

## Features

- **Multiple Analysis Methods:**
  - Basic Thresholding (Otsu)
  - Watershed Segmentation
  - Hough Circle Transform
  - StarDist (Deep Learning)
  - **U-Net (Deep Learning)** - Encoder-decoder architecture for semantic segmentation
  - Advanced Morphology & Cell Count
  - ZEISS arivis Pro (Simulation)
  - AssayScope (Simulation)

- **Interactive Web Interface:**
  - Upload multiple organoid images
  - Select analysis method
  - View growth trends and statistics
  - Visual analysis with annotated images

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd "OrganoidAnalysis ExtraMethods"
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

**Note:** Some deep learning methods (U-Net, StarDist) require TensorFlow. If TensorFlow is not available or has compatibility issues, these methods will automatically use advanced image processing fallbacks.

## Usage

### Start the Application

```bash
python3 app.py
```

Or use the startup script:
```bash
./run_app.sh
```

The application will be available at: **http://localhost:5174**

### Using the Web Interface

1. Open your browser and navigate to `http://localhost:5174`
2. Upload organoid images (Day 1, Day 2, Day 3, Day 4, etc.)
3. Select an analysis method from the dropdown
4. Click "Analyze Data"
5. View results including:
   - Growth trends (count and size)
   - Statistics cards
   - Visual analysis with annotated images

## Project Structure

```
OrganoidAnalysis ExtraMethods/
├── app.py                          # Flask web application
├── organoid_analysis.py            # Basic thresholding method
├── organoid_analysis_watershed.py  # Watershed segmentation
├── organoid_analysis_hough.py      # Hough circle transform
├── organoid_analysis_stardist.py   # StarDist deep learning
├── organoid_analysis_unet.py       # U-Net deep learning
├── organoid_analysis_morphology.py # Advanced morphology analysis
├── organoid_analysis_commercial_sims.py # Commercial tool simulations
├── organoid_analysis_cellpose.py   # Cellpose method (optional)
├── templates/
│   └── index.html                  # Web interface
├── static/
│   ├── uploads/                    # User uploaded images (created at runtime)
│   └── results/                    # Analysis results (created at runtime)
├── methods_explanation.html        # Methods comparison page
├── requirements.txt                # Python dependencies
├── run_app.sh                      # Startup script
└── README.md                       # This file
```

## Requirements

- Python 3.7+
- Flask >= 2.0.0
- OpenCV >= 4.5.0
- NumPy >= 1.21.0

**Optional (for deep learning methods):**
- TensorFlow >= 2.8.0 (for U-Net)
- StarDist >= 0.8.0 (for StarDist method)
- Cellpose >= 2.0.0 (for Cellpose method)

## Configuration

The default port is **5174**. You can change it by:
- Setting the `PORT` environment variable
- Modifying the port in `app.py`

## Notes

- Debug output images are automatically generated in `static/uploads/debug_output_*/` directories
- The application handles TensorFlow/NumPy compatibility issues gracefully with fallback methods
- All analysis methods return consistent data structures for easy comparison

## License

[Add your license here]

## Contributing

[Add contribution guidelines if needed]

