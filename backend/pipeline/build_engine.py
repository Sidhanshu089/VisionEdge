from pathlib import Path
import subprocess

ONNX_MODEL = Path("backend/models/onnx/yolov10n.onnx")
ENGINE_MODEL = Path("backend/models/tensorrt/yolov10n.engine")

ENGINE_MODEL.parent.mkdir(parents=True, exist_ok=True)

command = [
    "trtexec",
    f"--onnx={ONNX_MODEL}",
    f"--saveEngine={ENGINE_MODEL}",
]

print("Building TensorRT engine...\n")

result = subprocess.run(command)

if result.returncode == 0:
    print(f"\n✅ Engine saved to: {ENGINE_MODEL}")
else:
    print("\n❌ Engine build failed.")