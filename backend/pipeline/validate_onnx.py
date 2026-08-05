from pathlib import Path
import onnx

MODEL_PATH = Path("backend/models/onnx/yolov10n.onnx")


def validate_model():
    model = onnx.load(str(MODEL_PATH))
    onnx.checker.check_model(model)

    print("✅ ONNX model is valid!")
    print(f"IR Version   : {model.ir_version}")
    print(f"Producer     : {model.producer_name}")
    print(f"Graph Name   : {model.graph.name}")


if __name__ == "__main__":
    validate_model()