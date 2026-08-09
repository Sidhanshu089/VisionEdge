import cv2
import numpy as np

from av import VideoFrame
from aiortc import MediaStreamTrack

from backend.pipeline.trt_inference import TensorRTInference


class TensorRTVideoTrack(MediaStreamTrack):
    """
    Receives frames from aiortc, performs YOLOv10 TensorRT
    inference using letterbox preprocessing, draws detections,
    and returns the processed WebRTC frame.
    """

    kind = "video"

    def __init__(self, source_track):
        super().__init__()

        self.source_track = source_track

        print("🚀 Initializing TensorRT video tracker...")

        self.trt = TensorRTInference()

        print("✅ TensorRT video tracker ready.")

    def letterbox(self, image, new_shape=(640, 640)):
        """
        Resize image while maintaining aspect ratio and
        add padding to reach the target dimensions.
        """

        original_height, original_width = image.shape[:2]

        target_width, target_height = new_shape

        # Calculate scale
        scale = min(
            target_width / original_width,
            target_height / original_height
        )

        # New resized dimensions
        new_width = int(round(original_width * scale))
        new_height = int(round(original_height * scale))

        # Resize while preserving aspect ratio
        resized = cv2.resize(
            image,
            (new_width, new_height),
            interpolation=cv2.INTER_LINEAR
        )

        # Calculate padding
        pad_width = target_width - new_width
        pad_height = target_height - new_height

        left = pad_width // 2
        right = pad_width - left

        top = pad_height // 2
        bottom = pad_height - top

        # Add padding
        padded = cv2.copyMakeBorder(
            resized,
            top,
            bottom,
            left,
            right,
            cv2.BORDER_CONSTANT,
            value=(114, 114, 114)
        )

        return padded, scale, left, top

    async def recv(self):

        # Receive original frame
        frame = await self.source_track.recv()

        # Convert aiortc frame to OpenCV
        image = frame.to_ndarray(format="bgr24")

        original_height, original_width = image.shape[:2]

        # -------------------------------------------------
        # 1. LETTERBOX PREPROCESSING
        # -------------------------------------------------

        processed, scale, pad_x, pad_y = self.letterbox(
            image,
            (640, 640)
        )

        # BGR → RGB
        rgb = cv2.cvtColor(
            processed,
            cv2.COLOR_BGR2RGB
        )

        # Convert to float32 and normalize
        rgb = rgb.astype(np.float32) / 255.0

        # HWC → CHW
        tensor = np.transpose(
            rgb,
            (2, 0, 1)
        )

        # Add batch dimension
        tensor = np.expand_dims(
            tensor,
            axis=0
        )

        # -------------------------------------------------
        # 2. TENSORRT INFERENCE
        # -------------------------------------------------

        output = self.trt.infer(tensor)

        detections = output[0]

        # -------------------------------------------------
        # 3. POSTPROCESSING
        # -------------------------------------------------

        for detection in detections:

            x1, y1, x2, y2, confidence, class_id = detection

            # Confidence threshold
            if confidence < 0.35:
                continue

            # Remove letterbox padding
            x1 = (x1 - pad_x) / scale
            y1 = (y1 - pad_y) / scale
            x2 = (x2 - pad_x) / scale
            y2 = (y2 - pad_y) / scale

            # Clamp coordinates to original frame
            x1 = max(0, min(original_width - 1, x1))
            y1 = max(0, min(original_height - 1, y1))
            x2 = max(0, min(original_width - 1, x2))
            y2 = max(0, min(original_height - 1, y2))

            x1 = int(x1)
            y1 = int(y1)
            x2 = int(x2)
            y2 = int(y2)

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

        # -------------------------------------------------
        # 4. CONVERT BACK TO WEBRTC FRAME
        # -------------------------------------------------

        new_frame = VideoFrame.from_ndarray(
            image,
            format="bgr24"
        )

        # Preserve timing
        new_frame.pts = frame.pts
        new_frame.time_base = frame.time_base

        return new_frame