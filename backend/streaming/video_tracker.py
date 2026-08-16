COCO_CLASSES = [
    "person", "bicycle", "car", "motorcycle", "airplane",
    "bus", "train", "truck", "boat", "traffic light",
    "fire hydrant", "stop sign", "parking meter", "bench",
    "bird", "cat", "dog", "horse", "sheep", "cow",
    "elephant", "bear", "zebra", "giraffe", "backpack",
    "umbrella", "handbag", "tie", "suitcase", "frisbee",
    "skis", "snowboard", "sports ball", "kite", "baseball bat",
    "baseball glove", "skateboard", "surfboard", "tennis racket",
    "bottle", "wine glass", "cup", "fork", "knife", "spoon",
    "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
    "carrot", "hot dog", "pizza", "donut", "cake", "chair",
    "couch", "potted plant", "bed", "dining table", "toilet",
    "tv", "laptop", "mouse", "remote", "keyboard", "cell phone",
    "microwave", "oven", "toaster", "sink", "refrigerator",
    "book", "clock", "vase", "scissors", "teddy bear",
    "hair drier", "toothbrush"
]

import time

import cv2
import numpy as np

from av import VideoFrame
from aiortc import MediaStreamTrack

from backend.pipeline.trt_inference import TensorRTInference


class TensorRTVideoTrack(MediaStreamTrack):
    """
    Receives frames from aiortc, performs YOLOv10 TensorRT
    inference with letterbox preprocessing, draws detections,
    and reports live performance metrics.
    """

    kind = "video"

    def __init__(self, source_track):
        super().__init__()

        self.source_track = source_track

        print("🚀 Initializing TensorRT video tracker...")

        self.trt = TensorRTInference()

        self.frame_count = 0
        self.total_time = 0.0
        self.latest_metrics = {
            "frame": 0,
            "preprocess": 0.0,
            "tensorrt": 0.0,
            "postprocess": 0.0,
            "total": 0.0,
            "average": 0.0,
            "fps": 0.0,
            "detections": 0,
        }

        print("✅ TensorRT video tracker ready.")

    def letterbox(self, image, new_shape=(640, 640)):

        original_height, original_width = image.shape[:2]

        target_width, target_height = new_shape

        scale = min(
            target_width / original_width,
            target_height / original_height
        )

        new_width = int(round(original_width * scale))
        new_height = int(round(original_height * scale))

        resized = cv2.resize(
            image,
            (new_width, new_height),
            interpolation=cv2.INTER_LINEAR
        )

        pad_width = target_width - new_width
        pad_height = target_height - new_height

        left = pad_width // 2
        right = pad_width - left

        top = pad_height // 2
        bottom = pad_height - top

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

        frame_start = time.perf_counter()

        # -------------------------------------------------
        # RECEIVE FRAME
        # -------------------------------------------------

        frame = await self.source_track.recv()

        image = frame.to_ndarray(format="bgr24")

        original_height, original_width = image.shape[:2]

        # -------------------------------------------------
        # PREPROCESSING
        # -------------------------------------------------

        preprocess_start = time.perf_counter()

        processed, scale, pad_x, pad_y = self.letterbox(
            image,
            (640, 640)
        )

        rgb = cv2.cvtColor(
            processed,
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

        preprocess_time = (
            time.perf_counter() - preprocess_start
        ) * 1000

        # -------------------------------------------------
        # TENSORRT
        # -------------------------------------------------

        inference_start = time.perf_counter()

        output = self.trt.infer(tensor)

        inference_time = (
            time.perf_counter() - inference_start
        ) * 1000

        detections = output[0]

        # -------------------------------------------------
        # POSTPROCESSING
        # -------------------------------------------------

        postprocess_start = time.perf_counter()

        detection_count = 0

        for detection in detections:

            x1, y1, x2, y2, confidence, class_id = detection

            if confidence < 0.35:
                continue

            detection_count += 1

            # Remove letterbox padding
            x1 = (x1 - pad_x) / scale
            y1 = (y1 - pad_y) / scale
            x2 = (x2 - pad_x) / scale
            y2 = (y2 - pad_y) / scale

            # Clamp coordinates
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
            if 0 <= class_id < len(COCO_CLASSES):
                class_name = COCO_CLASSES[class_id]
            else:
                class_name = f"class_{class_id}"

            label = f"{class_name} {confidence:.2f}"

            cv2.putText(
                image,
                label,
                (x1, max(y1 - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 0, 0),
                2
            )

        postprocess_time = (
            time.perf_counter() - postprocess_start
        ) * 1000

        # -------------------------------------------------
        # TOTAL TIME
        # -------------------------------------------------

        total_time = (
            time.perf_counter() - frame_start
        ) * 1000

        self.frame_count += 1
        self.total_time += total_time

        average_time = (
            self.total_time / self.frame_count
        )

        pipeline_fps = 1000 / average_time

        self.latest_metrics = {
            "frame": self.frame_count,
            "preprocess": round(preprocess_time, 2),
            "tensorrt": round(inference_time, 2),
            "postprocess": round(postprocess_time, 2),
            "total": round(total_time, 2),
            "average": round(average_time, 2),
            "fps": round(pipeline_fps, 2),
            "detections": detection_count
        }

        # Print every 30 frames
        if self.frame_count % 30 == 0:

            print(
                "\n📊 VisionEdge Performance"
            )

            print(
                f"Frame        : {self.frame_count}"
            )

            print(
                f"Preprocess   : {preprocess_time:.2f} ms"
            )

            print(
                f"TensorRT     : {inference_time:.2f} ms"
            )

            print(
                f"Postprocess  : {postprocess_time:.2f} ms"
            )

            print(
                f"Total        : {total_time:.2f} ms"
            )

            print(
                f"Average      : {average_time:.2f} ms"
            )

            print(
                f"Pipeline FPS : {pipeline_fps:.2f}"
            )

            print(
                f"Detections   : {detection_count}"
            )

        # -------------------------------------------------
        # RETURN WEBRTC FRAME
        # -------------------------------------------------

        new_frame = VideoFrame.from_ndarray(
            image,
            format="bgr24"
        )

        new_frame.pts = frame.pts
        new_frame.time_base = frame.time_base

        return new_frame