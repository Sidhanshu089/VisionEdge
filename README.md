# VisionEdge

A GPU-accelerated Edge AI pipeline for real-time object detection on RTSP streams using YOLOv10, ONNX, TensorRT, and WebRTC.

---

## 🚀 Project Overview

VisionEdge is designed to perform real-time object detection on live video streams while keeping the entire pipeline GPU accelerated for maximum performance.

The project aims to:

- Decode RTSP streams using GPU acceleration
- Run YOLO object detection with minimal latency
- Optimize inference using ONNX and TensorRT
- Stream annotated video to a React frontend using WebRTC

---

## 🛠 Tech Stack

- Python 3.12
- FastAPI
- PyTorch
- YOLOv10 (Ultralytics)
- CUDA Toolkit 13
- TensorRT
- ONNX Runtime
- OpenCV
- PyAV
- aiortc
- React
- Docker
- Git & GitHub

---

## 📂 Project Structure

```
VisionEdge/
│
├── assets/
│   └── images/
│
├── backend/
│   ├── api/
│   ├── decoder/
│   ├── models/
│   ├── pipeline/
│   ├── streaming/
│   ├── telemetry/
│   └── utils/
│
├── docker/
├── frontend/
├── scripts/
│
├── config.py
├── main.py
└── README.md
```

---

## ✅ Features Completed

- GPU-enabled Python environment
- CUDA Toolkit installation
- PyTorch with CUDA support
- YOLOv10 model loading
- Image inference pipeline
- Object detection on images
- Modular backend architecture
- Git branching workflow

---

## 📅 Development Progress

### ✅ Day 1
- Project setup
- Repository structure
- FastAPI backend
- Git initialization

### ✅ Day 2
- Python 3.12 environment
- CUDA Toolkit installation
- GPU-enabled PyTorch
- Project dependencies

### ✅ Day 3
- YOLOv10 integration
- Model loader
- Image inference pipeline
- Detection result generation
- Pull Request workflow

---

## 🚧 Upcoming Milestones

- [ ] Export YOLOv10 to ONNX
- [ ] ONNX Runtime inference
- [ ] TensorRT engine generation
- [ ] RTSP video decoding
- [ ] WebRTC streaming
- [ ] React dashboard
- [ ] Docker deployment

---

## 👥 Team

Internship Project

Team Size: **5 Members**

---

## 📄 License

This project is developed for educational and internship purposes.