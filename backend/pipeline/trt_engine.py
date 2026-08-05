from pathlib import Path
import tensorrt as trt
import numpy as np

ENGINE_PATH = Path("backend/models/tensorrt/yolov10n.engine")


class TensorRTEngine:
    def __init__(self):
        logger = trt.Logger(trt.Logger.WARNING)

        with open(ENGINE_PATH, "rb") as f:
            runtime = trt.Runtime(logger)
            self.engine = runtime.deserialize_cuda_engine(f.read())

        if self.engine is None:
            raise RuntimeError("Failed to load TensorRT engine.")

        self.context = self.engine.create_execution_context()

        if self.context is None:
            raise RuntimeError("Failed to create execution context.")

        self.input_name = self.engine.get_tensor_name(0)
        self.output_name = self.engine.get_tensor_name(1)

        self.input_shape = tuple(self.engine.get_tensor_shape(self.input_name))
        self.output_shape = tuple(self.engine.get_tensor_shape(self.output_name))

        self.input_dtype = trt.nptype(
            self.engine.get_tensor_dtype(self.input_name)
        )

        self.output_dtype = trt.nptype(
            self.engine.get_tensor_dtype(self.output_name)
        )

        print("✅ TensorRT engine loaded.")
        print("✅ Execution context created.")
        print(f"Input : {self.input_name} {self.input_shape}")
        print(f"Output: {self.output_name} {self.output_shape}")