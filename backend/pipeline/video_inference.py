from ultralytics import YOLO
from pathlib import Path
import cv2

# Input and output paths
INPUT_VIDEO = Path("assets/videos/input/Video1.mp4")
OUTPUT_VIDEO = Path("assets/videos/output/output.mp4")

MODEL_PATH = "backend/models/weights/yolov10n.pt"

model = YOLO(MODEL_PATH)
print("✅ YOLOv10 model loaded.")

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

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        frame_count += 1

        # Display frame number
        # cv2.putText(
        #     frame,
        #     f"Frame: {frame_count}",
        #     (20, 40),
        #     cv2.FONT_HERSHEY_SIMPLEX,
        #     1,
        #     (0, 255, 0),
        #     2
        # )
        results = model.predict(
            source=frame,
            imgsz=640,
            conf=0.25,
            verbose=False
        )

        annotated_frame = results[0].plot()

        writer.write(annotated_frame)
        

        # writer.write(frame)

    cap.release()
    writer.release()

    print(f"✅ Processed {frame_count} frames.")
    print(f"✅ Output saved to: {OUTPUT_VIDEO}")


if __name__ == "__main__":
    process_video()