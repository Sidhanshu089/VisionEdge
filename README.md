# VisionEdge

> **GPU-Accelerated Real-Time Object Detection Pipeline for Edge AI**

VisionEdge is a Computer Vision and Edge AI project designed to perform real-time object detection on video streams using NVIDIA GPU acceleration. The project progressively optimizes inference by transitioning from PyTorch to ONNX Runtime and finally TensorRT, with the long-term goal of processing RTSP streams using NVIDIA DeepStream and streaming results to a React frontend.

---

# 🚀 Features

- Real-time object detection using YOLOv10
- Video processing with OpenCV
- ONNX model export and validation
- ONNX Runtime inference
- TensorRT engine generation
- GPU-accelerated inference pipeline
- Modular architecture for multiple inference backends
- Performance benchmarking
- Scalable for RTSP and DeepStream integration

---

# 🛠️ Tech Stack

### Programming Language
- Python 3.12

### AI & Computer Vision
- YOLOv10
- PyTorch
- ONNX
- ONNX Runtime
- TensorRT
- OpenCV

### GPU Technologies
- NVIDIA CUDA Toolkit
- CUDA Runtime API
- NVIDIA TensorRT

### Backend
- FastAPI

### Future Components
- NVIDIA DeepStream
- PyAV
- aiortc
- React
- WebRTC
- Docker

---

# 📂 Project Structure

```text
VisionEdge/
│
├── backend/
│   ├── models/
│   │   ├── weights/
│   │   ├── onnx/
│   │   └── tensorrt/
│   │
│   ├── pipeline/
│   │   ├── inference.py
│   │   ├── export_onnx.py
│   │   ├── validate_onnx.py
│   │   ├── onnx_inference.py
│   │   ├── tensorrt_inference.py
│   │   ├── trt_benchmark.py
│   │   └── video_inference.py
│   │
│   └── app.py
│
├── assets/
│   ├── images/
│   └── videos/
│
├── frontend/
│
└── README.md
```

---

# 📌 Development Progress

## ✅ Day 1 – Project Setup

- Created project repository
- Initialized Git workflow
- Created project structure
- Configured FastAPI backend
- Organized project folders

---

## ✅ Day 2 – GPU AI Development Environment

- Installed Python 3.12
- Created virtual environment
- Installed PyTorch
- Configured CUDA development environment
- Verified GPU detection
- Installed required AI libraries
- Configured Docker environment
- Set up Git branching workflow

---

## ✅ Day 3 – YOLOv10 Image Inference

- Integrated YOLOv10 model
- Loaded pretrained weights
- Performed image inference
- Saved prediction results
- Generated annotated output images
- Verified object detection pipeline

---

## ✅ Day 4 – ONNX Integration

- Exported YOLOv10 model to ONNX
- Validated exported ONNX model
- Loaded ONNX model using ONNX Runtime
- Executed inference using ONNX Runtime
- Measured inference latency
- Verified output tensor shapes

---

## ✅ Day 5 – TensorRT Engine Setup

- Installed TensorRT 11.1
- Configured TensorRT Python API
- Converted ONNX model into TensorRT Engine
- Loaded TensorRT Engine
- Created TensorRT execution context
- Verified Engine I/O tensors
- Prepared TensorRT inference pipeline

---

## ✅ Day 6 – YOLOv10 Video Inference Pipeline

- Developed a complete video processing pipeline
- Read videos using OpenCV
- Processed frames sequentially
- Integrated YOLOv10 object detection
- Drew bounding boxes and class labels
- Saved annotated output videos
- Successfully processed a 1280×720 video containing 602 frames

---

# ⚡ Current Pipeline

```text
Input Video
      │
      ▼
OpenCV Video Reader
      │
      ▼
Frame Extraction
      │
      ▼
YOLOv10 Inference
      │
      ▼
Object Detection
      │
      ▼
Bounding Box Rendering
      │
      ▼
Annotated Output Video
```

---

# 📊 Completed Milestones

| Milestone | Status |
|-----------|--------|
| Project Setup | ✅ |
| Git Workflow | ✅ |
| GPU Environment | ✅ |
| YOLOv10 Image Inference | ✅ |
| ONNX Export | ✅ |
| ONNX Runtime | ✅ |
| TensorRT Engine | ✅ |
| Video Inference | ✅ |

## 📅 Day 7 – ONNX Runtime Video Inference

### ✅ Completed
- Implemented video inference using the ONNX model.
- Integrated ONNX Runtime into the video pipeline.
- Benchmarked inference performance.
- Generated annotated output video.

### 📊 Results
- Frames Processed: 602
- Average Inference Time: 16.22 ms/frame
- Approximate AI FPS: 61.66 FPS

### 🔜 Next Steps
- Verify ONNX Runtime GPU execution.
- Integrate TensorRT into the video inference pipeline.
- Benchmark PyTorch vs ONNX Runtime vs TensorRT.

---

# 🎯 Upcoming Development

## Day 8
- Integrate TensorRT into the video pipeline
- Benchmark TensorRT vs ONNX Runtime

## Day 9
- RTSP stream processing

## Day 10
- NVIDIA DeepStream integration

## Day 11
- WebRTC streaming

## Day 12
- React dashboard integration

## Day 13
- Performance optimization

## Day 14
- Docker deployment

## Day 15
- Complete end-to-end GPU video analytics pipeline

---

# 🎯 Long-Term Goal

VisionEdge aims to build a production-ready, GPU-accelerated Edge AI platform capable of:

- Processing live RTSP camera streams
- Performing low-latency object detection
- Utilizing TensorRT for optimized GPU inference
- Leveraging NVIDIA DeepStream for high-performance video analytics
- Streaming annotated video to a web dashboard using WebRTC
- Deploying as a scalable edge AI application

---

# 📜 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

**Sidhanshu**

B.Tech Computer Science Engineering (AI/ML)

VisionEdge — GPU Accelerated Real-Time Object Detection Pipeline