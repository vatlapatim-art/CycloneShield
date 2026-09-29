import { useEffect, useMemo, useRef, useState } from "react";
import axios from "axios";

import {
  MapContainer,
  TileLayer,
  Polyline,
  Popup,
  CircleMarker,
  Circle,
  Rectangle,
  Marker,
  useMap,
} from "react-leaflet";

import {
  Activity,
  CloudRain,
  Database,
  Droplets,
  Mountain,
  Satellite,
  ShieldCheck,
  Waves,
  Wind,
  Route,
  Layers3,
  MapPinned,
  AlertTriangle,
  Crosshair,
  Maximize2,
  LocateFixed,
  Building2,
  Gauge,
  CircleGauge,
  X,
  ExternalLink,
  RefreshCw,
  FileText,
  Radio,
  BrainCircuit,
  Send,
  Play,
  Pause,
  Upload,
  Clipboard,
  Timer,
  TrendingUp,
} from "lucide-react";

import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "./index.css";


/* =========================================================
   API
   ========================================================= */

const API_BASE = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

const AMPHAN_SID = "2020136N10088";

const FLOOD_BOUNDS = [
  [21.5, 87.5],
  [23.0, 89.0],
];

const EXPOSURE_RADIUS = 250;


/* =========================================================
   MAP CONTROLLER
   ========================================================= */

function MapController({
  trackCoordinates,
  exposureCoordinates,
  peakIntensityPoint,
  selectedFacilityPoint,
  viewMode,
}) {
  const map = useMap();

  useEffect(() => {
    const timer = setTimeout(() => {
      map.invalidateSize();
    }, 300);

    return () => clearTimeout(timer);
  }, [map]);

  useEffect(() => {
    if (viewMode === "flood") {
      map.fitBounds(FLOOD_BOUNDS, {
        padding: [45, 45],
        maxZoom: 9,
        animate: true,
        duration: 0.8,
      });
      return;
    }

    if (
      viewMode === "exposure" &&
      exposureCoordinates.length > 0
    ) {
      map.fitBounds(exposureCoordinates, {
        padding: [70, 70],
        maxZoom: 10,
        animate: true,
        duration: 0.8,
      });
      return;
    }

    if (
      viewMode === "facility" &&
      selectedFacilityPoint
    ) {
      map.flyTo(
        selectedFacilityPoint,
        12,
        {
          animate: true,
          duration: 0.9,
        }
      );
      return;
    }

    if (
      viewMode === "peak" &&
      peakIntensityPoint
    ) {
      map.flyTo(
        peakIntensityPoint,
        8,
        {
          animate: true,
          duration: 0.9,
        }
      );
      return;
    }

    if (
      viewMode === "track" &&
      trackCoordinates.length > 1
    ) {
      map.fitBounds(trackCoordinates, {
        padding: [55, 55],
        maxZoom: 7,
        animate: true,
        duration: 0.8,
      });
    }
  }, [
    map,
    trackCoordinates,
    exposureCoordinates,
    peakIntensityPoint,
    selectedFacilityPoint,
    viewMode,
  ]);

  return null;
}


/* =========================================================
   BROADCAST-STYLE CYCLONE VORTEX
   ========================================================= */

function CycloneVortex({ center, wind, pressure, visible = true }) {
  const map = useMap();
  const [zoom, setZoom] = useState(() => map.getZoom());

  useEffect(() => {
    if (!map) return undefined;

    const updateZoom = () => setZoom(map.getZoom());
    map.on("zoomend", updateZoom);
    return () => map.off("zoomend", updateZoom);
  }, [map]);

  if (!center || !visible) return null;

  const windValue = Number.isFinite(Number(wind)) ? Number(wind) : null;
  const pressureValue = Number.isFinite(Number(pressure)) ? Number(pressure) : null;
  // Keep the animated wind field geographically tied to the map zoom instead
  // of leaving it at a fixed 280px icon size. At low zoom it shrinks so it
  // doesn't dominate the whole map; when zoomed in it expands naturally.
  const latitude = Number(center?.[0]) || 0;
  const metersPerPixel = (40075016.686 * Math.cos((latitude * Math.PI) / 180)) / (256 * Math.pow(2, zoom));
  const baseDiameterMeters = (windValue && windValue >= 120 ? 150000 : windValue && windValue >= 64 ? 125000 : 100000);
  const geographicSize = baseDiameterMeters / Math.max(1, metersPerPixel);
  const vortexSize = Math.round(Math.max(64, Math.min(170, geographicSize)));

  const html = `
    <div class="cyclone-vortex" style="--vortex-size:${vortexSize}px" aria-hidden="true">
      <div class="vortex-label">${windValue ? `${windValue} KT` : "CYCLONE"}</div>
      <svg class="vortex-svg" viewBox="0 0 280 280" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <radialGradient id="vortexGlow" cx="50%" cy="50%">
            <stop offset="0%" stop-color="#ffffff" stop-opacity="0.95"/>
            <stop offset="20%" stop-color="#d8f7ff" stop-opacity="0.60"/>
            <stop offset="52%" stop-color="#4bd7ff" stop-opacity="0.17"/>
            <stop offset="100%" stop-color="#4bd7ff" stop-opacity="0"/>
          </radialGradient>
          <filter id="softGlow" x="-80%" y="-80%" width="260%" height="260%">
            <feGaussianBlur stdDeviation="5" result="blur"/>
            <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
        </defs>
        <circle cx="140" cy="140" r="120" fill="url(#vortexGlow)"/>
        <g class="vortex-orbit orbit-slow">
          <ellipse cx="140" cy="140" rx="112" ry="82" fill="none" stroke="#65dfff" stroke-opacity="0.18" stroke-width="2" stroke-dasharray="2 12"/>
          <ellipse cx="140" cy="140" rx="92" ry="66" fill="none" stroke="#65dfff" stroke-opacity="0.22" stroke-width="2" stroke-dasharray="3 10"/>
        </g>
        <g class="vortex-orbit orbit-fast">
          <path d="M31 132 C43 67 102 25 161 38 C224 51 251 112 228 168 C204 227 129 248 73 217 C22 188 19 127 48 88 C76 49 130 44 172 68 C210 91 220 131 202 166 C183 203 135 216 96 194 C61 175 53 140 66 110 C78 82 110 67 139 75 C169 83 184 106 179 132 C174 160 145 177 119 169 C96 162 84 141 88 121 C92 101 111 89 129 94" fill="none" stroke="#c8f6ff" stroke-opacity="0.48" stroke-width="3.6" stroke-linecap="round"/>
          <path d="M54 196 C15 140 32 77 86 49 C141 20 207 50 232 106 C256 160 224 222 168 241" fill="none" stroke="#53d6ff" stroke-opacity="0.26" stroke-width="8" stroke-linecap="round"/>
          <path d="M94 226 C52 196 44 146 63 111 C85 72 133 63 171 85 C207 106 217 148 194 180 C170 213 124 220 92 198" fill="none" stroke="#ffffff" stroke-opacity="0.22" stroke-width="2.4" stroke-linecap="round"/>
        </g>
        <g class="vortex-particles">
          <circle class="particle p1" cx="140" cy="30" r="3"/>
          <circle class="particle p2" cx="218" cy="102" r="3"/>
          <circle class="particle p3" cx="203" cy="200" r="2.8"/>
          <circle class="particle p4" cx="71" cy="203" r="2.7"/>
          <circle class="particle p5" cx="57" cy="92" r="2.5"/>
          <circle class="particle p6" cx="164" cy="74" r="2.4"/>
        </g>
        <circle cx="140" cy="140" r="24" fill="#06111c" fill-opacity="0.92" stroke="#d6fbff" stroke-opacity="0.9" stroke-width="2.5"/>
        <circle cx="140" cy="140" r="10" fill="#effcff" filter="url(#softGlow)"/>
        <circle cx="140" cy="140" r="4" fill="#ffffff"/>
        <circle class="vortex-eye-halo" cx="140" cy="140" r="43" fill="none" stroke="#a7f0ff" stroke-opacity="0.22" stroke-width="1.5" stroke-dasharray="5 7"/>
      </svg>
      <div class="vortex-meta">${pressureValue ? `${Math.round(pressureValue)} MB` : "IBTRACS OBSERVED CENTER"}</div>
    </div>`;

  const icon = L.divIcon({
    className: "cyclone-vortex-icon",
    html,
    iconSize: [vortexSize, vortexSize],
    iconAnchor: [vortexSize / 2, vortexSize / 2],
  });

  return <Marker position={center} icon={icon} interactive={false} zIndexOffset={900} />;
}


/* =========================================================
   METEOROLOGICAL BROADCAST WIND FLOW
   ========================================================= */

function CycloneFlowOverlay({ field = null, observations = [], activeCenter = null, visible = true, showIsobars = true }) {
  const map = useMap();
  const heatRef = useRef(null);
  const flowRef = useRef(null);
  const contourRef = useRef(null);
  const frameRef = useRef(0);
  const sceneRef = useRef(null);
  const dirtyRef = useRef(true);
  const movingRef = useRef(false);
  const lastBuildRef = useRef(0);
  const lastFrameRef = useRef(0);

  const trackPoints = useMemo(() => (
    observations
      .map((o, index) => ({
        lat: Number(o?.lat),
        lon: Number(o?.lon),
        wind: Number(o?.wmo_wind_kt),
        speed: Number(o?.storm_speed_kt),
        direction: Number(o?.storm_direction_deg),
        index,
      }))
      .filter((p) => Number.isFinite(p.lat) && Number.isFinite(p.lon))
  ), [observations]);

  useEffect(() => {
    if (!map || !field?.data?.length || !heatRef.current || !flowRef.current || !contourRef.current) return undefined;

    const heat = heatRef.current;
    const flow = flowRef.current;
    const contour = contourRef.current;
    const container = map.getContainer();
    if (!container) return undefined;

    for (const canvas of [heat, flow, contour]) {
      if (canvas.parentNode !== container) container.appendChild(canvas);
    }

    const setCanvasSize = () => {
      const size = map.getSize();
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      for (const canvas of [heat, flow, contour]) {
        canvas.width = Math.max(1, Math.floor(size.x * dpr));
        canvas.height = Math.max(1, Math.floor(size.y * dpr));
        canvas.style.width = `${size.x}px`;
        canvas.style.height = `${size.y}px`;
        canvas.style.left = "0px";
        canvas.style.top = "0px";
        canvas.__dpr = dpr;
      }
      dirtyRef.current = true;
    };

    const setMotionVisibility = (isVisible) => {
      for (const canvas of [heat, flow, contour]) {
        canvas.style.opacity = isVisible ? "" : "0";
      }
    };
    const beginMovement = () => {
      // Freeze and temporarily hide the raster/vector wind layer during
      // Leaflet zoom/pan. Reprojecting on every intermediate frame is what
      // caused the previous wind layer to stutter and drift.
      movingRef.current = true;
      setMotionVisibility(false);
    };
    const endMovement = () => {
      movingRef.current = false;
      dirtyRef.current = true;
      requestAnimationFrame(() => {
        if (!movingRef.current) setMotionVisibility(true);
      });
    };

    setCanvasSize();
    map.on("resize", setCanvasSize);
    map.on("movestart", beginMovement);
    map.on("zoomstart", beginMovement);
    map.on("moveend", endMovement);
    map.on("zoomend", endMovement);

    const cleanup = () => {
      map.off("resize", setCanvasSize);
      map.off("movestart", beginMovement);
      map.off("zoomstart", beginMovement);
      map.off("moveend", endMovement);
      map.off("zoomend", endMovement);
      cancelAnimationFrame(frameRef.current);
      sceneRef.current = null;
      lastBuildRef.current = 0;
      lastFrameRef.current = 0;
      for (const canvas of [heat, flow, contour]) {
        if (canvas.parentNode === container) container.removeChild(canvas);
      }
    };

    const clamp = (value, min, max) => Math.max(min, Math.min(max, value));

    const buildScene = () => {
      const heatCtx = heat.getContext("2d");
      const flowCtx = flow.getContext("2d");
      const contourCtx = contour.getContext("2d");
      if (!heatCtx || !flowCtx || !contourCtx) return;

      const dpr = heat.__dpr || Math.min(window.devicePixelRatio || 1, 2);
      const width = map.getSize().x;
      const height = map.getSize().y;
      const values = [...field.data].sort((a, b) => (a.j - b.j) || (a.i - b.i));
      const cols = Number(field.cols) || 1;
      const rows = Number(field.rows) || 1;
      if (cols < 2 || rows < 2) return;

      const nodes = new Array(rows * cols);
      for (const item of values) {
        const i = Number(item.i);
        const j = Number(item.j);
        if (!Number.isInteger(i) || !Number.isInteger(j) || i < 0 || i >= cols || j < 0 || j >= rows) continue;
        const point = map.latLngToContainerPoint([Number(item.lat), Number(item.lon)]);
        nodes[j * cols + i] = {
          x: point.x,
          y: point.y,
          lat: Number(item.lat),
          lon: Number(item.lon),
          u: Number(item.u_ms) || 0,
          v: Number(item.v_ms) || 0,
          speed: Number(item.speed_kt) || 0,
          pressure: Number(item.mslp_hpa) || 1013,
        };
      }

      const validNodes = nodes.filter(Boolean);
      if (validNodes.length < 4) return;

      const gridLeft = Math.min(...validNodes.map(n => n.x));
      const gridRight = Math.max(...validNodes.map(n => n.x));
      const gridTop = Math.min(...validNodes.map(n => n.y));
      const gridBottom = Math.max(...validNodes.map(n => n.y));

      const stormTrack = trackPoints.map((p, idx) => {
        const projected = map.latLngToContainerPoint([p.lat, p.lon]);
        let direction = p.direction;
        if (!Number.isFinite(direction)) {
          const prev = trackPoints[Math.max(0, idx - 1)];
          const next = trackPoints[Math.min(trackPoints.length - 1, idx + 1)];
          if (prev && next && Number.isFinite(prev.lat) && Number.isFinite(next.lat)) {
            const dy = next.lat - prev.lat;
            const dx = (next.lon - prev.lon) * Math.cos(p.lat * Math.PI / 180);
            if (Math.abs(dx) + Math.abs(dy) > 1e-6) {
              direction = (Math.atan2(dx, dy) * 180 / Math.PI + 360) % 360;
            }
          }
        }
        const wind = Number.isFinite(p.wind) ? p.wind : 20;
        return {
          x: projected.x,
          y: projected.y,
          lat: p.lat,
          lon: p.lon,
          wind,
          direction: Number.isFinite(direction) ? direction : 0,
        };
      });

      const nearestStorm = (x, y) => {
        if (stormTrack.length === 0) return null;
        if (stormTrack.length === 1) {
          const s = stormTrack[0];
          const dx = x - s.x;
          const dy = y - s.y;
          const distancePx = Math.hypot(dx, dy);
          const metersPerPixel = (40075016.686 * Math.max(0.1, Math.cos(s.lat * Math.PI / 180))) / (256 * Math.pow(2, map.getZoom()));
          const radiusKm = clamp(85 + Math.max(0, s.wind - 25) * 2.05, 85, 300);
          return { ...s, x: s.x, y: s.y, distancePx, radiusPx: Math.max(24, (radiusKm * 1000) / Math.max(1, metersPerPixel)) };
        }

        let best = null;
        let bestD2 = Infinity;
        for (let i = 0; i < stormTrack.length - 1; i++) {
          const a = stormTrack[i];
          const b = stormTrack[i + 1];
          const dx = b.x - a.x;
          const dy = b.y - a.y;
          const len2 = dx * dx + dy * dy;
          const t = len2 > 1e-6 ? clamp(((x - a.x) * dx + (y - a.y) * dy) / len2, 0, 1) : 0;
          const px = a.x + dx * t;
          const py = a.y + dy * t;
          const ddx = x - px;
          const ddy = y - py;
          const d2 = ddx * ddx + ddy * ddy;
          if (d2 < bestD2) {
            const windA = Number.isFinite(a.wind) ? a.wind : 20;
            const windB = Number.isFinite(b.wind) ? b.wind : windA;
            const wind = windA + (windB - windA) * t;
            const lat = a.lat + (b.lat - a.lat) * t;
            // Use the actual observed movement direction when available; otherwise
            // derive the heading from the adjacent track segment.
            let direction = Number.isFinite(a.direction) ? a.direction : null;
            if (!Number.isFinite(direction)) {
              direction = (Math.atan2(dx, -dy) * 180 / Math.PI + 360) % 360;
            }
            bestD2 = d2;
            best = { x: px, y: py, lat, lon: a.lon + (b.lon - a.lon) * t, wind, direction };
          }
        }
        if (!best) return null;
        const latitude = best.lat * Math.PI / 180;
        const metersPerPixel = (40075016.686 * Math.max(0.1, Math.cos(latitude))) / (256 * Math.pow(2, map.getZoom()));
        const radiusKm = clamp(85 + Math.max(0, best.wind - 25) * 2.05, 85, 300);
        const radiusPx = Math.max(24, (radiusKm * 1000) / Math.max(1, metersPerPixel));
        return { ...best, distancePx: Math.sqrt(bestD2), radiusPx };
      };

      const colorStops = [
        [0, [35, 92, 205]],
        [20, [29, 180, 224]],
        [35, [49, 202, 132]],
        [50, [185, 224, 79]],
        [65, [255, 219, 70]],
        [80, [255, 145, 62]],
        [100, [247, 68, 67]],
        [120, [231, 49, 104]],
        [140, [182, 63, 196]],
      ];
      const colorForWind = (speed) => {
        const s = clamp(speed, 0, 140);
        for (let i = 0; i < colorStops.length - 1; i++) {
          const [a, ca] = colorStops[i];
          const [b, cb] = colorStops[i + 1];
          if (s <= b) {
            const q = (s - a) / (b - a);
            return ca.map((x, idx) => Math.round(x + (cb[idx] - x) * q));
          }
        }
        return colorStops[colorStops.length - 1][1];
      };

      const rowFromScreenY = (py) => {
        const f = clamp(((py - gridTop) / Math.max(1, gridBottom - gridTop)) * (rows - 1), 0, rows - 1.00001);
        const northRow = rows - 1 - Math.floor(f);
        return { northRow, southRow: Math.max(0, northRow - 1), ty: f - Math.floor(f) };
      };

      const sampleGrid = (px, py) => {
        if (px < gridLeft - 2 || px > gridRight + 2 || py < gridTop - 2 || py > gridBottom + 2) return null;
        const fx = clamp(((px - gridLeft) / Math.max(1, gridRight - gridLeft)) * (cols - 1), 0, cols - 1.00001);
        const i = Math.floor(fx);
        const tx = fx - i;
        const { northRow, southRow, ty } = rowFromScreenY(py);
        const right = Math.min(cols - 1, i + 1);
        const a = nodes[northRow * cols + i];
        const b = nodes[northRow * cols + right];
        const c = nodes[southRow * cols + right];
        const d = nodes[southRow * cols + i];
        if (!a || !b || !c || !d) return null;
        const bilerp = (va, vb, vc, vd) => {
          const top = va + (vb - va) * tx;
          const bottom = vd + (vc - vd) * tx;
          return top + (bottom - top) * ty;
        };
        return {
          speed: bilerp(a.speed, b.speed, c.speed, d.speed),
          u: bilerp(a.u, b.u, c.u, d.u),
          v: bilerp(a.v, b.v, c.v, d.v),
          pressure: bilerp(a.pressure, b.pressure, c.pressure, d.pressure),
        };
      };

      // The ERA5 field stays visible everywhere, while a separate track-aware
      // intensity envelope paints a geographically bounded swath along the
      // COMPLETE observed IBTrACS track. This is a derived visualization, not
      // a claim of measured 10 m winds at every point in the swath.
      const rasterW = Math.max(180, Math.min(300, Math.ceil(width / 5)));
      const rasterH = Math.max(110, Math.min(190, Math.ceil(height / 5)));
      const img = heatCtx.createImageData(rasterW, rasterH);
      let ptr = 0;
      for (let py = 0; py < rasterH; py++) {
        const sy = gridTop + (py / Math.max(1, rasterH - 1)) * (gridBottom - gridTop);
        for (let px = 0; px < rasterW; px++) {
          const sx = gridLeft + (px / Math.max(1, rasterW - 1)) * (gridRight - gridLeft);
          const base = sampleGrid(sx, sy);
          if (!base) { ptr += 4; continue; }

          const storm = nearestStorm(sx, sy);
          let stormWind = 0;
          let stormInfluence = 0;
          if (storm) {
            const q = storm.distancePx / storm.radiusPx;
            stormInfluence = q < 1.9 ? Math.exp(-q * q * 1.32) : 0;
            stormWind = storm.wind * stormInfluence;
          }

          const displayedWind = Math.max(base.speed, stormWind);
          const c = colorForWind(displayedWind);
          const baseNorm = clamp(base.speed / 60, 0, 1);
          const stormNorm = clamp(stormWind / 130, 0, 1);
          // Broadcast-style saturation: the real ERA5 background stays visible
          // across the full map, while the observed-intensity-derived storm
          // envelope becomes progressively brighter toward the core/track.
          const alpha = clamp(Math.round(34 + baseNorm * 70 + stormNorm * 155), 30, 220);
          img.data[ptr++] = c[0];
          img.data[ptr++] = c[1];
          img.data[ptr++] = c[2];
          img.data[ptr++] = alpha;
        }
      }
      const offscreen = document.createElement("canvas");
      offscreen.width = rasterW;
      offscreen.height = rasterH;
      offscreen.getContext("2d")?.putImageData(img, 0, 0);
      heatCtx.setTransform(1, 0, 0, 1, 0, 0);
      heatCtx.clearRect(0, 0, heat.width, heat.height);
      heatCtx.setTransform(dpr, 0, 0, dpr, 0, 0);
      heatCtx.filter = "blur(3px)";
      heatCtx.drawImage(offscreen, gridLeft, gridTop, gridRight - gridLeft, gridBottom - gridTop);
      heatCtx.filter = "none";

      // Pressure contours from the real ERA5 MSLP grid.
      contourCtx.setTransform(1, 0, 0, 1, 0, 0);
      contourCtx.clearRect(0, 0, contour.width, contour.height);
      contourCtx.setTransform(dpr, 0, 0, dpr, 0, 0);
      contourCtx.lineWidth = 0.75;
      contourCtx.strokeStyle = "rgba(255,255,255,0.16)";
      contourCtx.fillStyle = "rgba(255,255,255,0.50)";
      contourCtx.font = "10px ui-monospace, SFMono-Regular, Menlo, monospace";
      const pressureValues = validNodes.map(v => v.pressure).filter(Number.isFinite);
      const minP = pressureValues.length ? Math.floor(Math.min(...pressureValues) / 2) * 2 : 990;
      const maxP = pressureValues.length ? Math.ceil(Math.max(...pressureValues) / 2) * 2 : 1010;
      const levels = [];
      for (let level = Math.ceil(minP / 4) * 4; level <= maxP; level += 4) levels.push(level);
      const edgeIntersection = (level, a, b) => {
        const dv = b.pressure - a.pressure;
        const q = Math.abs(dv) < 1e-6 ? 0.5 : clamp((level - a.pressure) / dv, 0, 1);
        return { x: a.x + (b.x - a.x) * q, y: a.y + (b.y - a.y) * q };
      };
      let labels = 0;
      for (let j = 0; j < rows - 1; j++) {
        for (let i = 0; i < cols - 1; i++) {
          const a = nodes[j * cols + i];
          const b = nodes[j * cols + i + 1];
          const c = nodes[(j + 1) * cols + i + 1];
          const d = nodes[(j + 1) * cols + i];
          if (!a || !b || !c || !d) continue;
          for (const level of levels) {
            const hits = [];
            if ((a.pressure < level) !== (b.pressure < level)) hits.push(edgeIntersection(level, a, b));
            if ((b.pressure < level) !== (c.pressure < level)) hits.push(edgeIntersection(level, b, c));
            if ((c.pressure < level) !== (d.pressure < level)) hits.push(edgeIntersection(level, c, d));
            if ((d.pressure < level) !== (a.pressure < level)) hits.push(edgeIntersection(level, d, a));
            if (hits.length >= 2) {
              contourCtx.beginPath();
              contourCtx.moveTo(hits[0].x, hits[0].y);
              contourCtx.lineTo(hits[1].x, hits[1].y);
              contourCtx.stroke();
              if (labels < 8 && hits[0].x > gridLeft && hits[0].x < gridRight && hits[0].y > gridTop && hits[0].y < gridBottom) {
                contourCtx.fillText(String(level), hits[0].x + 3, hits[0].y - 3);
                labels += 1;
              }
            }
          }
        }
      }

      const vectorAt = (x, y) => {
        const sample = sampleGrid(x, y);
        if (!sample) return null;
        const mag = Math.hypot(sample.u, sample.v);
        if (!Number.isFinite(mag) || mag < 0.12) return null;
        return { east: sample.u / mag, north: sample.v / mag, speed: sample.speed };
      };

      const fieldVector = (x, y) => {
        const base = vectorAt(x, y);
        if (!base) return null;

        const storm = nearestStorm(x, y);
        const baseX = base.east;
        const baseY = -base.north;
        if (!storm || storm.distancePx > storm.radiusPx * 2.0) {
          return { ...base, dirX: baseX, dirY: baseY };
        }

        const dx = x - storm.x;
        const dy = y - storm.y;
        const r = Math.max(1, Math.hypot(dx, dy));
        const q = storm.distancePx / storm.radiusPx;
        const circulation = Math.exp(-q * q * 1.15) * clamp(storm.wind / 120, 0.18, 1);
        // Northern Hemisphere cyclonic flow: counter-clockwise.
        const tangentX = dy / r;
        const tangentY = -dx / r;
        const inwardX = -dx / r;
        const inwardY = -dy / r;
        const dirRad = storm.direction * Math.PI / 180;
        const motionX = Math.sin(dirRad);
        const motionY = -Math.cos(dirRad);
        const swirlWeight = clamp(0.10 + circulation * 0.48, 0.10, 0.58);
        const motionWeight = clamp(0.025 + circulation * 0.075, 0.025, 0.10);
        let dirX = baseX * (1 - swirlWeight - motionWeight) + tangentX * swirlWeight + motionX * motionWeight + inwardX * circulation * 0.035;
        let dirY = baseY * (1 - swirlWeight - motionWeight) + tangentY * swirlWeight + motionY * motionWeight + inwardY * circulation * 0.035;
        const n = Math.hypot(dirX, dirY) || 1;
        dirX /= n;
        dirY /= n;
        return { ...base, dirX, dirY };
      };

      const trace = (x0, y0, direction, step = 5.4, maxSteps = 108) => {
        const path = [{ x: x0, y: y0 }];
        let x = x0;
        let y = y0;
        for (let k = 0; k < maxSteps; k++) {
          const v1 = fieldVector(x, y);
          if (!v1) break;
          const mx = x + v1.dirX * direction * step * 0.5;
          const my = y + v1.dirY * direction * step * 0.5;
          const v2 = fieldVector(mx, my);
          if (!v2) break;
          x += v2.dirX * direction * step;
          y += v2.dirY * direction * step;
          if (x < gridLeft || x > gridRight || y < gridTop || y > gridBottom) break;
          path.push({ x, y });
        }
        return path;
      };

      const seedCols = Math.max(22, Math.round(width / 52));
      const seedRows = Math.max(14, Math.round(height / 52));
      const streamlines = [];
      for (let gy = 0; gy <= seedRows; gy++) {
        for (let gx = 0; gx <= seedCols; gx++) {
          const x = gridLeft + ((gx + 0.43) / Math.max(1, seedCols + 0.43)) * (gridRight - gridLeft);
          const y = gridTop + ((gy + 0.38) / Math.max(1, seedRows + 0.38)) * (gridBottom - gridTop);
          if (x < gridLeft || x > gridRight || y < gridTop || y > gridBottom) continue;
          const forward = trace(x, y, 1);
          const backward = trace(x, y, -1);
          const path = [...backward.reverse(), ...forward.slice(1)];
          if (path.length < 12) continue;
          let totalSpeed = 0;
          let count = 0;
          for (let p = 0; p < path.length; p += 6) {
            const vv = fieldVector(path[p].x, path[p].y);
            if (vv) { totalSpeed += Math.max(vv.speed, 1); count += 1; }
          }
          const stormSample = nearestStorm(x, y);
          const localWind = stormSample ? stormSample.wind : 0;
          streamlines.push({
            path,
            speed: count ? totalSpeed / count : 0,
            phase: (gx * 37 + gy * 61) % 211,
            localStormWind: localWind,
          });
        }
      }

      sceneRef.current = {
        streamlines: streamlines.slice(0, 620),
        displayMax: 140,
      };
      lastBuildRef.current = performance.now();
      contour.style.opacity = showIsobars ? "1" : "0";
    };

    const drawTrackMotion = (ctx) => {
      if (trackPoints.length < 2) return;
      ctx.save();
      ctx.lineWidth = 1.1;
      ctx.strokeStyle = "rgba(255,255,255,0.24)";
      ctx.fillStyle = "rgba(255,255,255,0.55)";
      for (let i = 0; i < trackPoints.length - 1; i += 2) {
        const a = map.latLngToContainerPoint([trackPoints[i].lat, trackPoints[i].lon]);
        const b = map.latLngToContainerPoint([trackPoints[Math.min(i + 1, trackPoints.length - 1)].lat, trackPoints[Math.min(i + 1, trackPoints.length - 1)].lon]);
        const dx = b.x - a.x;
        const dy = b.y - a.y;
        const mag = Math.hypot(dx, dy);
        if (mag < 11) continue;
        const ux = dx / mag;
        const uy = dy / mag;
        const size = 5.5;
        const px = b.x - ux * 2;
        const py = b.y - uy * 2;
        ctx.beginPath();
        ctx.moveTo(px, py);
        ctx.lineTo(px - ux * size - uy * size * 0.62, py - uy * size + ux * size * 0.62);
        ctx.lineTo(px - ux * size + uy * size * 0.62, py - uy * size - ux * size * 0.62);
        ctx.closePath();
        ctx.fill();
      }
      ctx.restore();
    };

    const drawFlow = (ts) => {
      lastFrameRef.current = ts;
      const rebuildInterval = movingRef.current ? 120 : 0;
      if (!sceneRef.current || dirtyRef.current) {
        if (!movingRef.current && ts - lastBuildRef.current >= rebuildInterval) {
          buildScene();
          dirtyRef.current = false;
        }
      }

      const flowCtx = flow.getContext("2d");
      if (!flowCtx || !sceneRef.current) {
        frameRef.current = requestAnimationFrame(drawFlow);
        return;
      }

      const dpr = flow.__dpr || Math.min(window.devicePixelRatio || 1, 2);
      flowCtx.setTransform(1, 0, 0, 1, 0, 0);
      flowCtx.clearRect(0, 0, flow.width, flow.height);
      if (!visible) {
        frameRef.current = requestAnimationFrame(drawFlow);
        return;
      }

      flowCtx.setTransform(dpr, 0, 0, dpr, 0, 0);
      drawTrackMotion(flowCtx);

      const { streamlines } = sceneRef.current;
      for (const line of streamlines) {
        const pts = line.path;
        if (pts.length < 8) continue;
        const speedNorm = clamp(line.speed / 70, 0, 1);
        const stormBoost = clamp(line.localStormWind / 130, 0, 1);
        flowCtx.strokeStyle = `rgba(239,249,255,${0.055 + speedNorm * 0.08 + stormBoost * 0.035})`;
        flowCtx.lineWidth = 0.55 + speedNorm * 0.28 + stormBoost * 0.20;
        flowCtx.lineCap = "round";
        flowCtx.beginPath();
        flowCtx.moveTo(pts[0].x, pts[0].y);
        for (let k = 1; k < pts.length; k++) flowCtx.lineTo(pts[k].x, pts[k].y);
        flowCtx.stroke();
      }

      flowCtx.globalCompositeOperation = "lighter";
      for (const line of streamlines) {
        const pts = line.path;
        if (pts.length < 8) continue;
        const speedNorm = clamp(line.speed / 70, 0, 1);
        const stormBoost = clamp(line.localStormWind / 130, 0, 1);
        const offset = ((ts * 0.001 * (24 + speedNorm * 90 + stormBoost * 45)) + line.phase * 13) % 280;
        const pos = Math.floor((offset / 280) * (pts.length - 1));
        const head = pts[pos];
        if (!head) continue;
        let accum = 0;
        const tail = 18 + speedNorm * 24 + stormBoost * 20;
        flowCtx.strokeStyle = `rgba(255,255,255,${0.18 + speedNorm * 0.30 + stormBoost * 0.26})`;
        flowCtx.lineWidth = 0.85 + speedNorm * 0.35 + stormBoost * 0.26;
        flowCtx.beginPath();
        flowCtx.moveTo(head.x, head.y);
        for (let k = 1; k < pts.length && accum < tail; k++) {
          const idx = pos - k;
          if (idx < 0) break;
          const a = pts[idx];
          const b = pts[idx + 1];
          accum += Math.hypot(b.x - a.x, b.y - a.y);
          flowCtx.lineTo(a.x, a.y);
        }
        flowCtx.stroke();
      }
      flowCtx.globalCompositeOperation = "source-over";
      flowCtx.setTransform(1, 0, 0, 1, 0, 0);
      frameRef.current = requestAnimationFrame(drawFlow);
    };

    dirtyRef.current = true;
    frameRef.current = requestAnimationFrame(drawFlow);
    return cleanup;
  }, [map, field, trackPoints, visible, showIsobars]);

  return (
    <>
      <canvas ref={heatRef} className="meteorological-wind-canvas meteo-heat-canvas" aria-hidden="true" />
      <canvas ref={flowRef} className="meteorological-wind-canvas meteo-flow-canvas" aria-label="ERA5 environmental wind field with derived cyclone intensity envelope" />
      <canvas ref={contourRef} className="meteorological-wind-canvas meteo-contour-canvas" aria-hidden="true" />
    </>
  );
}

/* =========================================================
   MAP WIND PROBE
   ========================================================= */

function MapWindProbe({ field, enabled = true }) {
  const map = useMap();
  const [probe, setProbe] = useState(null);

  useEffect(() => {
    if (!map || !enabled || !field?.data?.length) return undefined;
    const data = field.data || [];
    let lastUpdate = 0;
    const onMove = (event) => {
      const now = performance.now();
      if (now - lastUpdate < 100) return;
      lastUpdate = now;
      const lat = event.latlng.lat;
      const lon = event.latlng.lng;
      let best = null;
      let bestDistance = Infinity;
      for (let i = 0; i < data.length; i += 1) {
        const point = data[i];
        const dLat = (Number(point.lat) - lat) * 111.32;
        const dLon = (Number(point.lon) - lon) * 111.32 * Math.cos((lat * Math.PI) / 180);
        const d2 = dLat * dLat + dLon * dLon;
        if (d2 < bestDistance) { bestDistance = d2; best = point; }
      }
      if (!best) return;
      const u = Number(best.u_ms) || 0;
      const v = Number(best.v_ms) || 0;
      const direction = (Math.atan2(u, v) * 180 / Math.PI + 360) % 360;
      const labels = ["N","NE","E","SE","S","SW","W","NW"];
      const compass = labels[Math.round(direction / 45) % 8];
      setProbe({ x: event.containerPoint.x, y: event.containerPoint.y, speed: Number(best.speed_kt).toFixed(1), pressure: Number(best.mslp_hpa).toFixed(0), compass });
    };
    const onOut = () => setProbe(null);
    map.on("mousemove", onMove);
    map.on("mouseout", onOut);
    return () => { map.off("mousemove", onMove); map.off("mouseout", onOut); };
  }, [map, field, enabled]);

  if (!probe || !enabled) return null;
  return <div className="wind-probe" style={{ left: probe.x + 16, top: probe.y + 16 }}><strong>{probe.speed} kt</strong><span>{probe.compass} · ERA5 10 m</span><span>{probe.pressure} hPa MSLP</span></div>;
}

/* =========================================================
   DECISION-SUPPORT / AI COMMAND CENTER
   ========================================================= */

function riskColor(band) {
  if (band === "EXTREME") return "#ff315f";
  if (band === "HIGH") return "#ff8c42";
  if (band === "ELEVATED") return "#ffd166";
  return "#35c9bf";
}

function MissionControl({
  ready,
  cyclone,
  flood,
  terrain,
  rainfall,
  exposure,
  surgeData,
  pathwaysData,
  riskAssets,
  riskSummary,
  advisories,
  onSurgeData,
  onPathwaysData,
  onRiskAssets,
  onRiskSummary,
  onAdvisories,
}) {
  const [busy, setBusy] = useState(false);
  const [scenario, setScenario] = useState(null);
  const [leadHours, setLeadHours] = useState(12);
  const [aiBrief, setAiBrief] = useState(null);
  const [aiBusy, setAiBusy] = useState(false);
  const [imageBase64, setImageBase64] = useState("");
  const [imageName, setImageName] = useState("");
  const [dispatchStatus, setDispatchStatus] = useState(null);
  const [dispatchBusy, setDispatchBusy] = useState(false);
  const [copied, setCopied] = useState(false);

  const baseContext = useMemo(() => ({
    event: cyclone?.track?.properties?.name || "Cyclone event",
    season: cyclone?.track?.properties?.season,
    observations: cyclone?.observations?.slice?.(-20) || [],
    flood: flood ? {
      candidate_area_km2: flood.candidate_area_km2,
      before_scene_count: flood.before_scene_count,
      after_scene_count: flood.after_scene_count,
      method: flood.method,
    } : null,
    rainfall: rainfall ? {
      mean_mm: rainfall.rainfall_mean_mm,
      max_mm: rainfall.rainfall_max_mm,
      min_mm: rainfall.rainfall_min_mm,
      images: rainfall.image_count,
    } : null,
    terrain,
    exposure,
    risk: riskSummary,
    surge: surgeData ? { max_surge_potential_m: surgeData.max_surge_potential_m, hotspots: surgeData.hotspots?.slice?.(0, 8) } : null,
    pathways: pathwaysData ? { hotspots: pathwaysData.hotspots?.slice?.(0, 8) } : null,
    top_assets: riskAssets?.top?.slice?.(0, 10) || [],
  }), [cyclone, flood, rainfall, terrain, exposure, riskSummary, surgeData, pathwaysData, riskAssets]);

  async function runIntelligence() {
    if (!ready) return;
    setBusy(true);
    try {
      const [riskRes, scenarioRes, surgeRes, pathRes, assetsRes, advisoryRes] = await Promise.allSettled([
        axios.post(`${API_BASE}/risk/summary`, { cyclone, flood, terrain, rainfall, exposure }),
        axios.get(`${API_BASE}/risk/scenario?lead_hours=${leadHours}`),
        axios.get(`${API_BASE}/surge/grid`, { timeout: 120000 }),
        axios.get(`${API_BASE}/rainfall/pathways`, { timeout: 120000 }),
        axios.get(`${API_BASE}/risk/assets`, { timeout: 120000 }),
        axios.post(`${API_BASE}/advisories/generate`, { cyclone, flood, terrain, rainfall, exposure }),
      ]);
      if (riskRes.status === "fulfilled") onRiskSummary(riskRes.value.data);
      if (scenarioRes.status === "fulfilled") setScenario(scenarioRes.value.data);
      if (surgeRes.status === "fulfilled") onSurgeData(surgeRes.value.data);
      if (pathRes.status === "fulfilled") onPathwaysData(pathRes.value.data);
      if (assetsRes.status === "fulfilled") onRiskAssets(assetsRes.value.data);
      if (advisoryRes.status === "fulfilled") onAdvisories(advisoryRes.value.data);
    } finally {
      setBusy(false);
    }
  }

  async function changeScenario(value) {
    const hours = Number(value);
    setLeadHours(hours);
    try {
      const res = await axios.get(`${API_BASE}/risk/scenario?lead_hours=${hours}`);
      setScenario(res.data);
    } catch (error) {
      console.warn("Scenario unavailable", error);
    }
  }

  async function generateAI() {
    setAiBusy(true);
    try {
      const response = await axios.post(`${API_BASE}/ai/brief`, {
        context: baseContext,
        image_base64: imageBase64 || null,
        mime_type: "image/png",
      }, { timeout: 60000 });
      setAiBrief(response.data);
    } finally {
      setAiBusy(false);
    }
  }

  async function loadDispatchStatus() {
    try {
      const res = await axios.get(`${API_BASE}/advisories/status`);
      setDispatchStatus(res.data);
    } catch (error) {
      console.warn("Dispatch status unavailable", error);
    }
  }

  async function dispatch() {
    if (!advisories?.advisories?.length) return;
    setDispatchBusy(true);
    try {
      const response = await axios.post(`${API_BASE}/advisories/dispatch`, { advisories: advisories.advisories, recipients: [] });
      setDispatchStatus((prev) => ({ ...(prev || {}), last_dispatch: response.data }));
    } catch (error) {
      setDispatchStatus((prev) => ({ ...(prev || {}), error: error?.response?.data?.detail || error.message }));
    } finally {
      setDispatchBusy(false);
    }
  }

  function handleImage(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    setImageName(file.name);
    const reader = new FileReader();
    reader.onload = () => {
      const value = String(reader.result || "");
      setImageBase64(value.includes(",") ? value.split(",", 2)[1] : value);
    };
    reader.readAsDataURL(file);
  }

  const advisoryText = advisories?.advisories?.map((a) => `${a.priority} — ${a.audience}\n${a.subject}\n${a.message}`).join("\n\n") || "";

  async function copyAdvisories() {
    if (!advisoryText) return;
    await navigator.clipboard?.writeText(advisoryText);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1600);
  }

  return (
    <section className="mission-control">
      <div className="mission-head">
        <div>
          <div className="section-kicker">DECISION SUPPORT</div>
          <h2><BrainCircuit size={20} /> CycloneShield Command Center</h2>
          <p>Hazard → vulnerability → AI reasoning → action. Derived planning outputs remain clearly separated from observed datasets.</p>
        </div>
        <div className="mission-actions">
          <button className="mission-primary" onClick={runIntelligence} disabled={!ready || busy}>
            <TrendingUp size={15} /> {busy ? "Running analysis…" : "Run impact intelligence"}
          </button>
          <button className="mission-secondary" onClick={loadDispatchStatus}><Send size={14} /> Dispatch status</button>
        </div>
      </div>

      <div className="mission-grid">
        <div className="mission-card risk-card">
          <div className="mission-card-label">PREDICTIVE RISK</div>
          <div className="risk-score-row">
            <strong>{riskSummary?.risk_score ?? "—"}</strong>
            <span style={{ borderColor: riskColor(riskSummary?.risk_band), color: riskColor(riskSummary?.risk_band) }}>{riskSummary?.risk_band || "NOT RUN"}</span>
          </div>
          <div className="driver-list">
            {(riskSummary?.drivers || []).slice(0, 5).map((driver) => (
              <div className="driver-row" key={driver.name}>
                <span>{driver.name}</span><strong>{driver.score}</strong>
                <div className="driver-bar"><span style={{ width: `${Math.max(0, Math.min(100, driver.score))}%` }} /></div>
              </div>
            ))}
          </div>
        </div>

        <div className="mission-card scenario-card">
          <div className="mission-card-label">STORM SCENARIO</div>
          <div className="scenario-controls">
            {[6, 12, 24].map((h) => <button key={h} onClick={() => changeScenario(h)} className={leadHours === h ? "selected" : ""}>{h}h</button>)}
          </div>
          {scenario?.available ? (
            <div className="scenario-main">
              <div><span>Projected position</span><strong>{scenario.projected_position.lat}°, {scenario.projected_position.lon}°</strong></div>
              <div><span>Scenario wind</span><strong>{scenario.scenario_wind_kt} kt</strong></div>
              <div><span>Motion</span><strong>{scenario.storm_motion_kt} kt · {Math.round(scenario.storm_direction_deg)}°</strong></div>
            </div>
          ) : <div className="empty-state">Run impact intelligence to create a planning scenario.</div>}
          <small className="derived-note">Planning scenario from observed motion/intensity; not an official forecast track.</small>
        </div>

        <div className="mission-card surge-card">
          <div className="mission-card-label">STORM-SURGE SIMULATION</div>
          <div className="big-inline">{surgeData?.max_surge_potential_m ?? "—"}<span>m</span></div>
          <p>{surgeData?.hotspots?.length ? `${surgeData.hotspots.length} coastal hotspots ranked` : "Parametric coastal potential not run yet."}</p>
          <small className="derived-note">Uses observed storm wind/pressure + NASADEM/JRC context; not a hydrodynamic forecast.</small>
        </div>

        <div className="mission-card pathways-card">
          <div className="mission-card-label">RAIN → DAMAGE PATHWAYS</div>
          {pathwaysData?.hotspots?.slice(0, 4).map((p, idx) => (
            <div className="pathway-row" key={`${p.lat}-${p.lon}`}><b>{idx + 1}</b><div><strong>{p.pathway}</strong><span>{p.rainfall_mm} mm · {p.elevation_m} m elev.</span></div><em>{p.pathway_score}</em></div>
          )) || <div className="empty-state">Run impact intelligence to map rainfall/terrain pathways.</div>}
        </div>

        <div className="mission-card ai-card">
          <div className="mission-card-label"><BrainCircuit size={14} /> GEMINI MULTIMODAL REASONING</div>
          <div className="ai-upload-row">
            <label className="upload-button"><Upload size={14} /> Add satellite/map image<input type="file" accept="image/*" onChange={handleImage} hidden /></label>
            <span>{imageName || "Optional vision evidence"}</span>
          </div>
          <button className="ai-generate" onClick={generateAI} disabled={aiBusy || !ready}><BrainCircuit size={15} /> {aiBusy ? "Reasoning…" : "Generate AI impact brief"}</button>
          {aiBrief && <div className="ai-output"><div className="ai-badge">{aiBrief.mode === "gemini" ? `GEMINI · ${aiBrief.model}` : (aiBrief.retryable ? "GEMINI TEMPORARILY UNAVAILABLE · LOCAL FALLBACK" : "LOCAL FALLBACK")}{aiBrief.image_used ? " · IMAGE USED" : ""}</div><p>{aiBrief.text}</p>{aiBrief.mode !== "gemini" && aiBrief.attempts ? <small className="derived-note">Automatic retries attempted: {aiBrief.attempts}. {aiBrief.error || "External model did not become available."}</small> : null}</div>}
          <small className="derived-note">AI reasoning is an interpretation layer; it must not be treated as an official warning without human review.</small>
        </div>

        <div className="mission-card advisory-card">
          <div className="mission-card-label"><Send size={14} /> EARLY-WARNING ADVISORIES</div>
          {advisories?.advisories?.slice(0, 4).map((a) => <div className="advisory-row" key={a.id}><span className={`priority-pill ${a.priority.toLowerCase()}`}>{a.priority}</span><div><strong>{a.audience}</strong><span>{a.subject}</span></div></div>) || <div className="empty-state">Run impact intelligence to draft dispatch-ready advisories.</div>}
          <div className="advisory-actions"><button onClick={copyAdvisories} disabled={!advisoryText}><Clipboard size={13}/> {copied ? "Copied" : "Copy drafts"}</button><button onClick={dispatch} disabled={dispatchBusy || !advisories?.advisories?.length}>{dispatchBusy ? "Sending…" : "Dispatch"}</button></div>
          {dispatchStatus?.error && <small className="dispatch-error">{dispatchStatus.error}</small>}
          {dispatchStatus?.last_dispatch && <small className="dispatch-ok">Sent {dispatchStatus.last_dispatch.count} advisory emails.</small>}
        </div>

        <div className="mission-card watchlist-card">
          <div className="mission-card-label">ASSET RISK WATCHLIST</div>
          {riskAssets?.top?.slice(0, 8).map((asset) => <div className="watch-row" key={`${asset.name}-${asset.latitude}-${asset.longitude}`}><span className="watch-score" style={{ background: riskColor(asset.risk_band) }}>{Math.round(asset.risk_score)}</span><div><strong>{asset.name}</strong><span>{asset.category} · {asset.wind_proxy_kt} kt proxy · {asset.rainfall_mm} mm</span></div></div>) || <div className="empty-state">Run impact intelligence to rank facilities.</div>}
        </div>
      </div>
    </section>
  );
}

/* =========================================================
   MAIN APP
   ========================================================= */

function App() {
  const [cyclone, setCyclone] = useState(null);
  const [flood, setFlood] = useState(null);
  const [terrain, setTerrain] = useState(null);
  const [rainfall, setRainfall] = useState(null);
  const [exposure, setExposure] = useState(null);
  const [infrastructure, setInfrastructure] = useState(null);
  const [liveCyclones, setLiveCyclones] = useState([]);
  const [windField, setWindField] = useState(null);
  const [sourceStatus, setSourceStatus] = useState([]);
  const [refreshing, setRefreshing] = useState(false);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [showTrack, setShowTrack] = useState(true);
  const [showFlood, setShowFlood] = useState(true);
  const [showExposure, setShowExposure] = useState(true);
  const [showWindField, setShowWindField] = useState(true);
  const [showIsobars, setShowIsobars] = useState(true);
  const [showSurge, setShowSurge] = useState(true);
  const [showPathways, setShowPathways] = useState(false);
  const [showRiskAssets, setShowRiskAssets] = useState(false);

  const [viewMode, setViewMode] = useState("track");

  const [selectedFacility, setSelectedFacility] = useState(null);
  const [surgeData, setSurgeData] = useState(null);
  const [pathwaysData, setPathwaysData] = useState(null);
  const [riskAssets, setRiskAssets] = useState(null);
  const [riskSummary, setRiskSummary] = useState(null);
  const [advisories, setAdvisories] = useState(null);
  const [activeStormIndex, setActiveStormIndex] = useState(0);
  const [isStormPlaying, setIsStormPlaying] = useState(false);


  /* =======================================================
     LOAD REAL BACKEND DATA
     ======================================================= */

  async function loadDashboard(isRefresh = false) {
    try {
      if (isRefresh) setRefreshing(true);
      else setLoading(true);
      setError("");

      const requests = await Promise.allSettled([
        axios.get(`${API_BASE}/cyclone/${AMPHAN_SID}`, { timeout: 45000 }),
        axios.get(`${API_BASE}/flood`, { timeout: 90000 }),
        axios.get(`${API_BASE}/terrain`, { timeout: 45000 }),
        axios.get(`${API_BASE}/rainfall`, { timeout: 45000 }),
        axios.get(`${API_BASE}/exposure`, { timeout: 120000 }),
        axios.get(`${API_BASE}/infrastructure`, { timeout: 45000 }),
        axios.get(`${API_BASE}/cyclones/live`, { timeout: 20000 }),
        axios.get(`${API_BASE}/data-sources/status`, { timeout: 12000 }),
        axios.get(`${API_BASE}/wind-field`, { timeout: 90000 }),
      ]);

      const [cycloneResponse, floodResponse, terrainResponse, rainfallResponse, exposureResponse, infrastructureResponse, liveResponse, statusResponse, windFieldResponse] = requests;
      const failures = [];

      if (cycloneResponse.status === "fulfilled") setCyclone(cycloneResponse.value.data);
      else failures.push("cyclone track");
      if (floodResponse.status === "fulfilled") setFlood(floodResponse.value.data);
      else failures.push("flood analysis");
      if (terrainResponse.status === "fulfilled") setTerrain(terrainResponse.value.data);
      else failures.push("terrain");
      if (rainfallResponse.status === "fulfilled") setRainfall(rainfallResponse.value.data);
      else failures.push("rainfall");
      if (exposureResponse.status === "fulfilled") setExposure(exposureResponse.value.data);
      else failures.push("infrastructure exposure");
      if (infrastructureResponse.status === "fulfilled") setInfrastructure(infrastructureResponse.value.data);
      else failures.push("infrastructure layer");
      if (liveResponse.status === "fulfilled") {
        setLiveCyclones(liveResponse.value.data?.events ?? []);
        if (liveResponse.value.data?.available === false) console.warn("GDACS live feed unavailable; continuing without live events.");
      }
      if (statusResponse.status === "fulfilled") setSourceStatus(statusResponse.value.data?.sources ?? []);
      if (windFieldResponse.status === "fulfilled") setWindField(windFieldResponse.value.data);
      else failures.push("meteorological wind field");

      if (failures.length) {
        setError(`Some real-data services could not be refreshed: ${failures.join(", ")}. Existing successful data is retained.`);
      }
    } catch (err) {
      console.error("Dashboard loading error:", err);
      setError("Unable to refresh the real-data services.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    loadDashboard(false);
  }, []);

  useEffect(() => {
    if (!cyclone || !flood || !terrain || !rainfall || !exposure) return undefined;
    let cancelled = false;
    Promise.allSettled([
      axios.post(`${API_BASE}/risk/summary`, { cyclone, flood, terrain, rainfall, exposure }, { timeout: 15000 }),
      axios.post(`${API_BASE}/advisories/generate`, { cyclone, flood, terrain, rainfall, exposure }, { timeout: 15000 }),
    ]).then(([riskRes, advisoryRes]) => {
      if (cancelled) return;
      if (riskRes.status === "fulfilled") setRiskSummary(riskRes.value.data);
      if (advisoryRes.status === "fulfilled") setAdvisories(advisoryRes.value.data);
    }).catch(() => {});
    return () => { cancelled = true; };
  }, [cyclone, flood, terrain, rainfall, exposure]);



  /* =======================================================
     CYCLONE TRACK
     ======================================================= */

  const trackCoordinates = useMemo(() => {
    return (
      cyclone?.track?.geometry?.coordinates
        ?.filter(
          (point) =>
            Array.isArray(point) &&
            point.length >= 2 &&
            Number.isFinite(point[0]) &&
            Number.isFinite(point[1])
        )
        ?.map(
          ([lon, lat]) => [lat, lon]
        ) || []
    );
  }, [cyclone]);


  /* =======================================================
     REAL OBSERVATIONS
     ======================================================= */

  const observations =
    cyclone?.observations ?? [];


  /* =======================================================
     INTENSITY
     ======================================================= */

  const trackSegments = useMemo(() => {
    if (trackCoordinates.length < 2) return [];

    return trackCoordinates.slice(0, -1).map((start, index) => {
      const end = trackCoordinates[index + 1];
      const wind = Number.isFinite(Number(observations[index]?.wmo_wind_kt))
        ? Number(observations[index].wmo_wind_kt)
        : null;

      const color =
        wind !== null && wind >= 120
          ? "#ff315f"
          : wind !== null && wind >= 64
          ? "#f59e0b"
          : wind !== null && wind >= 34
          ? "#22d3ee"
          : "#34d399";

      return {
        positions: [start, end],
        color,
        wind,
      };
    });
  }, [trackCoordinates, observations]);


  const intensityObservations = useMemo(() => {
    return observations
      .filter(
        (observation) =>
          Number.isFinite(
            observation?.wmo_wind_kt
          )
      )
      .map((observation) => ({
        time: observation.time,
        wind: Number(
          observation.wmo_wind_kt
        ),
        pressure:
          Number.isFinite(
            observation?.wmo_pressure_mb
          )
            ? Number(
                observation.wmo_pressure_mb
              )
            : null,
        status: observation?.usa_status ?? null,
        lat: Number(
          observation.lat
        ),
        lon: Number(
          observation.lon
        ),
      }));
  }, [observations]);


  const peakIntensityObservation =
    useMemo(() => {
      if (
        intensityObservations.length === 0
      ) {
        return null;
      }

      return intensityObservations.reduce(
        (peak, current) =>
          current.wind > peak.wind
            ? current
            : peak
      );
    }, [intensityObservations]);


  const minimumPressureObservation =
    useMemo(() => {
      const validPressure =
        intensityObservations.filter(
          (observation) =>
            Number.isFinite(
              observation.pressure
            )
        );

      if (
        validPressure.length === 0
      ) {
        return null;
      }

      return validPressure.reduce(
        (minimum, current) =>
          current.pressure <
          minimum.pressure
            ? current
            : minimum
      );
    }, [intensityObservations]);


  const peakIntensityPoint =
    useMemo(() => {
      if (
        !peakIntensityObservation
      ) {
        return null;
      }

      return [
        peakIntensityObservation.lat,
        peakIntensityObservation.lon,
      ];
    }, [peakIntensityObservation]);


  const intensityBars = useMemo(() => {
    if (
      intensityObservations.length === 0
    ) {
      return [];
    }

    const maxWind = Math.max(
      ...intensityObservations.map(
        (observation) =>
          observation.wind
      )
    );

    return intensityObservations.map(
      (observation) => ({
        ...observation,
        height:
          maxWind > 0
            ? Math.max(
                8,
                (
                  observation.wind /
                  maxWind
                ) * 100
              )
            : 8,
      })
    );
  }, [intensityObservations]);


  /* =======================================================
     EXPOSURE
     ======================================================= */

  const nearbyExposureFacilities =
    exposure?.nearby_exposed_features ?? [];

  const allCriticalAssets = useMemo(() => {
    const features = infrastructure?.features ?? [];
    return features.filter((feature) =>
      ["medical", "emergency", "shelter", "power"].includes(feature?.category)
    );
  }, [infrastructure]);


  const exposureCoordinates =
    useMemo(() => {
      return nearbyExposureFacilities
        .filter(
          (feature) =>
            Number.isFinite(
              feature?.latitude
            ) &&
            Number.isFinite(
              feature?.longitude
            )
        )
        .map(
          (feature) => [
            feature.latitude,
            feature.longitude,
          ]
        );
    }, [nearbyExposureFacilities]);


  const selectedFacilityPoint =
    selectedFacility
      ? [
          selectedFacility.latitude,
          selectedFacility.longitude,
        ]
      : null;


  /* =======================================================
     REAL DATA VALUES
     ======================================================= */

  const observationCount =
    cyclone?.track?.properties
      ?.observation_count ?? null;

  const season =
    cyclone?.track?.properties
      ?.season ?? null;

  const floodArea =
    flood?.candidate_area_km2 ?? null;

  const beforeScenes =
    flood?.before_scene_count ?? null;

  const afterScenes =
    flood?.after_scene_count ?? null;

  const floodMapAvailable =
    flood?.map?.available === true;

  const meanElevation =
    terrain?.elevation_mean_m ?? null;

  const minElevation =
    terrain?.elevation_min_m ?? null;

  const maxElevation =
    terrain?.elevation_max_m ?? null;

  const rainfallMean =
    rainfall?.rainfall_mean_mm ?? null;

  const rainfallDays =
    rainfall?.image_count ?? null;

  const rainfallMin =
    rainfall?.rainfall_min_mm ?? null;

  const rainfallMax =
    rainfall?.rainfall_max_mm ?? null;


  /* =======================================================
     EXPOSURE VALUES
     ======================================================= */

  const criticalInfrastructureCount =
    exposure?.total_critical ?? null;

  const directExposureCount =
    exposure?.direct_exposed_count ?? null;

  const nearbyExposureCount =
    exposure?.nearby_exposed_count ?? null;

  const nearbyExposurePercentage =
    exposure?.nearby_exposure_percentage ?? null;

  const exposureDistance =
    exposure?.nearby_distance_meters ??
    EXPOSURE_RADIUS;

  const exposureCategories =
    exposure?.by_category ?? {};

  const medicalNearby =
    exposureCategories?.medical
      ?.nearby_exposed ?? 0;

  const emergencyNearby =
    exposureCategories?.emergency
      ?.nearby_exposed ?? 0;

  const shelterNearby =
    exposureCategories?.shelter
      ?.nearby_exposed ?? 0;

  const powerNearby =
    exposureCategories?.power
      ?.nearby_exposed ?? 0;


  /* =======================================================
     MAP
     ======================================================= */

  const floodTileUrl =
    `${API_BASE}/flood/tiles/{z}/{x}/{y}`;


  /* =======================================================
     TRACK START / END
     ======================================================= */

  const firstTrackPoint =
    trackCoordinates.length > 0
      ? trackCoordinates[0]
      : null;

  const lastTrackPoint =
    trackCoordinates.length > 0
      ? trackCoordinates[
          trackCoordinates.length - 1
        ]
      : null;

  const stormCenterPoint = useMemo(() => {
    if (peakIntensityObservation) {
      return [peakIntensityObservation.lat, peakIntensityObservation.lon];
    }
    return lastTrackPoint ?? null;
  }, [peakIntensityObservation, lastTrackPoint]);


  const activeStormObservation = intensityObservations[
    Math.min(Math.max(activeStormIndex, 0), Math.max(0, intensityObservations.length - 1))
  ] ?? peakIntensityObservation;

  const activeStormPoint = activeStormObservation
    ? [activeStormObservation.lat, activeStormObservation.lon]
    : stormCenterPoint;

  useEffect(() => {
    if (!isStormPlaying || intensityObservations.length < 2) return undefined;
    const timer = window.setInterval(() => {
      setActiveStormIndex((current) => (current + 1) % intensityObservations.length);
    }, 850);
    return () => window.clearInterval(timer);
  }, [isStormPlaying, intensityObservations.length]);

  /* =======================================================
     VIEW ACTIONS
     ======================================================= */

  function focusTrack() {
    setSelectedFacility(null);
    setViewMode("track");
  }

  function focusFlood() {
    setSelectedFacility(null);
    setViewMode("flood");
  }

  function focusExposure() {
    setSelectedFacility(null);

    if (
      exposureCoordinates.length > 0
    ) {
      setViewMode("exposure");
    }
  }

  function focusPeak() {
    setSelectedFacility(null);

    if (
      peakIntensityPoint
    ) {
      setViewMode("peak");
    }
  }

  function resetView() {
    setSelectedFacility(null);
    setViewMode("track");
  }


  function printReport() {
    window.print();
  }


  /* =======================================================
     FACILITY SELECTION
     ======================================================= */

  function selectFacility(
    facility
  ) {
    setSelectedFacility(
      facility
    );

    setViewMode("facility");
  }


  function closeFacility() {
    setSelectedFacility(null);
    setViewMode("track");
  }


  /* =======================================================
     FORMATTERS
     ======================================================= */

  function formatCategory(
    category
  ) {
    if (!category) {
      return "Unknown";
    }

    return (
      category.charAt(0).toUpperCase() +
      category.slice(1)
    );
  }


  function formatObservationTime(
    time
  ) {
    if (!time) {
      return "—";
    }

    const parts =
      time.split(" ");

    if (parts.length < 2) {
      return time;
    }

    return `${parts[0]} · ${parts[1]} UTC`;
  }


  /* =======================================================
     RENDER
     ======================================================= */

  return (
    <div className="app">


      {/* ==================================================
          TOP BAR
          ================================================== */}

      <header className="topbar">

        <div className="topbar-left">

          <div className="brand-icon">
            <Waves
              size={22}
              strokeWidth={2.4}
            />
          </div>

          <div>

            <div className="brand-name">
              CycloneShield
              <span>AI</span>
            </div>

            <div className="brand-subtitle">
              Cyclone Impact & Infrastructure
              Vulnerability Forecaster
            </div>

          </div>

        </div>


        <div className="topbar-right">

          <div className="source-status">

            <span
              className={`status-dot ${
                loading
                  ? "loading"
                  : "online"
              }`}
            />

            {loading
              ? "SYNCING DATA"
              : "DATA PIPELINE ONLINE"}

          </div>


          <button className="toolbar-button" onClick={() => loadDashboard(true)} disabled={refreshing}>
            <RefreshCw size={14} className={refreshing ? "spin" : ""} />
            {refreshing ? "Refreshing" : "Refresh"}
          </button>

          <button className="toolbar-button" onClick={printReport}>
            <FileText size={14} />
            Report
          </button>

          <div className="system-chip">
            <Activity size={15} />
            Earth Engine
          </div>

        </div>

      </header>


      {/* ==================================================
          STATUS
          ================================================== */}

      {loading && (
        <div className="notice loading-notice">

          <div className="loading-spinner"></div>

          Loading real satellite, rainfall,
          terrain, cyclone and infrastructure
          exposure data...

        </div>
      )}


      {error && (
        <div className="notice error-notice">

          <AlertTriangle size={17} />

          {error}

        </div>
      )}


      <div className="live-strip">
        <div><Radio size={15} /><strong>LIVE GDACS</strong> {liveCyclones.length} tropical cyclone event{liveCyclones.length === 1 ? "" : "s"} in the India / Indian Ocean view.</div>
        <div className="source-mini-list">
          {sourceStatus.slice(0, 4).map((source) => (
            <span key={source.name} className={`source-mini ${source.status}`}>{source.name}</span>
          ))}
        </div>
      </div>


      {/* ==================================================
          HERO
          ================================================== */}

      <section className="hero">

        <div className="hero-copy">

          <div className="section-kicker">
            HISTORICAL EVENT ANALYSIS
          </div>

          <h1>
            Cyclone
            <span> Amphan</span>
          </h1>

          <p>
            Real-data reconstruction using NOAA
            IBTrACS, Sentinel-1, Dynamic World,
            CHIRPS, NASADEM and OpenStreetMap
            infrastructure.
          </p>

        </div>


        <div className="event-badge">

          <div className="event-badge-icon">
            <Wind size={18} />
          </div>

          <div>

            <div className="event-badge-label">
              STORM SEASON
            </div>

            <div className="event-badge-value">
              {season ?? "—"}
            </div>

          </div>

        </div>

      </section>


      {/* ==================================================
          CORE METRICS
          ================================================== */}

      <section className="metrics-grid">


        <div className="metric-card">

          <div className="metric-top">

            <div className="metric-icon">
              <Route size={18} />
            </div>

            <span className="metric-source">
              IBTRACS
            </span>

          </div>

          <div className="metric-label">
            TRACK OBSERVATIONS
          </div>

          <div className="metric-number">
            {observationCount ?? "—"}
          </div>

          <div className="metric-description">
            Real cyclone track points
          </div>

        </div>


        <div className="metric-card intensity-metric">

          <div className="metric-top">

            <div className="metric-icon intensity-icon">
              <Gauge size={18} />
            </div>

            <span className="metric-source">
              IBTRACS
            </span>

          </div>

          <div className="metric-label">
            PEAK WMO WIND
          </div>

          <div className="metric-number">

            {peakIntensityObservation
              ? peakIntensityObservation.wind
              : "—"}

            <span className="metric-unit">
              kt
            </span>

          </div>

          <div className="metric-description">
            Maximum WMO wind observation
          </div>

        </div>


        <div className="metric-card pressure-metric">

          <div className="metric-top">

            <div className="metric-icon pressure-icon">
              <CircleGauge size={18} />
            </div>

            <span className="metric-source">
              IBTRACS
            </span>

          </div>

          <div className="metric-label">
            MINIMUM WMO PRESSURE
          </div>

          <div className="metric-number">

            {minimumPressureObservation
              ? minimumPressureObservation.pressure
              : "—"}

            <span className="metric-unit">
              mb
            </span>

          </div>

          <div className="metric-description">
            Lowest pressure observation
          </div>

        </div>


        <div className="metric-card highlight-card">

          <div className="metric-top">

            <div className="metric-icon flood-icon">
              <Droplets size={18} />
            </div>

            <span className="metric-source">
              SATELLITE
            </span>

          </div>

          <div className="metric-label">
            NEW-WATER CANDIDATE
          </div>

          <div className="metric-number">

            {floodArea !== null
              ? Number(
                  floodArea
                ).toFixed(2)
              : "—"}

            <span className="metric-unit">
              km²
            </span>

          </div>

          <div className="metric-description">
            Sentinel-1 + Dynamic World
          </div>

        </div>


        <div className="metric-card exposure-metric">

          <div className="metric-top">

            <div className="metric-icon exposure-icon">
              <Building2 size={18} />
            </div>

            <span className="metric-source">
              OSM + GEE
            </span>

          </div>

          <div className="metric-label">
            CRITICAL ASSETS MAPPED
          </div>

          <div className="metric-number">
            {allCriticalAssets.length || "—"}
          </div>

          <div className="metric-description">

            {exposureDistance !== null
              ? `${nearbyExposureCount ?? 0} within ${exposureDistance} m · ${
                  nearbyExposurePercentage !== null
                    ? `${Number(nearbyExposurePercentage).toFixed(2)}%`
                    : "—"
                } candidate-exposed`
              : "Real OpenStreetMap critical infrastructure"}

          </div>

        </div>

      </section>


      {liveCyclones.length > 0 && (
        <section className="live-events-section">
          <div className="section-kicker">LIVE TROPICAL CYCLONES</div>
          <div className="live-events-grid">
            {liveCyclones.slice(0, 6).map((event) => (
              <div className="live-event-card" key={event.id ?? `${event.latitude}-${event.longitude}`}>
                <div className="live-event-top"><Radio size={14} /><span>{event.severity.toUpperCase()}</span></div>
                <strong>{event.name}</strong>
                <span>{event.latitude.toFixed(2)}°N · {event.longitude.toFixed(2)}°E</span>
                <small>Source: GDACS · {event.modified ?? "current feed"}</small>
              </div>
            ))}
          </div>
        </section>
      )}


      {/* ==================================================
          IMPACT INTELLIGENCE
          ================================================== */}

      <section className="impact-intelligence">

        <div className="impact-head">

          <div>

            <div className="section-kicker">
              IMPACT INTELLIGENCE
            </div>

            <h2>
              From Storm Signal to Infrastructure Exposure
            </h2>

          </div>

          <div className="impact-status">

            <ShieldCheck size={14} />

            REAL-DATA EVIDENCE CHAIN

          </div>

        </div>


        <div className="impact-grid">


          <div className="impact-block">

            <div className="impact-block-head">

              <div className="impact-number-icon">
                <Wind size={17} />
              </div>

              <div>

                <span>
                  HAZARD SIGNAL
                </span>

                <strong>
                  Event observations
                </strong>

              </div>

            </div>


            <div className="impact-stat-grid">

              <div>
                <span>Track</span>

                <strong>
                  {observationCount ?? "—"}
                </strong>
              </div>


              <div>
                <span>Peak WMO</span>

                <strong>
                  {peakIntensityObservation
                    ? `${peakIntensityObservation.wind} kt`
                    : "—"}
                </strong>
              </div>

            </div>

          </div>


          <div className="impact-block">

            <div className="impact-block-head">

              <div className="impact-number-icon satellite">
                <Satellite size={17} />
              </div>

              <div>

                <span>
                  SATELLITE SIGNAL
                </span>

                <strong>
                  New-water candidate
                </strong>

              </div>

            </div>


            <div className="impact-main-number">

              {floodArea !== null
                ? Number(
                    floodArea
                  ).toFixed(2)
                : "—"}

              <small>
                km²
              </small>

            </div>


            <div className="impact-caption">
              Sentinel-1 SAR change + Dynamic World
            </div>

          </div>


          <div className="impact-block exposure-block">

            <div className="impact-block-head">

              <div className="impact-number-icon exposure">
                <Building2 size={17} />
              </div>

              <div>

                <span>
                  EXPOSURE SIGNAL
                </span>

                <strong>
                  Critical infrastructure
                </strong>

              </div>

            </div>


            <div className="impact-main-number">

              {nearbyExposureCount ?? "—"}

              <small>
                assets
              </small>

            </div>


            <div className="impact-caption">

              Within {exposureDistance ?? "—"} m ·{" "}
              {nearbyExposurePercentage !== null
                ? `${Number(
                    nearbyExposurePercentage
                  ).toFixed(2)}%`
                : "—"}{" "}
              candidate proximity

            </div>

          </div>

        </div>


        <div className="evidence-chain">

          <div className="chain-label">
            EVIDENCE CHAIN
          </div>

          <div className="chain">

            <div className="chain-node">
              <Wind size={14} />
              <span>STORM</span>
            </div>

            <div className="chain-arrow">
              →
            </div>

            <div className="chain-node">
              <CloudRain size={14} />
              <span>RAINFALL</span>
            </div>

            <div className="chain-arrow">
              →
            </div>

            <div className="chain-node">
              <Satellite size={14} />
              <span>SATELLITE</span>
            </div>

            <div className="chain-arrow">
              →
            </div>

            <div className="chain-node">
              <Droplets size={14} />
              <span>NEW WATER</span>
            </div>

            <div className="chain-arrow">
              →
            </div>

            <div className="chain-node">
              <Building2 size={14} />
              <span>INFRASTRUCTURE</span>
            </div>

          </div>

        </div>

      </section>


      {/* ==================================================
          INTENSITY PROFILE
          ================================================== */}

      <section className="intensity-section">

        <div className="intensity-header">

          <div>

            <div className="section-kicker">
              STORM DYNAMICS
            </div>

            <h2>
              Cyclone Intensity Profile
            </h2>

            <p>
              WMO wind observations from the real
              NOAA IBTrACS track.
            </p>

          </div>


          <button
            className="intensity-focus-button"
            onClick={focusPeak}
            disabled={!peakIntensityPoint}
          >
            <LocateFixed size={14} />
            Peak Focus
          </button>

        </div>


        <div className="intensity-overview">


          <div className="intensity-summary-card">

            <div className="summary-icon wind-summary">
              <Gauge size={18} />
            </div>

            <div>

              <span>
                PEAK WMO WIND
              </span>

              <strong>

                {peakIntensityObservation
                  ? peakIntensityObservation.wind
                  : "—"}

                <small>
                  kt
                </small>

              </strong>

              <p>
                Highest recorded WMO wind
              </p>

            </div>

          </div>


          <div className="intensity-summary-card">

            <div className="summary-icon pressure-summary">
              <CircleGauge size={18} />
            </div>

            <div>

              <span>
                MINIMUM WMO PRESSURE
              </span>

              <strong>

                {minimumPressureObservation
                  ? minimumPressureObservation.pressure
                  : "—"}

                <small>
                  mb
                </small>

              </strong>

              <p>
                Lowest recorded WMO pressure
              </p>

            </div>

          </div>


          <div className="intensity-summary-card">

            <div className="summary-icon location-summary">
              <MapPinned size={18} />
            </div>

            <div>

              <span>
                PEAK OBSERVATION
              </span>

              <strong className="summary-time">

                {peakIntensityObservation
                  ? formatObservationTime(
                      peakIntensityObservation.time
                    )
                  : "—"}

              </strong>

              <p>

                {peakIntensityObservation
                  ? `${peakIntensityObservation.lat.toFixed(4)}°N · ${peakIntensityObservation.lon.toFixed(4)}°E`
                  : "Real IBTrACS position"}

              </p>

            </div>

          </div>

        </div>


        <div className="intensity-chart">

          <div className="intensity-chart-header">

            <div>

              <span>
                WIND PROGRESSION
              </span>

              <strong>
                Real WMO observations
              </strong>

            </div>

            <div className="chart-scale">

              <span>
                0
              </span>

              <span>
                {peakIntensityObservation?.wind ?? "—"} kt
              </span>

            </div>

          </div>


          <div className="intensity-bars">

            {intensityBars.map(
              (
                observation,
                index
              ) => {

                const isPeak =
                  peakIntensityObservation &&
                  observation.time ===
                    peakIntensityObservation.time;

                return (

                  <div
                    className={
                      isPeak
                        ? "intensity-bar-wrap peak-bar"
                        : "intensity-bar-wrap"
                    }

                    key={
                      `${observation.time}-${index}`
                    }
                  >

                    <div
                      className="intensity-bar"
                      style={{
                        height:
                          `${observation.height}%`,
                      }}
                    >

                      {isPeak && (

                        <div className="bar-tooltip">
                          {observation.wind} kt
                        </div>

                      )}

                    </div>

                  </div>

                );
              }
            )}

          </div>


          <div className="intensity-axis">

            <span>
              15 May
            </span>

            <span>
              17 May
            </span>

            <span>
              18 May · PEAK
            </span>

            <span>
              19 May
            </span>

            <span>
              21 May
            </span>

          </div>

        </div>


        <div className="intensity-note">

          <Gauge size={14} />

          Peak and minimum values are calculated
          directly from the WMO fields in the real
          IBTrACS observations.

        </div>

      </section>


      {/* ==================================================
          MAIN GRID
          ================================================== */}

      <section className="main-grid">


        {/* =================================================
            MAP
            ================================================= */}

        <div className="map-panel">

          <div className="map-panel-header">

            <div>

              <div className="section-kicker">
                GEOSPATIAL INTELLIGENCE
              </div>

              <h2>
                Cyclone Track, Flood Evidence & Exposure
              </h2>

              <p>
                Real Earth observation and OpenStreetMap
                infrastructure layers for the Amphan event region.
              </p>

            </div>


            <div className="map-controls">

              <button
                className={
                  showTrack
                    ? "layer-button active"
                    : "layer-button"
                }
                onClick={() => {
                  setShowTrack(
                    !showTrack
                  );
                }}
              >
                <span className="track-dot"></span>
                Track
              </button>


              <button
                className={
                  showFlood
                    ? "layer-button active"
                    : "layer-button"
                }
                onClick={() => {
                  setShowFlood(
                    !showFlood
                  );
                }}
              >
                <span className="flood-dot"></span>
                Flood
              </button>


              <button
                className={
                  showExposure
                    ? "layer-button active"
                    : "layer-button"
                }
                onClick={() => {
                  setShowExposure(
                    !showExposure
                  );
                }}
              >
                <span
                  className="track-dot"
                  style={{
                    background:
                      "#a855f7",
                  }}
                />
                Assets
              </button>


              <button
                className={showWindField ? "layer-button active wind-field-button" : "layer-button wind-field-button"}
                onClick={() => setShowWindField(!showWindField)}
                title="ERA5 gridded wind field with derived cyclone flow visualization"
              >
                <Wind size={13} />
                Meteo Wind
              </button>

              <button className={showSurge ? "layer-button active" : "layer-button"} onClick={() => setShowSurge(!showSurge)} title="Derived parametric surge potential">
                <Waves size={13} />
                Surge
              </button>

              <button className={showPathways ? "layer-button active" : "layer-button"} onClick={() => setShowPathways(!showPathways)} title="Rainfall terrain impact pathways">
                <CloudRain size={13} />
                Pathways
              </button>

              <button className={showRiskAssets ? "layer-button active" : "layer-button"} onClick={() => setShowRiskAssets(!showRiskAssets)} title="Derived asset risk watchlist">
                <ShieldCheck size={13} />
                Risk
              </button>

              <button
                className={showIsobars ? "layer-button active pressure-layer-button" : "layer-button pressure-layer-button"}
                onClick={() => setShowIsobars(!showIsobars)}
                title="ERA5 mean sea-level pressure contours"
              >
                <Activity size={13} />
                Isobars
              </button>


              <button
                className="layer-button focus-button"
                onClick={focusPeak}
              >
                <Gauge size={13} />
                Peak
              </button>


              <button
                className="layer-button focus-button"
                onClick={focusFlood}
              >
                <LocateFixed size={13} />
                Flood Focus
              </button>


              <button
                className="layer-button focus-button"
                onClick={focusExposure}
              >
                <Building2 size={13} />
                Exposure
              </button>


              <button
                className="layer-button reset-button"
                onClick={resetView}
              >
                <Crosshair size={13} />
                Reset
              </button>

            </div>

          </div>

          <div className="storm-timeline">
            <div className="timeline-head">
              <div><Timer size={13}/> STORM REPLAY · {activeStormObservation?.time ?? "—"}</div>
              <button type="button" onClick={() => setIsStormPlaying((playing) => !playing)}>{isStormPlaying ? <Pause size={13}/> : <Play size={13}/>} {isStormPlaying ? "Pause" : "Play"}</button>
            </div>
            <input
              type="range"
              min="0"
              max={Math.max(0, intensityObservations.length - 1)}
              value={Math.min(activeStormIndex, Math.max(0, intensityObservations.length - 1))}
              onChange={(event) => { setIsStormPlaying(false); setActiveStormIndex(Number(event.target.value)); }}
              disabled={intensityObservations.length < 2}
            />
            <div className="timeline-meta"><span>START</span><strong>{activeStormObservation?.wind ?? "—"} kt · {activeStormObservation?.pressure ?? "—"} mb</strong><span>OBSERVED TRACK · {intensityObservations.length || 0} points</span></div>
          </div>

          <div className="map-wrapper">

            <MapContainer
              center={[22.2, 88.2]}
              zoom={6}
              minZoom={4}
              maxZoom={12}
              scrollWheelZoom={true}
              zoomControl={true}
              zoomAnimation={false}
              markerZoomAnimation={false}
              fadeAnimation={false}
              wheelDebounceTime={120}
              wheelPxPerZoomLevel={120}
              preferCanvas={true}
              className="leaflet-map"
            >


              <TileLayer
                attribution="&copy; OpenStreetMap contributors"
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                maxZoom={19}
                updateWhenZooming={false}
                updateWhenIdle={true}
                keepBuffer={4}
              />


              {liveCyclones.map((event) => (
                <CircleMarker
                  key={`live-${event.id ?? `${event.latitude}-${event.longitude}`}`}
                  center={[event.latitude, event.longitude]}
                  radius={9}
                  pathOptions={{
                    color: event.severity === "red" ? "#ff315f" : event.severity === "orange" ? "#ff9f43" : "#35c9bf",
                    fillColor: event.severity === "red" ? "#ff315f" : event.severity === "orange" ? "#ff9f43" : "#35c9bf",
                    fillOpacity: 0.85,
                    weight: 3,
                  }}
                >
                  <Popup>
                    <div className="popup">
                      <strong>{event.name}</strong>
                      <span>Live GDACS tropical cyclone</span>
                      <span>{event.latitude.toFixed(2)}°N · {event.longitude.toFixed(2)}°E</span>
                      <span>Alert: {event.alert_level ?? event.severity}</span>
                    </div>
                  </Popup>
                </CircleMarker>
              ))}


              {showFlood &&
                floodMapAvailable && (

                  <TileLayer
                    key={floodTileUrl}
                    url={floodTileUrl}
                    opacity={0.86}
                    zIndex={20}
                    updateWhenZooming={false}
                    updateWhenIdle={true}
                    keepBuffer={4}
                    attribution="Google Earth Engine"
                  />

                )}


              {viewMode === "flood" && (

                <Rectangle
                  bounds={FLOOD_BOUNDS}
                  pathOptions={{
                    color: "#35c9bf",
                    weight: 2,
                    opacity: 0.9,
                    fill: false,
                    dashArray: "6 6",
                  }}
                >

                  <Popup>

                    <div className="popup">

                      <strong>
                        Flood analysis region
                      </strong>

                      <span>
                        87.5°E – 89.0°E
                      </span>

                      <span>
                        21.5°N – 23.0°N
                      </span>

                    </div>

                  </Popup>

                </Rectangle>

              )}


              {showTrack &&
                trackSegments.map((segment, index) => (
                  <Polyline
                    key={`track-segment-${index}`}
                    positions={segment.positions}
                    pathOptions={{
                      color: segment.color,
                      weight: 6,
                      opacity: 0.96,
                      lineCap: "round",
                      lineJoin: "round",
                    }}
                  >
                    {index === 0 && (
                      <Popup>
                        <div className="popup">
                          <strong>Cyclone Amphan</strong>
                          <span>NOAA IBTrACS · 2020</span>
                          <span>{observationCount ?? "—"} observations</span>
                          <span>Track colour follows observed WMO wind intensity.</span>
                        </div>
                      </Popup>
                    )}
                  </Polyline>
                ))}


              {showTrack && showWindField && (
                <CycloneFlowOverlay
                  field={windField}
                  observations={observations}
                  activeCenter={activeStormPoint}
                  visible={true}
                  showIsobars={showIsobars}
                />
              )}

              {showTrack && showWindField && stormCenterPoint && (
                <CycloneVortex
                  center={activeStormPoint}
                  wind={activeStormObservation?.wind}
                  pressure={activeStormObservation?.pressure}
                />
              )}


              {showTrack &&
                firstTrackPoint && (

                  <CircleMarker
                    center={
                      firstTrackPoint
                    }
                    radius={7}
                    pathOptions={{
                      color: "#ffffff",
                      fillColor: "#20d49a",
                      fillOpacity: 1,
                      weight: 2,
                    }}
                  >

                    <Popup>

                      <div className="popup">

                        <strong>
                          Track origin
                        </strong>

                        <span>
                          First recorded position
                        </span>

                      </div>

                    </Popup>

                  </CircleMarker>

                )}


              {showTrack &&
                lastTrackPoint && (

                  <CircleMarker
                    center={
                      lastTrackPoint
                    }
                    radius={8}
                    pathOptions={{
                      color: "#ffffff",
                      fillColor: "#ff315f",
                      fillOpacity: 1,
                      weight: 2,
                    }}
                  >

                    <Popup>

                      <div className="popup">

                        <strong>
                          Final recorded position
                        </strong>

                        <span>
                          NOAA IBTrACS
                        </span>

                      </div>

                    </Popup>

                  </CircleMarker>

                )}


              {/* =================================================
                  CYCLONE INTENSITY OBSERVATIONS
                  ================================================= */}

              {showTrack && intensityObservations.map((observation, index) => {
                const wind = Number(observation.wind) || 0;
                const radius = Math.max(4, Math.min(10, 4 + wind / 30));
                const fill = wind >= 120 ? "#ff315f" : wind >= 64 ? "#f59e0b" : wind >= 34 ? "#22d3ee" : "#34d399";
                return (
                  <CircleMarker
                    key={`intensity-${observation.time}-${index}`}
                    center={[observation.lat, observation.lon]}
                    radius={radius}
                    pathOptions={{ color: "#ffffff", fillColor: fill, fillOpacity: 0.85, weight: 1.5 }}
                  >
                    <Popup>
                      <div className="popup">
                        <strong>{observation.wind} kt WMO wind</strong>
                        <span>{observation.time}</span>
                        <span>Pressure: {observation.pressure ?? "—"} mb</span>
                        {observation.status && <span>Status: {observation.status}</span>}
                      </div>
                    </Popup>
                  </CircleMarker>
                );
              })}


              {/* =================================================
                  PEAK INTENSITY
                  ================================================= */}

              {peakIntensityPoint && (

                <CircleMarker
                  center={
                    peakIntensityPoint
                  }
                  radius={11}
                  pathOptions={{
                    color: "#ffffff",
                    fillColor: "#f59e0b",
                    fillOpacity: 1,
                    weight: 3,
                  }}
                >

                  <Popup>

                    <div className="popup">

                      <strong>
                        Peak WMO intensity
                      </strong>

                      <span>
                        {peakIntensityObservation?.wind}
                        {" "}kt
                      </span>

                      <span>
                        Pressure:{" "}
                        {peakIntensityObservation?.pressure ?? "—"}
                        {" "}mb
                      </span>

                      <span>
                        {peakIntensityObservation?.time}
                      </span>

                      <span>
                        {peakIntensityObservation?.lat?.toFixed(4)}
                        °N ·{" "}
                        {peakIntensityObservation?.lon?.toFixed(4)}
                        °E
                      </span>

                    </div>

                  </Popup>

                </CircleMarker>

              )}


              {/* =================================================
                  ALL CRITICAL OSM ASSETS
                  ================================================= */}

              {showExposure && allCriticalAssets.map((facility, index) => {
                const key = `${facility.osm_type}-${facility.osm_id}`;
                return (
                  <CircleMarker
                    key={`asset-${key}`}
                    center={[facility.latitude, facility.longitude]}
                    radius={3.5}
                    pathOptions={{
                      color: "#78b9d6",
                      fillColor: facility.category === "medical" ? "#58b8a9" : facility.category === "emergency" ? "#ff7a89" : facility.category === "power" ? "#e9a93b" : "#d6a2ff",
                      fillOpacity: 0.75,
                      weight: 1,
                    }}
                    eventHandlers={{
                      click: () => selectFacility({
                        ...facility,
                        latitude: Number(facility.latitude),
                        longitude: Number(facility.longitude),
                        direct_flood_candidate: false,
                        nearby_distance_meters: null,
                      }),
                    }}
                  />
                );
              })}


              {/* =================================================
                  250 M EXPOSURE ZONES
                  ================================================= */}

              {showExposure &&
                nearbyExposureFacilities.map(
                  (
                    facility,
                    index
                  ) => {

                    const isSelected =
                      selectedFacility &&
                      selectedFacility.latitude ===
                        facility.latitude &&
                      selectedFacility.longitude ===
                        facility.longitude;

                    return (

                      <Circle
                        key={`zone-${facility.name}-${facility.latitude}-${facility.longitude}`}

                        center={[
                          facility.latitude,
                          facility.longitude,
                        ]}

                        radius={
                          facility.nearby_distance_meters ??
                          EXPOSURE_RADIUS
                        }

                        pathOptions={{
                          color: isSelected
                            ? "#d9a8ff"
                            : "#a855f7",
                          weight: isSelected
                            ? 2.8
                            : 1.5,
                          opacity: isSelected
                            ? 1
                            : 0.75,
                          fillColor: "#a855f7",
                          fillOpacity: isSelected
                            ? 0.15
                            : 0.08,
                          dashArray: isSelected
                            ? "8 5"
                            : "5 5",
                        }}
                      />

                    );
                  }
                )}


              {/* =================================================
                  EXPOSURE MARKERS
                  ================================================= */}

              {showExposure &&
                nearbyExposureFacilities.map(
                  (
                    facility,
                    index
                  ) => {

                    const isSelected =
                      selectedFacility &&
                      selectedFacility.latitude ===
                        facility.latitude &&
                      selectedFacility.longitude ===
                        facility.longitude;

                    return (

                      <CircleMarker
                        key={`${facility.name}-${facility.latitude}-${facility.longitude}`}

                        center={[
                          facility.latitude,
                          facility.longitude,
                        ]}

                        radius={
                          isSelected
                            ? 12
                            : 8
                        }

                        pathOptions={{
                          color: "#ffffff",
                          fillColor: isSelected
                            ? "#d8a8ff"
                            : "#a855f7",
                          fillOpacity: 0.98,
                          weight: isSelected
                            ? 3
                            : 2,
                        }}

                        eventHandlers={{
                          click: () => {
                            selectFacility(
                              facility
                            );
                          },
                        }}
                      >

                        <Popup>

                          <div className="popup">

                            <strong>
                              {facility.name}
                            </strong>

                            <span>
                              {formatCategory(
                                facility.category
                              )}
                            </span>

                            <span>
                              Within{" "}
                              {facility.nearby_distance_meters}
                              {" "}m of flood candidate
                            </span>

                            <span>
                              Click to inspect asset
                            </span>

                          </div>

                        </Popup>

                      </CircleMarker>

                    );
                  }
                )}


              {showSurge && surgeData?.hotspots?.map((point, index) => {
                const value = Number(point.surge_potential_m) || 0;
                const color = value >= 2.5 ? "#ff315f" : value >= 1.5 ? "#ff8c42" : value >= 0.7 ? "#ffd166" : "#35c9bf";
                return (
                  <CircleMarker key={`surge-${point.lat}-${point.lon}`} center={[point.lat, point.lon]} radius={Math.max(3, Math.min(8, 3 + value * 1.5))} pathOptions={{ color, fillColor: color, fillOpacity: 0.28, weight: 1.4 }}>
                    <Popup><div className="popup"><strong>Parametric surge potential</strong><span>{value.toFixed(2)} m · {point.class}</span><span>Elevation {point.elevation_m} m</span><span>Wind proxy {point.wind_proxy_kt} kt</span></div></Popup>
                  </CircleMarker>
                );
              })}

              {showPathways && pathwaysData?.hotspots?.map((point, index) => (
                <CircleMarker key={`pathway-${point.lat}-${point.lon}`} center={[point.lat, point.lon]} radius={5} pathOptions={{ color: "#ffd166", fillColor: "#ff8c42", fillOpacity: 0.35, weight: 1.4 }}>
                  <Popup><div className="popup"><strong>{point.pathway}</strong><span>{point.rainfall_mm} mm rainfall</span><span>{point.elevation_m} m elevation · score {point.pathway_score}</span></div></Popup>
                </CircleMarker>
              ))}

              {showRiskAssets && riskAssets?.top?.map((asset, index) => {
                const color = riskColor(asset.risk_band);
                return <CircleMarker key={`risk-asset-${asset.name}-${asset.latitude}-${asset.longitude}`} center={[asset.latitude, asset.longitude]} radius={6} pathOptions={{ color: "#ffffff", fillColor: color, fillOpacity: 0.72, weight: 2 }}>
                  <Popup><div className="popup"><strong>{asset.name}</strong><span>{asset.category} · risk {asset.risk_score}</span><span>{asset.wind_proxy_kt} kt wind proxy · {asset.rainfall_mm} mm rain</span></div></Popup>
                </CircleMarker>;
              })}

              {showWindField && windField && <MapWindProbe field={windField} enabled={showWindField} />}

              <MapController
                trackCoordinates={
                  trackCoordinates
                }
                exposureCoordinates={
                  exposureCoordinates
                }
                peakIntensityPoint={
                  peakIntensityPoint
                }
                selectedFacilityPoint={
                  selectedFacilityPoint
                }
                viewMode={
                  viewMode
                }
              />

            </MapContainer>


            {/* =================================================
                MAP LEGEND
                ================================================= */}

            <div className="map-overlay">

              <div className="map-overlay-title">

                <Layers3 size={15} />

                ACTIVE LAYERS

              </div>


              <div className="map-overlay-row">

                <span className="overlay-indicator track-indicator" />

                Cyclone Track

              </div>


              <div className="map-overlay-row">

                <span className="overlay-indicator flood-indicator" />

                New-Water Candidate

              </div>


              <div className="map-overlay-row">

                <span className="overlay-indicator exposure-indicator" />

                Critical Infrastructure

              </div>


              <div className="map-overlay-row">

                <span className="overlay-indicator zone-indicator" />

                250 m Exposure Zone

              </div>


              <div className="map-overlay-row">

                <span className="overlay-indicator peak-indicator" />

                Peak Intensity

              </div>

              <div className="map-overlay-row">

                <span className="overlay-indicator wind-indicator" />

                ERA5 Wind Flow

              </div>

              <div className="map-overlay-row"><span className="overlay-indicator surge-indicator" /> Parametric Surge</div>
              <div className="map-overlay-row"><span className="overlay-indicator pathway-indicator" /> Rainfall Pathways</div>
              <div className="map-overlay-row"><span className="overlay-indicator risk-indicator" /> Asset Risk</div>

            </div>


            <div className="map-event-chip">

              <Crosshair size={14} />

              AMPHAN · BAY OF BENGAL

            </div>


            <div className="map-data-badge">

              <Wind size={14} />

              ERA5 WIND · IBTRACS · EARTH ENGINE · OSM

            </div>


            {windField && (
              <div className="meteo-snapshot-chip">
                <Wind size={11} /> <strong>METEO MODE</strong> · ERA5 snapshot · 10 m wind + MSLP
              </div>
            )}


            {windField && (
              <div className="wind-legend">
                <div className="wind-legend-head"><Wind size={12} /> WIND INTENSITY · 0–140 KT</div>
                <div className="wind-gradient"><span>LOW</span><div className="wind-gradient-bar" /><span>HIGH</span></div>
                <div className="wind-scale-labels"><span>20</span><span>35</span><span>50</span><span>65</span><span>80</span><span>100</span><span>120</span><span>140 KT</span></div>
                <div className="wind-legend-meta">ERA5 ~31 km 10 m wind + derived intensity envelope along the full IBTrACS track · Hover the map for a local ERA5 sample · {windField.timestamp ? new Date(windField.timestamp).toLocaleString([], { dateStyle: "medium", timeStyle: "short" }) : "historical snapshot"}</div>
              </div>
            )}


            <div className="map-zoom-hint">

              <Maximize2 size={13} />

              {viewMode === "flood"
                ? "Flood analysis focus"
                : viewMode === "exposure"
                ? `${allCriticalAssets.length || 0} critical assets · ${nearbyExposureCount ?? 0} within 250 m`
                : viewMode === "facility"
                ? "Selected facility"
                : viewMode === "peak"
                ? "Peak intensity location"
                : "Scroll to explore"}

            </div>


            {/* =================================================
                SELECTED FACILITY FLOATING PANEL
                ================================================= */}

            {selectedFacility && (

              <div className="selected-map-facility">

                <div className="selected-map-top">

                  <div>

                    <span>
                      SELECTED ASSET
                    </span>

                    <strong>
                      {selectedFacility.name}
                    </strong>

                  </div>


                  <button
                    onClick={
                      closeFacility
                    }
                    aria-label="Close selected facility"
                  >
                    <X size={14} />
                  </button>

                </div>


                <div className="selected-map-meta">

                  <span>
                    {formatCategory(
                      selectedFacility.category
                    )}
                  </span>

                  <span>
                    Within{" "}
                    {selectedFacility.nearby_distance_meters ??
                      EXPOSURE_RADIUS}
                    {" "}m
                  </span>

                </div>


                <button
                  className="selected-map-button"
                  onClick={() => {
                    setViewMode(
                      "facility"
                    );
                  }}
                >
                  <LocateFixed size={13} />
                  Focus asset
                </button>

              </div>

            )}

          </div>

        </div>


        {/* =================================================
            INTELLIGENCE PANEL
            ================================================= */}

        <aside className="intelligence-panel">


          {/* =================================================
              SELECTED FACILITY INTELLIGENCE
              ================================================= */}

          {selectedFacility ? (

            <div className="side-card facility-intelligence-card">

              <div className="side-card-heading">

                <div className="heading-icon selected-facility-icon">
                  <Building2 size={17} />
                </div>

                <div>

                  <span className="side-kicker">
                    ASSET INTELLIGENCE
                  </span>

                  <h3>
                    Selected Facility
                  </h3>

                </div>

              </div>


              <div className="selected-facility-name">

                {selectedFacility.name}

              </div>


              <div className="selected-facility-category">

                {formatCategory(
                  selectedFacility.category
                )}

              </div>


              <div className="facility-status-chip">

                <span className="facility-status-dot"></span>

                NEAR FLOOD CANDIDATE

              </div>


              <div className="profile-grid">

                <div>

                  <span>
                    Latitude
                  </span>

                  <strong>
                    {Number(
                      selectedFacility.latitude
                    ).toFixed(6)}°
                  </strong>

                </div>


                <div>

                  <span>
                    Longitude
                  </span>

                  <strong>
                    {Number(
                      selectedFacility.longitude
                    ).toFixed(6)}°
                  </strong>

                </div>


                <div>

                  <span>
                    Search radius
                  </span>

                  <strong>
                    {selectedFacility.nearby_distance_meters ??
                      EXPOSURE_RADIUS} m
                  </strong>

                </div>


                <div>

                  <span>
                    Direct overlap
                  </span>

                  <strong>
                    {selectedFacility.direct_flood_candidate
                      ? "YES"
                      : "NO"}
                  </strong>

                </div>

              </div>


              <div className="facility-evidence-list">

                <div>

                  <Satellite size={13} />

                  Sentinel-1 SAR candidate

                </div>


                <div>

                  <Droplets size={13} />

                  Dynamic World new-water signal

                </div>


                <div>

                  <Building2 size={13} />

                  OpenStreetMap asset location

                </div>

              </div>


              <button
                className="side-focus-button facility-locate-button"
                onClick={() => {
                  setViewMode(
                    "facility"
                  );
                }}
              >

                <LocateFixed size={13} />

                Locate on map

              </button>


              <button
                className="facility-close-button"
                onClick={
                  closeFacility
                }
              >

                <X size={13} />

                Close asset

              </button>

            </div>

          ) : (

            <div className="side-card facility-intelligence-card">

              <div className="side-card-heading">

                <div className="heading-icon selected-facility-icon">
                  <Building2 size={17} />
                </div>

                <div>

                  <span className="side-kicker">
                    ASSET INTELLIGENCE
                  </span>

                  <h3>
                    Facility Selection
                  </h3>

                </div>

              </div>


              <div className="facility-empty-state">

                <MapPinned size={16} />

                <div>

                  <strong>
                    Select an exposed asset
                  </strong>

                  <span>
                    The map shows all real OSM critical assets;
                    purple markers identify assets within 250 m
                    of the satellite-derived flood candidate.
                  </span>

                </div>

              </div>

            </div>

          )}


          {/* =================================================
              EVENT PROFILE
              ================================================= */}

          <div className="side-card event-card">

            <div className="side-card-heading">

              <div className="heading-icon">
                <MapPinned size={17} />
              </div>

              <div>

                <span className="side-kicker">
                  EVENT PROFILE
                </span>

                <h3>
                  Amphan
                </h3>

              </div>

            </div>


            <div className="profile-grid">

              <div>

                <span>
                  Season
                </span>

                <strong>
                  {season ?? "—"}
                </strong>

              </div>


              <div>

                <span>
                  Track points
                </span>

                <strong>
                  {observationCount ?? "—"}
                </strong>

              </div>


              <div>

                <span>
                  Peak WMO
                </span>

                <strong>
                  {peakIntensityObservation
                    ? `${peakIntensityObservation.wind} kt`
                    : "—"}
                </strong>

              </div>


              <div>

                <span>
                  Min pressure
                </span>

                <strong>
                  {minimumPressureObservation
                    ? `${minimumPressureObservation.pressure} mb`
                    : "—"}
                </strong>

              </div>

            </div>

          </div>


          {/* =================================================
              STORM INTENSITY
              ================================================= */}

          <div className="side-card intensity-side-card">

            <div className="side-card-heading">

              <div className="heading-icon intensity-heading-icon">
                <Gauge size={17} />
              </div>

              <div>

                <span className="side-kicker">
                  STORM INTENSITY
                </span>

                <h3>
                  Peak Observation
                </h3>

              </div>

            </div>


            <div className="intensity-side-main">

              <strong>

                {peakIntensityObservation
                  ? peakIntensityObservation.wind
                  : "—"}

                <small>
                  kt
                </small>

              </strong>

              <span>
                WMO wind
              </span>

            </div>


            <div className="intensity-side-detail">

              <div>

                <span>
                  Pressure
                </span>

                <strong>
                  {peakIntensityObservation?.pressure ?? "—"}
                  {" "}mb
                </strong>

              </div>


              <div>

                <span>
                  Position
                </span>

                <strong>
                  {peakIntensityObservation
                    ? `${peakIntensityObservation.lat.toFixed(2)}°N`
                    : "—"}
                </strong>

              </div>

            </div>


            <button
              className="side-focus-button"
              onClick={
                focusPeak
              }
            >

              <LocateFixed size={13} />

              Locate peak intensity

            </button>

          </div>


          {/* =================================================
              SATELLITE
              ================================================= */}

          <div className="side-card">

            <div className="side-card-heading">

              <div className="heading-icon">
                <Satellite size={17} />
              </div>

              <div>

                <span className="side-kicker">
                  SATELLITE EVIDENCE
                </span>

                <h3>
                  Inundation Candidate
                </h3>

              </div>

            </div>


            <div className="evidence-number">

              {floodArea !== null
                ? Number(
                    floodArea
                  ).toFixed(2)
                : "—"}

              <span>
                km²
              </span>

            </div>


            <div className="evidence-note">

              {flood?.method?.water_support ||
                "Event-aligned Sentinel-1 / Dynamic World analysis"}
              .

            </div>


            <div className="method-tag">
              CANDIDATE · NOT VERIFIED EXTENT
            </div>

          </div>


          {/* =================================================
              EXPOSURE
              ================================================= */}

          <div className="side-card">

            <div className="side-card-heading">

              <div className="heading-icon exposure-heading-icon">
                <Building2 size={17} />
              </div>

              <div>

                <span className="side-kicker">
                  INFRASTRUCTURE EXPOSURE
                </span>

                <h3>
                  Critical Assets
                </h3>

              </div>

            </div>


            <div className="evidence-number">

              {nearbyExposureCount ?? "—"}

              <span>
                nearby
              </span>

            </div>


            <div className="evidence-note">

              Real OpenStreetMap critical infrastructure
              located within {exposureDistance ?? "—"} m
              of satellite-derived flood candidates.

            </div>


            <div className="profile-grid">

              <div>

                <span>
                  Critical assets
                </span>

                <strong>
                  {criticalInfrastructureCount ?? "—"}
                </strong>

              </div>


              <div>

                <span>
                  Candidate exposure
                </span>

                <strong>
                  {nearbyExposurePercentage !== null
                    ? `${Number(
                        nearbyExposurePercentage
                      ).toFixed(2)}%`
                    : "—"}
                </strong>

              </div>


              <div>

                <span>
                  Direct
                </span>

                <strong>
                  {directExposureCount ?? "—"}
                </strong>

              </div>


              <div>

                <span>
                  Search radius
                </span>

                <strong>
                  {exposureDistance !== null
                    ? `${exposureDistance} m`
                    : "—"}
                </strong>

              </div>

            </div>


            <div className="evidence-note">
              Category counts
            </div>


            <div className="source-list">

              <div className="source-row">
                <span className="source-status">✓</span>

                <div>
                  <strong>Medical</strong>

                  <span>
                    {medicalNearby} nearby candidate
                  </span>
                </div>
              </div>


              <div className="source-row">
                <span className="source-status">✓</span>

                <div>
                  <strong>Emergency</strong>

                  <span>
                    {emergencyNearby} nearby candidate
                  </span>
                </div>
              </div>


              <div className="source-row">
                <span className="source-status">✓</span>

                <div>
                  <strong>Power</strong>

                  <span>
                    {powerNearby} nearby candidate
                  </span>
                </div>
              </div>


              <div className="source-row">
                <span className="source-status">✓</span>

                <div>
                  <strong>Shelter</strong>

                  <span>
                    {shelterNearby} nearby candidate
                  </span>
                </div>
              </div>

            </div>


            <div className="method-tag">
              CANDIDATE EXPOSURE · REAL OSM LOCATIONS
            </div>

          </div>


          {/* =================================================
              TERRAIN
              ================================================= */}

          <div className="side-card">

            <div className="side-card-heading">

              <div className="heading-icon">
                <Mountain size={17} />
              </div>

              <div>

                <span className="side-kicker">
                  TERRAIN
                </span>

                <h3>
                  Elevation Profile
                </h3>

              </div>

            </div>


            <div className="terrain-bars">

              <div className="terrain-row">

                <div className="terrain-label">

                  <span>
                    Minimum
                  </span>

                  <strong>

                    {minElevation !== null
                      ? `${minElevation} m`
                      : "—"}

                  </strong>

                </div>

                <div className="terrain-track">
                  <div className="terrain-fill low"></div>
                </div>

              </div>


              <div className="terrain-row">

                <div className="terrain-label">

                  <span>
                    Mean
                  </span>

                  <strong>

                    {meanElevation !== null
                      ? `${Number(
                          meanElevation
                        ).toFixed(2)} m`
                      : "—"}

                  </strong>

                </div>

                <div className="terrain-track">
                  <div className="terrain-fill mean"></div>
                </div>

              </div>


              <div className="terrain-row">

                <div className="terrain-label">

                  <span>
                    Maximum
                  </span>

                  <strong>

                    {maxElevation !== null
                      ? `${maxElevation} m`
                      : "—"}

                  </strong>

                </div>

                <div className="terrain-track">
                  <div className="terrain-fill high"></div>
                </div>

              </div>

            </div>

          </div>


          {/* =================================================
              RAINFALL
              ================================================= */}

          <div className="side-card">

            <div className="side-card-heading">

              <div className="heading-icon">
                <CloudRain size={17} />
              </div>

              <div>

                <span className="side-kicker">
                  RAINFALL
                </span>

                <h3>
                  CHIRPS Observation Range
                </h3>

              </div>

            </div>


            <div className="profile-grid">

              <div>

                <span>Mean</span>

                <strong>
                  {rainfallMean !== null
                    ? `${Number(
                        rainfallMean
                      ).toFixed(2)} mm`
                    : "—"}
                </strong>

              </div>


              <div>

                <span>Minimum</span>

                <strong>
                  {rainfallMin !== null
                    ? `${Number(
                        rainfallMin
                      ).toFixed(2)} mm`
                    : "—"}
                </strong>

              </div>


              <div>

                <span>Maximum</span>

                <strong>
                  {rainfallMax !== null
                    ? `${Number(
                        rainfallMax
                      ).toFixed(2)} mm`
                    : "—"}
                </strong>

              </div>


              <div>

                <span>Images</span>

                <strong>
                  {rainfallDays ?? "—"}
                </strong>

              </div>

            </div>

          </div>


          {/* =================================================
              EXPOSURE LOCATIONS
              ================================================= */}

          <div className="side-card">

            <div className="side-card-heading">

              <div className="heading-icon">
                <MapPinned size={17} />
              </div>

              <div>

                <span className="side-kicker">
                  EXPOSURE LOCATIONS
                </span>

                <h3>
                  Nearby Critical Assets
                </h3>

              </div>

            </div>


            <div className="source-list">

              {nearbyExposureFacilities.length === 0 ? (

                <div className="evidence-note">

                  No critical infrastructure was identified
                  within 250 m of the flood candidate.

                </div>

              ) : (

                nearbyExposureFacilities
                  .slice(0, 5)
                  .map(
                    (
                      facility,
                      index
                    ) => {

                      const isSelected =
                        selectedFacility &&
                        selectedFacility.latitude ===
                          facility.latitude &&
                        selectedFacility.longitude ===
                          facility.longitude;

                      return (

                        <button
                          type="button"
                          className={
                            isSelected
                              ? "facility-row selected"
                              : "facility-row"
                          }

                          key={
                            `${facility.name}-${facility.latitude}-${facility.longitude}-${index}`
                          }

                          onClick={() => {
                            selectFacility(
                              facility
                            );
                          }}
                        >

                          <span className="source-status">
                            {index + 1}
                          </span>

                          <div>

                            <strong>
                              {facility.name}
                            </strong>

                            <span>
                              {formatCategory(
                                facility.category
                              )}
                              {" · "}
                              {Number(
                                facility.latitude
                              ).toFixed(4)},
                              {" "}
                              {Number(
                                facility.longitude
                              ).toFixed(4)}
                            </span>

                          </div>

                        </button>

                      );
                    }
                  )

              )}

            </div>

          </div>


          {/* =================================================
              SOURCES
              ================================================= */}

          <div className="side-card sources-card">

            <div className="side-card-heading">

              <div className="heading-icon">
                <Database size={17} />
              </div>

              <div>

                <span className="side-kicker">
                  DATA LINEAGE
                </span>

                <h3>
                  Real Sources
                </h3>

              </div>

            </div>


            <div className="source-list">

              <div className="source-row">
                <span className="source-status">✓</span>

                <div>
                  <strong>NOAA IBTrACS</strong>
                  <span>
                    Cyclone track & intensity
                  </span>
                </div>
              </div>


              <div className="source-row">
                <span className="source-status">✓</span>

                <div>
                  <strong>Sentinel-1</strong>
                  <span>
                    SAR change detection
                  </span>
                </div>
              </div>


              <div className="source-row">
                <span className="source-status">✓</span>

                <div>
                  <strong>Dynamic World</strong>
                  <span>
                    Water probability
                  </span>
                </div>
              </div>


              <div className="source-row">
                <span className="source-status">✓</span>

                <div>
                  <strong>CHIRPS Daily</strong>
                  <span>
                    Rainfall observations
                  </span>
                </div>
              </div>


              <div className="source-row">
                <span className="source-status">✓</span>

                <div>
                  <strong>NASADEM</strong>
                  <span>
                    Elevation data
                  </span>
                </div>
              </div>


              <div className="source-row">
                <span className="source-status">✓</span>

                <div>
                  <strong>OpenStreetMap</strong>
                  <span>
                    Critical infrastructure
                  </span>
                </div>
              </div>

              <div className="source-row">
                <span className="source-status">AI</span>
                <div>
                  <strong>Gemini multimodal reasoning</strong>
                  <span>
                    Evidence interpretation + briefing (API key optional)
                  </span>
                </div>
              </div>

            </div>

          </div>

        </aside>

      </section>


      <MissionControl
        ready={!loading && Boolean(cyclone)}
        cyclone={cyclone}
        flood={flood}
        terrain={terrain}
        rainfall={rainfall}
        exposure={exposure}
        surgeData={surgeData}
        pathwaysData={pathwaysData}
        riskAssets={riskAssets}
        riskSummary={riskSummary}
        advisories={advisories}
        onSurgeData={setSurgeData}
        onPathwaysData={setPathwaysData}
        onRiskAssets={setRiskAssets}
        onRiskSummary={setRiskSummary}
        onAdvisories={setAdvisories}
      />


      {/* ====================================================
          METHODOLOGY
          ==================================================== */}

      <section className="analysis-strip">

        <div className="analysis-title">

          <ShieldCheck size={18} />

          <div>

            <span>
              ANALYSIS METHODOLOGY
            </span>

            <strong>
              Real observations → geospatial processing
            </strong>

          </div>

        </div>


        <div className="analysis-items">

          <div>
            <Satellite size={15} />
            SAR change
          </div>

          <div>
            <Droplets size={15} />
            New-water detection
          </div>

          <div>
            <Mountain size={15} />
            Terrain context
          </div>

          <div>
            <CloudRain size={15} />
            Rainfall context
          </div>

          <div>
            <Gauge size={15} />
            Intensity profile
          </div>

          <div>
            <Building2 size={15} />
            OSM exposure
          </div>

        </div>

      </section>


      {/* ====================================================
          FOOTER
          ==================================================== */}

      <footer className="footer">

        <div>
          CycloneShield AI
        </div>

        <div>
          REAL DATA PIPELINE · GOOGLE EARTH ENGINE + OPENSTREETMAP
        </div>

      </footer>

    </div>
  );
}


export default App;