import subprocess


def get_gpu_metrics():
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu="
                "utilization.gpu,"
                "memory.used,"
                "memory.total,"
                "temperature.gpu,"
                "power.draw",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=2,
        )

        if result.returncode != 0:
            return {
                "available": False,
                "error": "nvidia-smi failed",
            }

        values = [
            value.strip()
            for value in result.stdout.strip().split(",")
        ]

        if len(values) != 5:
            return {
                "available": False,
                "error": "Unexpected nvidia-smi output",
            }

        return {
            "available": True,
            "gpu_utilization": float(values[0]),
            "memory_used": float(values[1]),
            "memory_total": float(values[2]),
            "temperature": float(values[3]),
            "power": float(values[4]),
        }

    except Exception as error:
        return {
            "available": False,
            "error": str(error),
        }