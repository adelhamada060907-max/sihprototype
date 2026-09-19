# AquaGuard AI — Autonomous Side Scan Sonar Marine Debris Detection and Geospatial Reporting System

> **Smart India Hackathon (SIH) Prototype**
> An end-to-end AI/CV system engineered to process Side Scan Sonar (SSS) acoustic imagery, suppress speckle noise, detect man-made underwater debris (ghost nets, shipwrecks, pipes, cylinders), filter out false positives using acoustic shadow analysis, convert target bounding boxes to WGS84 GPS coordinates, and display real-time surveys on an interactive React GIS Web Dashboard.

---

## Technical Stack

- **AI/ML & Vision**: Python, PyTorch, YOLOv11, OpenCV, NumPy, SciPy, Albumentations
- **Backend API**: FastAPI, SQLite, SQLAlchemy, Pydantic, Uvicorn
- **Frontend Dashboard**: React 18, Vite, Tailwind CSS, Leaflet.js (GIS Mapping), Chart.js (Analytics)
- **Deployment & Edge Optimization**: Docker, Docker Compose, ONNX export support for NVIDIA Jetson

---

## Detailed VS Code Setup Guide (Step-by-Step)

### Step 1: Install VS Code
Download and install [Visual Studio Code](https://code.visualstudio.com/).
Install recommended extensions:
- Python (ms-python.python)
- ES7+ React/Redux/React-Native snippets

### Step 2: Install Python
Ensure Python 3.10 or higher is installed:
```bash
python --version
```

### Step 3: Open Project Workspace
Open VS Code and navigate to the project root:
```bash
cd c:\Users\syeda\oceanguard
```

### Step 4: Create & Activate Virtual Environment
```bash
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / MacOS
python3 -m venv venv
source venv/bin/activate
```

### Step 5: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 6: Download / Generate Side-Scan Sonar Datasets
To generate synthetic side-scan sonar waterfall images with acoustic shadows and YOLO labels:
```bash
python ml/synthetic_generator.py
```

To view real-world side-scan sonar dataset acquisition commands (Roboflow / Kaggle):
```bash
python ml/dataset_pipeline.py
```

### Step 7: Train YOLOv11 Detector Model
```bash
python ml/train.py
```
To validate training metrics (Precision, Recall, mAP50, mAP50-95):
```bash
python ml/validate.py
```
To export to ONNX for NVIDIA Jetson edge hardware:
```bash
python ml/export_onnx.py
```

### Step 8: Start FastAPI Server & Integrated Web Dashboard
In Terminal 1:
```bash
python -m backend.app.main
```
The application server and integrated Web Dashboard will start at:
👉 **`http://localhost:8000`**

API Swagger Documentation: `http://localhost:8000/docs`

### Step 9: (Optional) Run React Vite Dev Server (Requires Node.js)
If Node.js is installed on your system:
```bash
cd frontend
npm install
npm run dev
```
The Vite React Dashboard will run at: `http://localhost:3000` (proxied to port 8000).

### Step 10: Run & Test Complete Prototype (SIH Demo Mode)
1. Open `http://localhost:3000` in your web browser.
2. Click **"Run SIH Demo Mode"** in the top navigation bar.
3. The system will pre-generate synthetic sonar datasets, execute AI detection, perform acoustic shadow false positive verification, georeference targets, and render real-time GIS pins on Leaflet map!
4. Test uploading your own sonar image with vessel telemetry (Lat, Lon, Depth, Heading).
5. Click **"Download JSON Report"** or **"Download CSV Report"** to export survey results.

---

## Docker Deployment

To launch the full stack in isolated Docker containers:
```bash
docker-compose up --build
```
Access Frontend at `http://localhost:3000` and Backend at `http://localhost:8000`.

---

## SIH Innovation Points & Future Scope

1. **Acoustic Shadow Verification**: Eliminates natural seabed false positives (rocks, sand ridges) by verifying whether a bright highlight return is trailed by an acoustic shadow away from nadir.
2. **Real-Time Slant Range WGS84 Georeferencing**: Converts pixel offsets into precise latitude, longitude, and depth using vessel compass heading and range resolution.
3. **Edge Optimization**: Exportable to ONNX / TensorRT for deployment directly on Autonomous Underwater Vehicles (AUVs) powered by NVIDIA Jetson.
