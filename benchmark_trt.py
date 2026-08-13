import time
import cv2
import numpy as np

from backend.pipeline.trt_inference import TensorRTInference


IMAGE_PATH = "assets/images/input/test.png"


# Load image
image = cv2.imread(IMAGE_PATH)

if image is None:
    raise RuntimeError(f"Could not load image: {IMAGE_PATH}")


# Prepare input
image = cv2.resize(image, (640, 640))

rgb = cv2.cvtColor(
    image,
    cv2.COLOR_BGR2RGB
)

rgb = rgb.astype(np.float32) / 255.0

tensor = np.transpose(
    rgb,
    (2, 0, 1)
)

tensor = np.expand_dims(
    tensor,
    axis=0
)


# Load TensorRT
trt = TensorRTInference()


# Warm-up
print("\n🔥 Warming up TensorRT...")

for _ in range(10):
    trt.infer(tensor)


# Benchmark
print("📊 Running benchmark...")

times = []

for _ in range(30):

    start = time.perf_counter()

    trt.infer(tensor)

    end = time.perf_counter()

    elapsed_ms = (end - start) * 1000

    times.append(elapsed_ms)


# Results
average = np.mean(times)
minimum = np.min(times)
maximum = np.max(times)
fps = 1000 / average


print("\n========== TensorRT Benchmark ==========")

print(f"Average inference : {average:.2f} ms")
print(f"Minimum inference : {minimum:.2f} ms")
print(f"Maximum inference : {maximum:.2f} ms")
print(f"Approx FPS        : {fps:.2f}")

print("========================================")