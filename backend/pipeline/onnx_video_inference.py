from ultralytics import YOLO
import time
from pathlib import Path
import cv2

# Input and output paths
INPUT_VIDEO = Path("assets/videos/input/Video1.mp4")
OUTPUT_VIDEO = Path("assets/videos/output/output.mp4")

ONNX_MODEL = Path("backend/models/onnx/yolov10n.onnx")

model = YOLO(str(ONNX_MODEL), task="detect")

print("✅ YOLOv10 ONNX model loaded.")

def preprocess(frame):
    image = cv2.resize(frame, (640, 640))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    image = image.astype(np.float32) / 255.0
    image = np.transpose(image, (2, 0, 1))
    image = np.expand_dims(image, axis=0)

    return image


def process_video():
    cap = cv2.VideoCapture(str(INPUT_VIDEO))

    if not cap.isOpened():
        print("❌ Failed to open input video.")
        return

    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    print(f"Resolution : {width} x {height}")
    print(f"FPS        : {fps}")

    # Create output folder
    OUTPUT_VIDEO.parent.mkdir(parents=True, exist_ok=True)

    writer = cv2.VideoWriter(
        str(OUTPUT_VIDEO),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height)
    )

    frame_count = 0
    total_inference_time = 0.0

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        frame_count += 1

        
        start = time.perf_counter()

        results = model.predict(
            source=frame,
            imgsz=640,
            conf=0.25,
            verbose=False
        )

        end = time.perf_counter()

        total_inference_time += (end - start)

        annotated_frame = results[0].plot()

        writer.write(annotated_frame)
        

        # writer.write(frame)

    cap.release()
    writer.release()

    print(f"✅ Processed {frame_count} frames.")

    avg_time = (total_inference_time / frame_count) * 1000

    print(f"Average Inference Time: {avg_time:.2f} ms/frame")
    print(f"Approximate AI FPS: {1000 / avg_time:.2f}")
    print(f"✅ Output saved to: {OUTPUT_VIDEO}")


if __name__ == "__main__":
    process_video()