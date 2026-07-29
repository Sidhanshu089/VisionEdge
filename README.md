# VisionEdge

A GPU-accelerated Edge AI pipeline for real-time object detection on RTSP streams using YOLOv10, ONNX Runtime, TensorRT, FastAPI, and NVIDIA GPU acceleration.

---

## 🚀 Features

- Real-time object detection using YOLOv10
- GPU-accelerated inference pipeline
- ONNX model export and validation
- ONNX Runtime inference
- TensorRT optimization (Coming Soon)
- FastAPI backend
- Docker support
- Modular AI pipeline architecture

---

## 🛠 Tech Stack

- Python 3.12
- PyTorch
- Ultralytics YOLOv10
- ONNX
- ONNX Runtime
- TensorRT (Upcoming)
- CUDA
- OpenCV
- NumPy
- FastAPI
- aiortc
- PyAV
- Docker
- Git & GitHub

---

## 📂 Project Structure

```text
VisionEdge
│
├── backend
│   ├── models
│   │   ├── weights
│   │   ├── onnx
│   │   └── tensorrt
│   │
│   ├── pipeline
│   │   ├── loader.py
│   │   ├── predictor.py
│   │   ├── export_onnx.py
│   │   ├── validate_onnx.py
│   │   ├── preprocess.py
│   │   └── onnx_inference.py
│   │
│   └── config.py
│
├── assets
├── frontend
├── docker
└── README.md
```

---

## 📅 Development Progress

### ✅ Day 1
- Project setup
- Repository structure
- FastAPI backend
- Git workflow

### ✅ Day 2
- Python 3.12 environment
- CUDA installation
- GPU-enabled PyTorch
- AI library installation
- Docker configuration

### ✅ Day 3
- YOLOv10 integration
- Model loader
- Image inference pipeline
- Object detection
- Git branching workflow

### ✅ Day 4
- Exported YOLOv10 to ONNX
- ONNX model validation
- Manual image preprocessing
- ONNX Runtime integration
- ONNX inference pipeline
- Performance measurement

---

## 📊 Current Pipeline

```text
Image
   │
   ▼
Preprocessing
   │
   ▼
YOLOv10 (.pt)
   │
   ▼
ONNX Export
   │
   ▼
YOLOv10 (.onnx)
   │
   ▼
ONNX Runtime
   │
   ▼
Detections
```

---

## 🎯 Upcoming

- TensorRT Engine Conversion
- RTSP Stream Processing
- GPU Video Decoding
- FastAPI REST APIs
- WebRTC Streaming
- React Dashboard
- Performance Benchmarking
- Docker Deployment

---

## 📌 Current Status

🚧 **Day 4 Complete — ONNX Runtime inference pipeline is operational.**