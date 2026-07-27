from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_DIR = PROJECT_ROOT / "backend" / "models"

WEIGHTS_DIR = MODEL_DIR / "weights"
ONNX_DIR = MODEL_DIR / "onnx"
TENSORRT_DIR = MODEL_DIR / "tensorrt"

YOLO_MODEL = WEIGHTS_DIR / "yolov10n.pt"