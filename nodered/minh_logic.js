// Pure JS logic for Minh's Node-RED function nodes (YCCB, YC5, YC11).
// Tested with `node --test nodered/minh_logic.test.js`.

/** Validate DHT22 MQTT payload and attach an ISO timestamp. */
function validateDht(payload, ts = new Date().toISOString()) {
  if (!payload || typeof payload !== "object") return null;
  const { temp, hum } = payload;
  if (typeof temp !== "number" || typeof hum !== "number") return null;
  if (!Number.isFinite(temp) || !Number.isFinite(hum)) return null;
  if (temp < -40 || temp > 80 || hum < 0 || hum > 100) return null;
  return { temp, hum, ts };
}

function round1(val) {
  return Math.round(val * 10) / 10;
}

/** Format Supabase sensor_data rows into summary stats and Dashboard 2.0 chart points. */
function formatChart24h(rows) {
  if (!Array.isArray(rows) || rows.length === 0) {
    return {
      summary: { avgTemp: 0, minTemp: 0, maxTemp: 0, avgHum: 0, count: 0 },
      series: [],
    };
  }

  let sumTemp = 0;
  let sumHum = 0;
  let minTemp = Infinity;
  let maxTemp = -Infinity;
  const series = [];

  for (const r of rows) {
    sumTemp += r.temp;
    sumHum += r.hum;
    if (r.temp < minTemp) minTemp = r.temp;
    if (r.temp > maxTemp) maxTemp = r.temp;
    series.push({ series: "Nhiệt độ (°C)", x: r.created_at, y: r.temp });
    series.push({ series: "Độ ẩm (%)", x: r.created_at, y: r.hum });
  }

  // Group by series name so temperature points precede humidity points.
  const tempPoints = series.filter((p) => p.series === "Nhiệt độ (°C)");
  const humPoints = series.filter((p) => p.series === "Độ ẩm (%)");

  return {
    summary: {
      avgTemp: round1(sumTemp / rows.length),
      minTemp: round1(minTemp),
      maxTemp: round1(maxTemp),
      avgHum: round1(sumHum / rows.length),
      count: rows.length,
    },
    series: [...tempPoints, ...humPoints],
  };
}

function bestBin(map) {
  let bestKey = null;
  let bestAvg = -1;
  for (const [key, entry] of map.entries()) {
    const avg = entry.sum / entry.count;
    if (avg > bestAvg) {
      bestAvg = avg;
      bestKey = key;
    }
  }
  return bestKey;
}

/** Analyze study_sessions to find optimal temp/hum/hour (YC11) with cold-start fallback. */
function analyzeOptimal(sessions) {
  const valid = Array.isArray(sessions)
    ? sessions.filter(
        (s) =>
          typeof s.duration_min === "number" &&
          typeof s.rating === "number" &&
          typeof s.avg_temp === "number" &&
          typeof s.avg_hum === "number" &&
          s.started_at
      )
    : [];

  if (valid.length < 5) {
    return {
      coldStart: true,
      sampleCount: valid.length,
      optimal: null,
      recommendation:
        "Chưa đủ dữ liệu phiên học (cần tối thiểu 5 phiên). Khuyến nghị mặc định: 24–27°C, độ ẩm 50–65%.",
    };
  }

  const tempBins = new Map();
  const humBins = new Map();
  const hourBins = new Map();

  for (const s of valid) {
    const target = s.target_min > 0 ? s.target_min : 25;
    const completion = Math.min(1, s.duration_min / target);
    const q = 0.5 * completion + 0.5 * (s.rating / 5);

    const tLow = Math.floor(s.avg_temp / 2) * 2;
    const hLow = Math.floor(s.avg_hum / 10) * 10;
    const hrLow = Math.floor(new Date(s.started_at).getUTCHours() / 2) * 2;

    const add = (map, key) => {
      const cur = map.get(key) || { sum: 0, count: 0 };
      cur.sum += q;
      cur.count += 1;
      map.set(key, cur);
    };

    add(tempBins, `${tLow}-${tLow + 2}`);
    add(humBins, `${hLow}-${hLow + 10}`);
    const pad = (n) => String(n).padStart(2, "0");
    add(hourBins, `${pad(hrLow)}:00-${pad(hrLow + 2)}:00`);
  }

  const tempRange = bestBin(tempBins).split("-").map(Number);
  const humRange = bestBin(humBins).split("-").map(Number);
  const bestHour = bestBin(hourBins);

  return {
    coldStart: false,
    sampleCount: valid.length,
    optimal: { tempRange, humRange, bestHour },
    recommendation: `Điều kiện tối ưu của bạn: ${tempRange[0]}–${tempRange[1]}°C, độ ẩm ${humRange[0]}–${humRange[1]}%, khung giờ vàng ${bestHour}.`,
  };
}

module.exports = { validateDht, formatChart24h, analyzeOptimal };
