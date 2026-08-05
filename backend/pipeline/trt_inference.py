import numpy as np
from cuda.bindings import runtime as cudart

from backend.pipeline.trt_engine import TensorRTEngine
from backend.pipeline.trt_allocator import TensorRTAllocator


class TensorRTInference:

    def __init__(self):

        self.engine = TensorRTEngine()
        self.memory = TensorRTAllocator(self.engine)

    def infer(self, input_tensor):

        np.copyto(self.memory.host_input, input_tensor.astype(np.float32))

        err = cudart.cudaMemcpy(
        self.memory.device_input,
        self.memory.host_input.ctypes.data,
        self.memory.host_input.nbytes,
        cudart.cudaMemcpyKind.cudaMemcpyHostToDevice
        )[0]

        if err != 0:
            raise RuntimeError("Host → Device copy failed.")

    # Bind GPU memory to TensorRT tensors
        self.engine.context.set_tensor_address(
            self.engine.input_name,
            int(self.memory.device_input)
        )

        self.engine.context.set_tensor_address(
            self.engine.output_name,
            int(self.memory.device_output)
        )

    # Execute inference
        success = self.engine.context.execute_v2([
            int(self.memory.device_input),
            int(self.memory.device_output)
        ])

        if not success:
            raise RuntimeError("TensorRT execution failed.")

        err = cudart.cudaMemcpy(
            self.memory.host_output.ctypes.data,
            self.memory.device_output,
            self.memory.host_output.nbytes,
            cudart.cudaMemcpyKind.cudaMemcpyDeviceToHost
        )[0]

        if err != 0:
            raise RuntimeError("Device → Host copy failed.")

        return self.memory.host_output