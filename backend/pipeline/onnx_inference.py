# from pathlib import Path
# import onnxruntime as ort

# MODEL_PATH = Path("backend/models/onnx/yolov10n.onnx")


# def load_onnx_model():
#     session = ort.InferenceSession(
#         str(MODEL_PATH),
#         providers=["CPUExecutionProvider"]
#         # This guarantees the code works on your machine without any extra setup.
#         # Later, when we reach TensorRT and GPU optimization, we'll switch to GPU execution providers.
#     )

#     print("✅ ONNX Runtime model loaded successfully!\n")

#     print("Model Inputs:")
#     for inp in session.get_inputs():
#         print(f"  Name : {inp.name}")
#         print(f"  Shape: {inp.shape}")
#         print(f"  Type : {inp.type}")
#         print()

#     print("Model Outputs:")
#     for out in session.get_outputs():
#         print(f"  Name : {out.name}")
#         print(f"  Shape: {out.shape}")
#         print(f"  Type : {out.type}")
#         print()

#     return session


# if __name__ == "__main__":
#     load_onnx_model()

# ---------------------------- UPDATED CODE BELOW ----------------------------

from pathlib import Path
import time

import onnxruntime as ort

from backend.pipeline.preprocess import preprocess

MODEL_PATH = Path("backend/models/onnx/yolov10n.onnx")


def run_inference():
    session = ort.InferenceSession(
        str(MODEL_PATH),
        providers=["CPUExecutionProvider"]
    )

    input_name = session.get_inputs()[0].name

    image = preprocess()

    start = time.perf_counter()

    outputs = session.run(
        None,
        {input_name: image}
    )

    end = time.perf_counter()

    print("\n✅ ONNX Inference Successful!")
    print(f"Inference Time: {(end-start)*1000:.2f} ms")

    output = outputs[0]

    print(f"Output Shape: {output.shape}")
    print("\nFirst 5 detections:\n")

    for i in range(5):
        print(output[0][i])


if __name__ == "__main__":
    run_inference()