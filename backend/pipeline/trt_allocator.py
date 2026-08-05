import numpy as np
from cuda.bindings import runtime as cudart


class TensorRTAllocator:
    def __init__(self, engine):

        self.engine = engine

        self.host_input = np.empty(
            engine.input_shape,
            dtype=engine.input_dtype
        )

        self.host_output = np.empty(
            engine.output_shape,
            dtype=engine.output_dtype
        )

        input_bytes = self.host_input.nbytes
        output_bytes = self.host_output.nbytes

        err, self.device_input = cudart.cudaMalloc(input_bytes)
        if err != 0:
            raise RuntimeError("Failed to allocate input GPU memory.")

        err, self.device_output = cudart.cudaMalloc(output_bytes)
        if err != 0:
            raise RuntimeError("Failed to allocate output GPU memory.")

        print("✅ GPU memory allocated successfully.")
        print(f"Input Buffer : {input_bytes} bytes")
        print(f"Output Buffer: {output_bytes} bytes")