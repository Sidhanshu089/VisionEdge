# VisionEdge

A GPU-accelerated Edge AI pipeline for real-time object detection on RTSP streams using YOLOv10, ONNX, TensorRT, and NVIDIA acceleration.

---

## 🚀 Tech Stack

- Python 3.12
- FastAPI
- YOLOv10
- ONNX
- ONNX Runtime
- TensorRT
- CUDA
- PyAV
- aiortc
- React
- Docker (planned)

---

## 📌 Project Progress

### ✅ Day 1 – Project Setup
- Created project structure
- Initialized Git repository
- Configured GitHub workflow
- Set up FastAPI backend

### ✅ Day 2 – GPU AI Environment
- Configured Python virtual environment
- Installed PyTorch with CUDA support
- Verified GPU and CUDA installation
- Configured development environment

### ✅ Day 3 – YOLOv10 Image Inference
- Integrated YOLOv10 model
- Performed image inference
- Saved prediction results
- Displayed detected objects with confidence scores

### ✅ Day 4 – ONNX Integration
- Exported YOLOv10 model to ONNX
- Validated ONNX model
- Performed inference using ONNX Runtime
- Benchmarked ONNX Runtime inference

### ✅ Day 5 – TensorRT Engine Setup
- Installed TensorRT 11.1
- Configured TensorRT Python API
- Converted ONNX model to TensorRT Engine
- Loaded TensorRT Engine
- Created Execution Context
- Verified Engine Input/Output tensors

---

## 📂 Project Structure

```text
VisionEdge/
│
├── backend/
│   ├── models/
│   │   ├── weights/
│   │   ├── onnx/
│   │   └── tensorrt/
│   └── pipeline/
│
├── frontend/
│
└── README.md
```

---

## 🔜 Upcoming Work

- Execute TensorRT inference
- Benchmark TensorRT vs ONNX Runtime
- Video inference pipeline
- RTSP stream processing
- DeepStream integration
- WebRTC streaming
- React dashboard

---

## 📜 License

MIT License