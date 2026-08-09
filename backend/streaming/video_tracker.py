import cv2
import numpy as np

from av import VideoFrame
from aiortc import MediaStreamTrack

from backend.pipeline.trt_inference import TensorRTInference


class TensorRTVideoTrack(MediaStreamTrack):
    """
    Receives video frames from aiortc,
    runs YOLOv10 TensorRT inference,
    draws detections,
    and returns the processed frame.
    """

    kind = "video"

    def __init__(self, source_track):
        super().__init__()

        self.source_track = source_track

        print("🚀 Initializing TensorRT video tracker...")
        self.trt = TensorRTInference()
        print("✅ TensorRT video tracker ready.")

    async def recv(self):
        # Receive frame from the original video track
        frame = await self.source_track.recv()

        # Convert aiortc frame -> OpenCV BGR image
        image = frame.to_ndarray(format="bgr24")

        original_height, original_width = image.shape[:2]

        # YOLO input size
        input_size = 640

        # Resize to TensorRT input size
        resized = cv2.resize(
            image,
            (input_size, input_size)
        )

        # BGR -> RGB
        rgb = cv2.cvtColor(
            resized,
            cv2.COLOR_BGR2RGB
        )

        # Normalize
        rgb = rgb.astype(np.float32) / 255.0

        # HWC -> CHW
        tensor = np.transpose(
            rgb,
            (2, 0, 1)
        )

        # Add batch dimension
        tensor = np.expand_dims(
            tensor,
            axis=0
        )

        # TensorRT inference
        output = self.trt.infer(tensor)

        # Remove batch dimension
        detections = output[0]

        # Draw detections
        for detection in detections:

            x1, y1, x2, y2, confidence, class_id = detection

            # Ignore weak detections
            if confidence < 0.35:
                continue

            # Convert coordinates back to original frame size
            x1 = int(x1 * original_width / input_size)
            y1 = int(y1 * original_height / input_size)
            x2 = int(x2 * original_width / input_size)
            y2 = int(y2 * original_height / input_size)

            class_id = int(class_id)

            # Draw bounding box
            cv2.rectangle(
                image,
                (x1, y1),
                (x2, y2),
                (255, 0, 0),
                2
            )

            # Label
            label = f"class {class_id} {confidence:.2f}"

            cv2.putText(
                image,
                label,
                (x1, max(y1 - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 0, 0),
                2
            )

        # Convert OpenCV image -> WebRTC frame
        new_frame = VideoFrame.from_ndarray(
            image,
            format="bgr24"
        )

        # Preserve WebRTC timing information
        new_frame.pts = frame.pts
        new_frame.time_base = frame.time_base

        return new_frame