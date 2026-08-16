import { useEffect, useRef, useState } from "react";
import "./App.css";

const BACKEND_URL = "http://127.0.0.1:8000";

function App() {
  const videoRef = useRef(null);
  const peerRef = useRef(null);
  const metricsIntervalRef = useRef(null);

  const [status, setStatus] = useState("Disconnected");
  const [streaming, setStreaming] = useState(false);
  const [systemStatus, setSystemStatus] = useState(null);

  const [gpuMetrics, setGpuMetrics] = useState({
    utilization: "—",
    memory: "—",
    temperature: "—",
    power: "—",
  });

  const [metrics, setMetrics] = useState({
    fps: "—",
    inference: "—",
    preprocess: "—",
    postprocess: "—",
    detections: "—",
    total: "—",
    average: "—",
  });

  const [performanceHistory, setPerformanceHistory] = useState([]);



  // -------------------------------------------------
  // FETCH SYSTEM STATUS
  // -------------------------------------------------

  async function fetchStatus() {
    try {
      const response = await fetch(`${BACKEND_URL}/status`);

      if (!response.ok) {
        throw new Error("Failed to fetch system status");
      }

      const data = await response.json();

      setSystemStatus(data);

      if (data.gpu?.available) {
        setGpuMetrics({
          utilization: `${Number(data.gpu.gpu_utilization).toFixed(1)}%`,
          memory: `${Number(data.gpu.memory_used).toFixed(0)} / ${Number(
            data.gpu.memory_total
          ).toFixed(0)} MB`,
          temperature: `${Number(data.gpu.temperature).toFixed(0)}°C`,
          power: `${Number(data.gpu.power).toFixed(2)} W`,
        });
      }

      console.log("🖥️ System Status:", data);

    } catch (error) {
      console.error("❌ Status fetch failed:", error);
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

      // ---------------------------------------------
      // UPDATE LIVE METRICS
      // ---------------------------------------------

      setMetrics({
        fps:
          data.fps !== undefined
            ? `≈${Number(data.fps).toFixed(2)}`
            : "—",

        inference:
          data.tensorrt !== undefined
            ? `≈${Number(data.tensorrt).toFixed(2)} ms`
            : "—",

        preprocess:
          data.preprocess !== undefined
            ? `≈${Number(data.preprocess).toFixed(2)} ms`
            : "—",

        postprocess:
          data.postprocess !== undefined
            ? `≈${Number(data.postprocess).toFixed(2)} ms`
            : "—",

        detections:
          data.detections !== undefined
            ? data.detections
            : "—",

        total:
          data.total !== undefined
            ? `≈${Number(data.total).toFixed(2)} ms`
            : "—",

        average:
          data.average !== undefined
            ? `≈${Number(data.average).toFixed(2)} ms`
            : "—",
      });

      // ---------------------------------------------
      // ADD PERFORMANCE SAMPLE
      // ---------------------------------------------

      setPerformanceHistory((previous) => {
        const sample = {
          time: new Date().toLocaleTimeString(),
          fps: Number(data.fps) || 0,
          inference: Number(data.tensorrt) || 0,
          total: Number(data.total) || 0,
        };

        return [...previous, sample].slice(-30);
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

    setPerformanceHistory([]);
  }

  // -------------------------------------------------
  // CLEANUP
  // -------------------------------------------------

  useEffect(() => {
    // Initial status fetch
    fetchStatus();

    // Live metrics polling
    const metricsInterval = setInterval(() => {
      fetchMetrics();
    }, 500);

    // GPU + system status polling
    const statusInterval = setInterval(() => {
      fetchStatus();
    }, 1000);

    return () => {
      clearInterval(metricsInterval);
      clearInterval(statusInterval);

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
            className={`status-dot ${streaming ? "active" : ""
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
        {/* PERFORMANCE CHART */}
        {/* ----------------------------------------- */}

        <section className="performance-chart-card">

          <div className="chart-header">

            <div>
              <h2>Live Performance</h2>

              <p>
                Real-time pipeline performance over the last 15 seconds
              </p>
            </div>

            <div className="chart-live-indicator">
              <span className="status-dot active"></span>
              LIVE
            </div>

          </div>

          <div className="chart-stats">

            <div>
              <span>Current FPS</span>
              <strong>
                {metrics.fps}
              </strong>
            </div>

            <div>
              <span>TensorRT</span>
              <strong>
                {metrics.inference}
              </strong>
            </div>

            <div>
              <span>Samples</span>
              <strong>
                {performanceHistory.length}
              </strong>
            </div>

          </div>

          <div className="performance-chart">

            {performanceHistory.length === 0 ? (

              <div className="chart-empty">
                Start the stream to collect performance data
              </div>

            ) : (

              performanceHistory.map((sample, index) => {

                const maxFPS = Math.max(
                  ...performanceHistory.map(
                    (item) => item.fps
                  ),
                  1
                );

                const height = Math.max(
                  8,
                  (sample.fps / maxFPS) * 100
                );

                return (
                  <div
                    className="chart-bar"
                    key={`${sample.time}-${index}`}
                    style={{
                      height: `${height}%`,
                    }}
                    title={`${sample.time} • ${sample.fps.toFixed(1)} FPS • ${sample.inference.toFixed(2)} ms`}
                  ></div>
                );

              })

            )}

          </div>

          <div className="chart-footer">

            <span>
              FPS
            </span>

            <span>
              Hover bars for detailed measurements
            </span>

          </div>

        </section>


        {/* ----------------------------------------- */}
        {/* GPU MONITORING */}
        {/* ----------------------------------------- */}

        <section className="gpu-card">

          <div className="gpu-header">

            <div>
              <h2>GPU Monitoring</h2>

              <p>
                NVIDIA RTX 3050 hardware utilization
              </p>
            </div>

            <div className="gpu-live">
              <span className="status-dot active"></span>
              LIVE
            </div>

          </div>

          <div className="gpu-grid">

            <div className="gpu-metric">
              <span>GPU Utilization</span>

              <strong>
                {gpuMetrics.utilization}
              </strong>

              <small>
                Compute utilization
              </small>
            </div>

            <div className="gpu-metric">
              <span>VRAM Usage</span>

              <strong>
                {gpuMetrics.memory}
              </strong>

              <small>
                Memory used / total
              </small>
            </div>

            <div className="gpu-metric">
              <span>Temperature</span>

              <strong>
                {gpuMetrics.temperature}
              </strong>

              <small>
                GPU temperature
              </small>
            </div>

            <div className="gpu-metric">
              <span>Power</span>

              <strong>
                {gpuMetrics.power}
              </strong>

              <small>
                Current power draw
              </small>
            </div>

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

          <div className="backend-info">

            <div className="backend-title-row">

              <h2>
                VisionEdge Pipeline
              </h2>

              <span className="system-badge">
                {systemStatus?.backend === "online"
                  ? "SYSTEM ONLINE"
                  : "SYSTEM OFFLINE"}
              </span>

            </div>

            <p>
              FastAPI → aiortc → TensorRT → WebRTC
            </p>

            <div className="pipeline-status">

              <span>
                <strong>Backend</strong>
                {systemStatus?.backend || "—"}
              </span>

              <span>
                <strong>Engine</strong>
                {systemStatus?.tensorRT || "TensorRT"}
              </span>

              <span>
                <strong>Source</strong>
                {systemStatus?.video_source || "—"}
              </span>

              <span>
                <strong>Peers</strong>
                {systemStatus?.active_peers ?? "—"}
              </span>

            </div>

          </div>

          <div className="backend-status">

            <span
              className={`status-dot ${systemStatus?.streaming ? "active" : ""
                }`}
            ></span>

            {systemStatus?.streaming
              ? "Stream Active"
              : "Backend Ready"}

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