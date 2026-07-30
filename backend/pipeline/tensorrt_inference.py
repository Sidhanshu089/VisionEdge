from pathlib import Path
import tensorrt as trt

ENGINE_PATH = Path("backend/models/tensorrt/yolov10n.engine")


def load_engine():
    logger = trt.Logger(trt.Logger.WARNING)

    with open(ENGINE_PATH, "rb") as f:
        runtime = trt.Runtime(logger)
        engine = runtime.deserialize_cuda_engine(f.read())

    if engine is None:
        print("❌ Failed to load engine.")
        return

    print("✅ Engine loaded successfully!")

    context = engine.create_execution_context()

    if context is None:
        print("❌ Failed to create execution context.")
        return

    print("✅ Execution context created successfully!")

    return engine, context


if __name__ == "__main__":
    load_engine()