import { useEffect, useRef, useState } from "react";
import "./App.css";

const BACKEND_URL = "http://127.0.0.1:8000";

function App() {
  const videoRef = useRef(null);
  const peerRef = useRef(null);
  const metricsIntervalRef = useRef(null);

  const [status, setStatus] = useState("Disconnected");
  const [streaming, setStreaming] = useState(false);

  const [metrics, setMetrics] = useState({
    fps: "—",
    inference: "—",
    preprocess: "—",
    postprocess: "—",
    detections: "—",
    total: "—",
    average: "—",
  });

  // -------------------------------------------------
  // FETCH LIVE METRICS
  // -------------------------------------------------

  async function fetchMetrics() {
    try {
      const response = await fetch(`${BACKEND_URL}/metrics`);

      if (!response.ok) {
        return;
      }

      const data = await response.json();

      if (!data.active || !data.latest_metrics) {
        return;
      }

      const live = data.latest_metrics;

      setMetrics({
        fps:
          live.fps !== undefined
            ? `≈${Number(live.fps).toFixed(1)}`
            : "—",

        inference:
          live.inference !== undefined
            ? `≈${Number(live.inference).toFixed(2)} ms`
            : "—",

        preprocess:
          live.preprocess !== undefined
            ? `≈${Number(live.preprocess).toFixed(2)} ms`
            : "—",

        postprocess:
          live.postprocess !== undefined
            ? `≈${Number(live.postprocess).toFixed(2)} ms`
            : "—",

        detections:
          live.detections !== undefined
            ? live.detections
            : "—",

        total:
          live.total !== undefined
            ? `≈${Number(live.total).toFixed(2)} ms`
            : "—",

        average:
          live.average !== undefined
            ? `≈${Number(live.average).toFixed(2)} ms`
            : "—",
      });
    } catch (error) {
      console.error("Failed to fetch metrics:", error);
    }
  }

  // -------------------------------------------------
  // START METRICS POLLING
  // -------------------------------------------------

  function startMetricsPolling() {
    fetchMetrics();

    metricsIntervalRef.current = setInterval(() => {
      fetchMetrics();
    }, 500);
  }

  // -------------------------------------------------
  // STOP METRICS POLLING
  // -------------------------------------------------

  function stopMetricsPolling() {
    if (metricsIntervalRef.current) {
      clearInterval(metricsIntervalRef.current);
      metricsIntervalRef.current = null;
    }
  }

  // -------------------------------------------------
  // START WEBRTC STREAM
  // -------------------------------------------------

  async function startStream() {
    try {
      if (peerRef.current) {
        console.log("⚠️ Stream already running");
        return;
      }
      setStatus("Connecting...");

      const pc = new RTCPeerConnection();

      peerRef.current = pc;

      pc.addTransceiver("video", {
        direction: "recvonly",
      });

      pc.ontrack = (event) => {
        console.log("🎥 WebRTC video track received");

        if (videoRef.current) {
          videoRef.current.srcObject = event.streams[0];
        }

        setStatus("Streaming");
        setStreaming(true);

        // Start live metrics
        startMetricsPolling();
      };

      pc.onconnectionstatechange = () => {
      console.log(
      "WebRTC connection:",
      pc.connectionState
    );

    if (pc.connectionState === "connected") {
      setStatus("Streaming");
      setStreaming(true);
    }

    if (
      pc.connectionState === "failed" ||
      pc.connectionState === "disconnected" ||
      pc.connectionState === "closed"
    ) {
      setStatus("Disconnected");
      setStreaming(false);
      peerRef.current = null;
    }
  };

      const offer = await pc.createOffer();

      await pc.setLocalDescription(offer);

      // Wait for ICE gathering to complete.
      await new Promise((resolve) => {
        if (pc.iceGatheringState === "complete") {
          resolve();
          return;
        }

        const checkState = () => {
          if (pc.iceGatheringState === "complete") {
            pc.removeEventListener(
              "icegatheringstatechange",
              checkState
            );

            resolve();
          }
        };

        pc.addEventListener(
          "icegatheringstatechange",
          checkState
        );
      });

      const response = await fetch(
        `${BACKEND_URL}/offer`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            sdp: pc.localDescription.sdp,
            type: pc.localDescription.type,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(
          `Backend returned ${response.status}`
        );
      }

      const answer = await response.json();

      await pc.setRemoteDescription(
        new RTCSessionDescription(answer)
      );

      console.log(
        "✅ WebRTC connection established"
      );

    } catch (error) {
      console.error(
        "❌ WebRTC connection failed:",
        error
      );

      setStatus("Connection Failed");
      setStreaming(false);
      stopMetricsPolling();
    }
  }

  // -------------------------------------------------
  // FETCH METRICS
  // -------------------------------------------------

  async function fetchMetrics() {
    try {
      const response = await fetch(`${BACKEND_URL}/metrics`);

      if (!response.ok) {
        throw new Error("Failed to fetch metrics");
      }

      const data = await response.json();

      if (!data.active) {
        return;
      }

      setMetrics({
        fps: `≈${data.fps}`,
        inference: `≈${data.tensorrt} ms`,
        preprocess: `≈${data.preprocess} ms`,
        postprocess: `≈${data.postprocess} ms`,
        detections: data.detections,
      });

      console.log("📊 Metrics:", data);

    } catch (error) {
      console.error("❌ Metrics fetch failed:", error);
    }
  }


  // -------------------------------------------------
  // STOP WEBRTC STREAM
  // -------------------------------------------------

  function stopStream() {
    stopMetricsPolling();

    if (peerRef.current) {
      peerRef.current.close();
      peerRef.current = null;
    }

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }

    setStatus("Disconnected");
    setStreaming(false);

    setMetrics({
      fps: "—",
      inference: "—",
      preprocess: "—",
      postprocess: "—",
      detections: "—",
      total: "—",
      average: "—",
    });
  }

  // -------------------------------------------------
  // CLEANUP
  // -------------------------------------------------

  useEffect(() => {
    const interval = setInterval(() => {
      fetchMetrics();
    }, 500);

    return () => {
      clearInterval(interval);

      if (peerRef.current) {
      peerRef.current.close();
      }
    };
  }, []);

  // -------------------------------------------------
  // UI
  // -------------------------------------------------

  return (
    <div className="app">

      <header className="header">

        <div>
          <h1>VisionEdge</h1>

          <p>
            Hardware-Accelerated Video Analytics
          </p>
        </div>

        <div className="status">

          <span
            className={`status-dot ${
              streaming ? "active" : ""
            }`}
          ></span>

          {status}

        </div>

      </header>

      <main className="dashboard">

        {/* ----------------------------------------- */}
        {/* VIDEO */}
        {/* ----------------------------------------- */}

        <section className="video-card">

          <div className="card-header">

            <div>
              <h2>Live Detection Stream</h2>

              <p>
                YOLOv10 + TensorRT + WebRTC
              </p>
            </div>

            <span className="live-badge">
              {streaming ? "LIVE" : "OFFLINE"}
            </span>

          </div>

          <div className="video-container">

            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="video"
            />

            {!streaming && (
              <div className="video-placeholder">

                <div className="play-icon">
                  ▶
                </div>

                <h3>
                  VisionEdge Video Stream
                </h3>

                <p>
                  Start the WebRTC stream to begin
                  detection
                </p>

              </div>
            )}

          </div>

          <div className="stream-controls">

            {!streaming ? (
              <button
                className="start-button"
                onClick={startStream}
              >
                ▶ Start Stream
              </button>
            ) : (
              <button
                className="stop-button"
                onClick={stopStream}
              >
                ■ Stop Stream
              </button>
            )}

          </div>

        </section>

        {/* ----------------------------------------- */}
        {/* LIVE METRICS */}
        {/* ----------------------------------------- */}

        <section className="metrics">

          <div className="metric-card">

            <span>Pipeline FPS</span>

            <strong>
              {metrics.fps}
            </strong>

            <small>
              Frames / second
            </small>

          </div>

          <div className="metric-card">

            <span>TensorRT</span>

            <strong>
              {metrics.inference}
            </strong>

            <small>
              Inference time
            </small>

          </div>

          <div className="metric-card">

            <span>Preprocessing</span>

            <strong>
              {metrics.preprocess}
            </strong>

            <small>
              Frame preparation
            </small>

          </div>

          <div className="metric-card">

            <span>Detections</span>

            <strong>
              {metrics.detections}
            </strong>

            <small>
              Objects / frame
            </small>

          </div>

        </section>

        {/* ----------------------------------------- */}
        {/* PERFORMANCE */}
        {/* ----------------------------------------- */}

        <section className="performance-card">

          <h2>Measured Performance</h2>

          <div className="performance-grid">

            <div>
              <span>TensorRT inference</span>

              <strong>
                {metrics.inference}
              </strong>
            </div>

            <div>
              <span>Preprocessing</span>

              <strong>
                {metrics.preprocess}
              </strong>
            </div>

            <div>
              <span>Postprocessing</span>

              <strong>
                {metrics.postprocess}
              </strong>
            </div>

            <div>
              <span>Live pipeline</span>

              <strong>
                {metrics.fps} FPS
              </strong>
            </div>

            <div>
              <span>Source video</span>

              <strong>
                59.94 FPS
              </strong>
            </div>

            <div>
              <span>Resolution</span>

              <strong>
                1280 × 720
              </strong>
            </div>

          </div>

        </section>

        {/* ----------------------------------------- */}
        {/* BACKEND */}
        {/* ----------------------------------------- */}

        <section className="backend-card">

          <div>

            <h2>
              VisionEdge Pipeline
            </h2>

            <p>
              FastAPI → aiortc → TensorRT → WebRTC
            </p>

          </div>

          <div className="backend-status">

            <span className="status-dot active"></span>

            Backend Ready

          </div>

        </section>

      </main>

      <footer>
        VisionEdge • Computer Vision & Edge Computing
      </footer>

    </div>
  );
}

export default App;