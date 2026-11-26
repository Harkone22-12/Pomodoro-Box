const test = require("node:test");
const assert = require("node:assert/strict");

const {
  validateDht,
  formatChart24h,
  analyzeOptimal,
} = require("./minh_logic");

test("validateDht accepts valid temp/hum and attaches timestamp", () => {
  const res = validateDht({ temp: 27.5, hum: 64.0 }, "2026-11-26T15:00:00Z");
  assert.deepEqual(res, {
    temp: 27.5,
    hum: 64.0,
    ts: "2026-11-26T15:00:00Z",
  });
});

test("validateDht rejects out-of-range or non-numeric readings", () => {
  assert.equal(validateDht({ temp: 99, hum: 50 }), null);
  assert.equal(validateDht({ temp: 25, hum: 120 }), null);
  assert.equal(validateDht({ temp: "25", hum: 50 }), null);
  assert.equal(validateDht(null), null);
});

test("formatChart24h computes summary stats and Dashboard 2.0 chart series", () => {
  const rows = [
    { created_at: "2026-11-26T08:00:00Z", temp: 25.0, hum: 60.0 },
    { created_at: "2026-11-26T09:00:00Z", temp: 27.0, hum: 70.0 },
  ];
  const out = formatChart24h(rows);
  assert.deepEqual(out.summary, {
    avgTemp: 26.0,
    minTemp: 25.0,
    maxTemp: 27.0,
    avgHum: 65.0,
    count: 2,
  });
  assert.equal(out.series.length, 4);
  assert.equal(out.series[0].series, "Nhiệt độ (°C)");
  assert.equal(out.series[2].series, "Độ ẩm (%)");
});

test("analyzeOptimal handles cold-start when fewer than 5 sessions exist", () => {
  const res = analyzeOptimal([
    { started_at: "2026-11-26T08:00:00Z", duration_min: 25, target_min: 25, rating: 5, avg_temp: 26, avg_hum: 60 },
  ]);
  assert.equal(res.coldStart, true);
  assert.equal(res.sampleCount, 1);
  assert.equal(res.optimal, null);
  assert.match(res.recommendation, /24.*27/);
});

test("analyzeOptimal finds best temp/hum bin and golden hour when >= 5 sessions", () => {
  const sessions = [
    { started_at: "2026-11-26T08:30:00Z", duration_min: 25, target_min: 25, rating: 5, avg_temp: 25.2, avg_hum: 58 },
    { started_at: "2026-11-25T09:00:00Z", duration_min: 25, target_min: 25, rating: 5, avg_temp: 24.8, avg_hum: 55 },
    { started_at: "2026-11-24T08:15:00Z", duration_min: 25, target_min: 25, rating: 4, avg_temp: 25.5, avg_hum: 62 },
    { started_at: "2026-11-23T14:00:00Z", duration_min: 15, target_min: 25, rating: 2, avg_temp: 32.0, avg_hum: 82 },
    { started_at: "2026-11-22T14:30:00Z", duration_min: 10, target_min: 25, rating: 2, avg_temp: 33.0, avg_hum: 85 },
  ];
  const res = analyzeOptimal(sessions);
  assert.equal(res.coldStart, false);
  assert.equal(res.sampleCount, 5);
  assert.deepEqual(res.optimal.tempRange, [24, 26]);
  assert.deepEqual(res.optimal.humRange, [50, 60]);
  assert.equal(res.optimal.bestHour, "08:00-10:00");
});
