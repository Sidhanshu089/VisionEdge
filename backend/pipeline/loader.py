from ultralytics import YOLO
from backend.config import YOLO_MODEL


def load_model():
    """
    Load the YOLO model.
    """
    try:
        model = YOLO(YOLO_MODEL)
        print(f"Model loaded successfully: {YOLO_MODEL}")
        return model

    except Exception as e:
        print(f"Error loading model: {e}")
        raise


if __name__ == "__main__":
    load_model()