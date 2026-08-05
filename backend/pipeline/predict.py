from pathlib import Path

from backend.pipeline.loader import load_model


INPUT_IMAGE = Path("assets/images/input/test.png")
OUTPUT_DIR = Path("assets/images/output")


def predict():

    model = load_model()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not INPUT_IMAGE.exists():
        raise FileNotFoundError(f"Input image not found: {INPUT_IMAGE}")

    results = model.predict(
        source=str(INPUT_IMAGE),
        save=True,
        project=str(OUTPUT_DIR),
        name="",
        exist_ok=True,
        conf=0.25
    )

    print("\nDetection Results\n")

    for result in results:

        for box in result.boxes:

            cls = int(box.cls[0])
            confidence = float(box.conf[0])

            print(
                f"{model.names[cls]} | "
                f"Confidence: {confidence:.2f}"
            )


if __name__ == "__main__":
    predict()