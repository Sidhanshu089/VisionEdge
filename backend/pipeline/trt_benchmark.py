from pathlib import Path
import tensorrt as trt

ENGINE_PATH = Path("backend/models/tensorrt/yolov10n.engine")


def inspect_engine():
    logger = trt.Logger(trt.Logger.WARNING)

    with open(ENGINE_PATH, "rb") as f:
        runtime = trt.Runtime(logger)
        engine = runtime.deserialize_cuda_engine(f.read())

    if engine is None:
        print("❌ Failed to load engine.")
        return

    print("✅ Engine loaded successfully!\n")

    print(f"Number of I/O Tensors: {engine.num_io_tensors}\n")

    for i in range(engine.num_io_tensors):

        tensor_name = engine.get_tensor_name(i)
        shape = engine.get_tensor_shape(tensor_name)
        dtype = engine.get_tensor_dtype(tensor_name)
        mode = engine.get_tensor_mode(tensor_name)

        print(f"Tensor {i}")
        print(f"Name  : {tensor_name}")
        print(f"Shape : {shape}")
        print(f"Type  : {dtype}")
        print(f"Mode  : {mode}")
        print()


if __name__ == "__main__":
    inspect_engine()