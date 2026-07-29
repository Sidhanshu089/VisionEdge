from pathlib import Path
from ultralytics import YOLO

PT_MODEL = Path("backend/models/weights/yolov10n.pt")
ONNX_MODEL = Path("backend/models/onnx/yolov10n.onnx")


def export_model():
    if not PT_MODEL.exists():
        raise FileNotFoundError(f"Model not found: {PT_MODEL}")

    model = YOLO(str(PT_MODEL))

    model.export(
        format="onnx",
        imgsz=640,
        opset=17,
        simplify=True
    )

    print("\n✅ ONNX export completed successfully!")


if __name__ == "__main__":
    export_model()