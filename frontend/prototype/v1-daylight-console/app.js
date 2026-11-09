/* Study Station: UI prototype behaviour.
   All data here is simulated in the browser. Nothing is sent over MQTT;
   the toasts only show which topic and payload (docs/topics.md) the real
   app would publish. */
(() => {
  'use strict';

  // ---------- helpers ----------
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const pad = (n) => String(n).padStart(2, '0');
  const hm = (d) => `${pad(d.getHours())}:${pad(d.getMinutes())}`;
  const hms = (d) => `${hm(d)}:${pad(d.getSeconds())}`;
  const mmss = (s) => `${pad(Math.floor(s / 60))}:${pad(s % 60)}`;
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const bind = (key, val) => $$(`[data-bind="${key}"]`).forEach((el) => { el.textContent = val; });
  const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const dayLabel = (d) => `${DAYS[d.getDay()]} ${pad(d.getDate())}`;
  const isDesktop = () => matchMedia('(min-width: 1181px)').matches;

  // deterministic noise so screenshots are stable
  let seed = 7;
  const rnd = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };

  function toast(html, opts = {}) {
    const t = document.createElement('div');
    t.className = 'toast';
    t.innerHTML = `<svg class="ic" aria-hidden="true"><use href="#${opts.icon || 'i-check'}"/></svg><div>${html}</div>`;
    if (opts.action) {
      const b = document.createElement('button');
      b.className = 'btn btn-sm btn-primary';
      b.textContent = opts.action.label;
      b.addEventListener('click', () => { opts.action.fn(); close(); });
      t.append(b);
    }
    $('.toasts').append(t);
    const close = () => {
      if (!t.isConnected) return;
      t.classList.add('out');
      setTimeout(() => t.remove(), 200);
    };
    setTimeout(close, opts.ms || 4200);
  }
  const mqtt = (topic, payload, dir = '←') =>
    `<code>${esc(topic)} ${dir} ${esc(JSON.stringify(payload))}</code>`;

  // ---------- shared state ----------
  const now0 = Date.now();
  const settings = { focus: 25, short: 5, long: 15, every: 4, remind: 50, lightThreshold: 1200 };
  let lastMsg = now0 - 2000;

  // ---------- routing ----------
  const SCREENS = ['signin', 'register', 'workspace', 'history', 'settings'];
  const MTABS = ['timer', 'lcd', 'room', 'log'];
  const TITLES = { timer: 'Timer', lcd: 'LCD', room: 'Room', log: 'Log', history: 'History', settings: 'Settings', signin: 'Sign in', register: 'Create account' };

  function route() {
    const parts = (location.hash || '#/signin').replace(/^#\/?/, '').split('/');
    const screen = SCREENS.includes(parts[0]) ? parts[0] : 'signin';
    const body = document.body;
    body.dataset.screen = screen;
    if (screen === 'workspace' && MTABS.includes(parts[1])) body.dataset.mtab = parts[1];

    const isAuth = screen === 'signin' || screen === 'register';
    $('.app').hidden = isAuth;
    $$('[data-screen-id]').forEach((el) => { el.hidden = el.dataset.screenId !== screen; });

    $$('[data-nav]').forEach((a) => {
      if (a.dataset.nav === screen) a.setAttribute('aria-current', 'page');
      else a.removeAttribute('aria-current');
    });

    const tabKey = screen === 'workspace' ? body.dataset.mtab : screen === 'history' ? 'log' : screen;
    $$('[data-tabnav]').forEach((a) => {
      if (a.dataset.tabnav === tabKey) a.setAttribute('aria-current', 'page');
      else a.removeAttribute('aria-current');
    });

    const title = screen === 'workspace' ? TITLES[body.dataset.mtab] : TITLES[screen];
    $('.mobile-title').textContent = title;
    document.title = `${screen === 'workspace' ? 'Workspace' : title} · Study Station`;

    if (screen === 'workspace') requestAnimationFrame(() => { if (!userMoved) arrange(); });
    if (screen === 'history') drawHistory();
    window.scrollTo(0, 0);
  }
  window.addEventListener('hashchange', route);

  // ---------- forms: auth ----------
  const emailOk = (v) => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v.trim());
  function setErr(input, msg) {
    const id = input.getAttribute('aria-describedby');
    const el = id && document.getElementById(id);
    if (msg) input.setAttribute('aria-invalid', 'true'); else input.removeAttribute('aria-invalid');
    if (el) el.textContent = msg || '';
    return !msg;
  }
  const rules = {
    email: (v) => (!v.trim() ? 'Enter your email.' : !emailOk(v) ? 'This email looks incomplete, e.g. you@student.edu.vn.' : ''),
    password: (v) => (v.length < 8 ? `Use at least 8 characters (${v.length}/8).` : ''),
    name: (v) => (!v.trim() ? 'Enter your name.' : ''),
  };

  function wireAuth(form, check, done) {
    $$('input', form).forEach((inp) => inp.addEventListener('blur', () => { if (inp.value || inp.getAttribute('aria-invalid')) check(inp); }));
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const bad = $$('input[aria-describedby]', form).filter((inp) => !check(inp));
      if (bad.length) { bad[0].focus(); return; }
      const btn = $('button[type="submit"]', form);
      btn.classList.add('is-loading');
      btn.disabled = true;
      setTimeout(() => {
        btn.classList.remove('is-loading');
        btn.disabled = false;
        done();
      }, 700);
    });
  }

  const signin = $('#form-signin');
  wireAuth(signin, (inp) => setErr(inp, inp.name === 'email' ? rules.email(inp.value) : rules.password(inp.value)), () => {
    location.hash = '#/workspace';
    toast('Signed in. The box is online.');
  });

  const register = $('#form-register');
  wireAuth(register, (inp) => {
    if (inp.name === 'password2') return setErr(inp, inp.value !== $('#rg-pass').value ? 'Passwords do not match.' : '');
    return setErr(inp, rules[inp.name](inp.value));
  }, () => {
    location.hash = '#/workspace';
    toast('Account created. Welcome to Study Station.');
  });

  document.addEventListener('click', (e) => {
    const a = e.target.closest('[data-action="forgot"], [data-action="change-pass"]');
    if (!a) return;
    e.preventDefault();
    toast('Prototype: the real app would email you a reset link.', { icon: 'i-alert' });
  });

  // ---------- clock + MQTT age ----------
  function tickClock() {
    bind('clock', hm(new Date()));
    const age = Math.max(0, Math.round((Date.now() - lastMsg) / 1000));
    bind('mqttAge', `${age} s`);
  }

  // ---------- DHT22 ----------
  const dht = { temp: 29.5, hum: 70, t: [], h: [] };
  for (let i = 0; i < 30; i++) {
    const k = i / 29;
    dht.t.push(28.4 + 1.1 * k + (rnd() - 0.5) * 0.25);
    dht.h.push(73.5 - 3.5 * k + (rnd() - 0.5) * 0.8);
  }
  dht.t[29] = dht.temp; dht.h[29] = dht.hum;

  function drawSpark() {
    const toPts = (arr, lo, hi) => arr.map((v, i) => `${(i / (arr.length - 1)) * 300},${(52 - ((v - lo) / (hi - lo)) * 44).toFixed(1)}`).join(' ');
    $('.spark-temp').setAttribute('points', toPts(dht.t, 27.8, 30.4));
    $('.spark-hum').setAttribute('points', toPts(dht.h, 63, 78));
  }
  function renderDht() {
    bind('temp', dht.temp.toFixed(1));
    bind('hum', Math.round(dht.hum));
    bind('comfort', dht.temp >= 31 ? 'too hot' : dht.temp >= 29 ? 'warm' : dht.temp < 20 ? 'cool' : 'comfortable');
    drawSpark();
  }
  function stepDht() {
    dht.temp = clamp(dht.temp + (Math.random() - 0.5) * 0.2, 27, 31.5);
    dht.hum = clamp(dht.hum + (Math.random() - 0.5) * 0.8, 60, 78);
    dht.t.push(dht.temp); dht.t.shift();
    dht.h.push(dht.hum); dht.h.shift();
    lastMsg = Date.now();
    renderDht();
  }

  // ---------- LDR ----------
  const light = { raw: 2100 };
  const seg = $('.segbar');
  seg.innerHTML = '<i></i>'.repeat(20);
  function renderLight() {
    const enough = light.raw >= settings.lightThreshold;
    bind('raw', light.raw);
    const badge = $('[data-bind="lightLabel"]');
    badge.textContent = enough ? 'Enough light' : 'Too dim';
    badge.className = `badge ${enough ? 'badge-ok' : 'badge-warn'}`;
    const on = Math.round((light.raw / 4095) * 20);
    $$('i', seg).forEach((el, i) => el.classList.toggle('on', i < on));
    seg.classList.toggle('dim', !enough);
  }
  function stepLight() {
    light.raw = Math.round(clamp(light.raw + (Math.random() - 0.5) * 120, 1700, 2500));
    lastMsg = Date.now();
    renderLight();
  }

  // ---------- RFID session ----------
  const sess = { active: true, uid: 'A1B2C3D4', start: now0 - (56 * 60 + 18) * 1000 };
  function renderSession() {
    const badge = $('[data-bind="sessionBadge"]');
    const alert = $('[data-bind="breakAlert"]');
    if (!sess.active) {
      bind('sessionElapsed', '0:00:00');
      bind('uid', '—');
      bind('sessionStart', '—');
      badge.textContent = 'Idle';
      badge.className = 'badge badge-off';
      alert.hidden = true;
      bind('tapLabel', 'Simulate card tap (start)');
      return;
    }
    const s = Math.floor((Date.now() - sess.start) / 1000);
    bind('sessionElapsed', `${Math.floor(s / 3600)}:${pad(Math.floor(s / 60) % 60)}:${pad(s % 60)}`);
    bind('uid', sess.uid);
    bind('sessionStart', hms(new Date(sess.start)));
    badge.textContent = 'Active';
    badge.className = 'badge badge-ok';
    const over = s >= settings.remind * 60;
    alert.hidden = !over;
    bind('breakMin', settings.remind);
    bind('breakAt', hm(new Date(sess.start + settings.remind * 60000)));
    bind('tapLabel', 'Simulate card tap (stop)');
  }
  $('[data-action="tap"]').addEventListener('click', () => {
    sess.active = !sess.active;
    const action = sess.active ? 'start' : 'stop';
    if (sess.active) sess.start = Date.now();
    else {
      const first = sessions[0];
      first.end = hm(new Date());
    }
    renderSession();
    renderLogList();
    toast(`Card ${action === 'start' ? 'tapped, session started' : 'tapped, session stopped'} ${mqtt('study/rfid', { uid: 'A1B2C3D4', action }, '→')}`, { icon: 'i-card' });
  });

  // ---------- Timer (study/timer) ----------
  const T = {
    preset: 'focus',
    mode: 'Focus',
    total: settings.focus * 60,
    endAt: now0 + (18 * 60 + 42) * 1000,
    left: 0,
    running: true,
    round: 3,
    advance: false,
    today: 2,
    week: 26,
  };
  const timerLeft = () => (T.running ? Math.max(0, Math.ceil((T.endAt - Date.now()) / 1000)) : T.left);
  const presetMinutes = (p) => (p === 'custom' ? Number($('#custom-min').value) : settings[p]);
  const MODE = { focus: 'Focus', short: 'Short break', long: 'Long break', custom: 'Custom' };

  function renderRounds() {
    const el = $('.rounds');
    el.innerHTML = Array.from({ length: settings.every }, (_, i) => {
      const done = i < T.round - 1 || (i === T.round - 1 && T.advance);
      const cur = i === T.round - 1 && !T.advance;
      return `<i class="${done ? 'done' : cur ? 'now' : ''}"></i>`;
    }).join('');
    el.setAttribute('aria-label', `Round ${T.round} of ${settings.every}`);
  }
  function renderTimer() {
    const left = timerLeft();
    if (T.running && left === 0) finishRound();
    const l = timerLeft();
    bind('countdown', l >= 3600 ? `${Math.floor(l / 3600)}:${pad(Math.floor(l / 60) % 60)}:${pad(l % 60)}` : mmss(l));
    bind('timerMode', T.running ? T.mode : T.left === 0 && T.advance ? `${T.mode} done` : T.left === T.total ? 'Ready' : 'Stopped');
    const isFocus = T.mode === 'Focus' || T.mode === 'Custom';
    bind('countdownSub', `left of ${mmss(T.total)} · ${isFocus ? `round ${T.round} of ${settings.every}` : T.mode.toLowerCase()}`);
    const pct = T.total ? Math.round(((T.total - l) / T.total) * 100) : 0;
    $('.progress span').style.width = `${pct}%`;
    $('.progress').setAttribute('aria-valuenow', pct);
    $('.timer-card').classList.toggle('is-paused', !T.running);
    $('[data-action="timer-stop"]').disabled = !T.running;
    bind('today', T.today);
    bind('week', T.week);
  }
  function finishRound() {
    T.running = false;
    T.left = 0;
    const wasFocus = T.mode === 'Focus' || T.mode === 'Custom';
    if (wasFocus) {
      T.today += 1; T.week += 1; T.advance = true;
      const next = T.round % settings.every === 0 ? 'long' : 'short';
      $(`input[name="preset"][value="${next}"]`).checked = true;
      T.preset = next;
    } else {
      $('input[name="preset"][value="focus"]').checked = true;
      T.preset = 'focus';
    }
    renderRounds();
    toast("Time's up. The box buzzes 3 times (GPIO25 LOW).", { icon: 'i-timer', ms: 6000 });
  }
  function checkCustom() {
    const inp = $('#custom-min');
    const v = Number(inp.value);
    const ok = Number.isInteger(v) && v >= 1 && v <= 120;
    return setErr(inp, ok ? '' : 'Enter a whole number from 1 to 120.');
  }
  $('#custom-min').addEventListener('input', () => {
    $('#preset-custom').checked = true;
    T.preset = 'custom';
    checkCustom();
    if (!T.running && checkCustom()) previewPreset();
  });
  function previewPreset() {
    T.total = presetMinutes(T.preset) * 60;
    T.left = T.total;
    T.mode = MODE[T.preset];
    renderTimer();
  }
  $$('input[name="preset"]').forEach((r) => r.addEventListener('change', () => {
    T.preset = r.value;
    if (r.value !== 'custom') setErr($('#custom-min'), '');
    if (!T.running) previewPreset();
  }));
  $('[data-action="timer-send"]').addEventListener('click', () => {
    if (T.preset === 'custom' && !checkCustom()) { $('#custom-min').focus(); return; }
    const minutes = presetMinutes(T.preset);
    T.mode = MODE[T.preset];
    if ((T.preset === 'focus' || T.preset === 'custom') && T.advance) {
      T.round = (T.round % settings.every) + 1;
      T.advance = false;
    }
    T.total = minutes * 60;
    T.endAt = Date.now() + T.total * 1000;
    T.running = true;
    renderRounds();
    renderTimer();
    toast(`Sent to box ${mqtt('study/timer', { minutes })}`, { icon: 'i-timer' });
  });
  $('[data-action="timer-stop"]').addEventListener('click', () => {
    T.left = timerLeft();
    T.running = false;
    renderTimer();
    toast('Countdown stopped on the page. There is no stop command in docs/topics.md yet, so the box keeps counting.', { icon: 'i-alert', ms: 6500 });
  });

  // ---------- LCD (study/lcd) ----------
  const lcdInput = $('#lcd-text');
  const toLcd = (s) => s.normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/đ/g, 'd').replace(/Đ/g, 'D').replace(/[^\x20-\x7E]/g, '?');
  function wrap16(t) {
    if (t.length <= 16) return [t, ''];
    const i = t.lastIndexOf(' ', 16);
    if (i > 0 && t.length - i - 1 <= 16) return [t.slice(0, i), t.slice(i + 1)];
    return [t.slice(0, 16), t.slice(16, 32)];
  }
  function renderLcd() {
    const raw = lcdInput.value;
    const conv = toLcd(raw).slice(0, 32);
    if (conv !== raw) {
      const pos = lcdInput.selectionStart;
      lcdInput.value = conv;
      try { lcdInput.setSelectionRange(pos, pos); } catch (_) { /* ignore */ }
      bind('lcdHint', 'Accents removed: the LCD1602 has no Vietnamese characters.');
    } else if (!conv.trim()) {
      bind('lcdHint', 'Type a message to show on the box.');
    } else {
      bind('lcdHint', 'Text wraps at 16 characters per line.');
    }
    bind('lcdCount', `${conv.length}/32`);
    const lines = wrap16(conv);
    $$('.lcd-row').forEach((row, r) => {
      const s = lines[r].padEnd(16, ' ');
      row.innerHTML = [...s].map((c) => `<span>${c === ' ' ? '&nbsp;' : esc(c)}</span>`).join('');
    });
    $('.lcd').setAttribute('aria-label', `LCD preview: ${lines.filter(Boolean).join(' / ') || 'empty'}`);
  }
  lcdInput.addEventListener('input', renderLcd);
  $('#form-lcd').addEventListener('submit', (e) => {
    e.preventDefault();
    const text = lcdInput.value.trim();
    if (!text) { bind('lcdHint', 'Type a message first.'); lcdInput.focus(); return; }
    toast(`Sent to LCD ${mqtt('study/lcd', { text })}`, { icon: 'i-lcd' });
  });
  $$('[data-quick]').forEach((b) => b.addEventListener('click', () => {
    lcdInput.value = b.dataset.quick;
    renderLcd();
    lcdInput.focus();
  }));

  // ---------- sessions (log + history) ----------
  const today = new Date();
  const daysAgo = (n) => { const d = new Date(today); d.setDate(d.getDate() - n); return d; };
  const sessions = [
    { d: daysAgo(0), start: hm(new Date(sess.start)), end: 'now', rounds: '2+1', card: 'A1B2C3D4', t: '29.5', light: 'enough' },
    { d: daysAgo(1), start: '09:10', end: '09:40', rounds: '1', card: 'A1B2C3D4', t: '28.1', light: 'enough' },
    { d: daysAgo(2), start: '20:00', end: '21:00', rounds: '2', card: 'A1B2C3D4', t: '27.4', light: 'dim' },
    { d: daysAgo(3), start: '18:30', end: '22:10', rounds: '7', card: 'A1B2C3D4', t: '27.0', light: 'enough' },
    { d: daysAgo(4), start: '14:00', end: '15:30', rounds: '3', card: 'A1B2C3D4', t: '31.2', light: 'bright' },
    { d: daysAgo(5), start: '19:20', end: '21:45', rounds: '5', card: 'A1B2C3D4', t: '28.6', light: 'enough' },
  ];
  function renderLogList() {
    $('[data-bind="logList"]').innerHTML = sessions.slice(0, 3).map((s) =>
      `<li><span>${dayLabel(s.d)}</span><span>${s.start} → ${s.end}</span><span class="r">${s.rounds} rd</span></li>`).join('');
    if (historyDrawn) renderSessionRows();
  }

  const BARS = {
    week: () => Array.from({ length: 7 }, (_, i) => {
      const d = daysAgo(6 - i);
      return { k: DAYS[d.getDay()], v: i === 6 ? T.today : [4, 6, 3, 7, 2, 1][i], now: i === 6 };
    }),
    month: () => ['W1', 'W2', 'W3', 'W4'].map((k, i) => ({ k, v: [18, 24, 30, 26][i], now: i === 3 })),
    year: () => ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'].map((k, i) => ({ k, v: [40, 52, 66, 30, 58, 22, 10, 14, 61, 88, 98, 0][i], now: i === today.getMonth() })),
  };
  let range = 'week';
  function renderBars() {
    const data = BARS[range]();
    const max = Math.max(...data.map((d) => d.v), 1);
    $('.bars').innerHTML = data.map((d) =>
      `<div class="bar${d.now ? ' today' : ''}"><span class="v">${d.v}</span><span class="col" style="height:${Math.round((d.v / max) * 84)}px"></span><span class="d">${d.k}</span></div>`).join('');
    $('.bars').setAttribute('aria-label', `Rounds finished per ${range === 'week' ? 'day' : range === 'month' ? 'week' : 'month'}: ${data.map((d) => `${d.k} ${d.v}`).join(', ')}`);
  }
  $$('.seg [data-range]').forEach((b) => b.addEventListener('click', () => {
    range = b.dataset.range;
    $$('.seg [data-range]').forEach((x) => x.setAttribute('aria-selected', String(x === b)));
    renderBars();
  }));

  // ---------- history ----------
  let historyDrawn = false;
  const RANGE = { 7: [26, 3, 2], 30: [98, 11, 9], 90: [281, 29, 24] };
  function renderStats() {
    const days = $('#range').value;
    const [rounds, early, rem] = RANGE[days];
    const mins = rounds * settings.focus;
    bind('rangeLabel', `Last ${days} days`);
    bind('hRounds', rounds);
    bind('hRoundsSub', `finished in ${days} days`);
    bind('hFocus', `${Math.floor(mins / 60)}h${pad(mins % 60)}`);
    bind('hFocusSub', `${rounds} × ${settings.focus} min`);
    bind('hEarly', early);
    bind('hRem', rem);
  }
  $('#range').addEventListener('change', renderStats);

  function heatLevel(day, hour) {
    // day 0 = Mon … 6 = Sun ; hours 6..23
    const weekend = day >= 5;
    let v = 0;
    if (!weekend) {
      if (hour >= 19 && hour <= 22) v = 3 + ((day + hour) % 2);
      else if (hour === 14 || hour === 15) v = 1 + (day % 2);
      else if (hour === 18 || hour === 23) v = (day + hour) % 3 === 0 ? 1 : 0;
    } else {
      if (hour >= 8 && hour <= 11) v = 2 + ((hour === 10 || (day === 6 && hour === 9)) ? 1 : 0);
      if (day === 6 && hour === 18) v = 1;
    }
    return v;
  }
  function drawHeatmap() {
    const names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    let html = '';
    names.forEach((n, d) => {
      html += `<span class="hd">${n}</span>`;
      for (let h = 6; h <= 23; h++) html += `<span class="c h${heatLevel(d, h)}" title="${n} ${pad(h)}:00"></span>`;
    });
    html += '<span></span>';
    for (let h = 6; h <= 23; h++) html += `<span class="hx">${h % 3 === 0 ? h : ''}</span>`;
    $('.heatmap').innerHTML = html;
  }
  function drawLineChart() {
    const svg = $('.linechart');
    const X0 = 60, X1 = 600, Y0 = 18, Y1 = 186;
    const temp = [], hum = [];
    for (let i = 0; i <= 24; i++) {
      const hour = (today.getHours() - 24 + i + 24) % 24;
      const day = Math.cos(((hour - 14) / 24) * 2 * Math.PI); // 1 at 14:00
      temp.push(28.4 + 2.6 * day + (rnd() - 0.5) * 0.3);
      hum.push(67 - 9 * day + (rnd() - 0.5) * 1.2);
    }
    const x = (i) => X0 + (i / 24) * (X1 - X0);
    const yT = (v) => Y1 - ((v - 24) / (34 - 24)) * (Y1 - Y0);
    const yH = (v) => Y1 - ((v - 45) / (85 - 45)) * (Y1 - Y0);
    let g = '';
    [26, 28, 30, 32].forEach((t, k) => {
      const y = yT(t);
      g += `<line class="grid" x1="${X0}" x2="${X1}" y1="${y}" y2="${y}"/>`;
      g += `<text x="${X0 - 8}" y="${y + 4}" text-anchor="end">${t}°</text>`;
      g += `<text x="${X1 + 8}" y="${y + 4}">${[53, 61, 69, 77][k]}%</text>`;
    });
    g += `<line class="axis" x1="${X0}" x2="${X1}" y1="${Y1}" y2="${Y1}"/>`;
    for (let i = 0; i <= 24; i += 6) {
      const d = new Date(today.getTime() - (24 - i) * 3600000);
      g += `<text x="${x(i)}" y="${Y1 + 24}" text-anchor="${i === 0 ? 'start' : i === 24 ? 'end' : 'middle'}">${pad(d.getHours())}:00</text>`;
    }
    const path = (arr, fy) => arr.map((v, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)},${fy(v).toFixed(1)}`).join(' ');
    g += `<path class="h" d="${path(hum, yH)}"/><path class="t" d="${path(temp, yT)}"/>`;
    svg.innerHTML = g;
  }
  function renderSessionRows() {
    $('[data-bind="sessionRows"]').innerHTML = sessions.map((s) =>
      `<tr><td>${dayLabel(s.d)}</td><td>${s.start} → ${s.end}</td><td class="r">${s.rounds}</td><td>${s.card}</td><td>${s.t}</td><td>${s.light}</td></tr>`).join('');
  }
  function drawHistory() {
    renderStats();
    if (historyDrawn) return;
    historyDrawn = true;
    drawHeatmap();
    drawLineChart();
    renderSessionRows();
  }
  $('[data-action="export"]').addEventListener('click', () => {
    const rows = [['date', 'start', 'end', 'rounds', 'card', 'avg_temp_c', 'light']]
      .concat(sessions.map((s) => [s.d.toISOString().slice(0, 10), s.start, s.end, s.rounds, s.card, s.t, s.light]));
    const blob = new Blob([rows.map((r) => r.join(',')).join('\n')], { type: 'text/csv' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'study-sessions.csv';
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
    toast('Exported study-sessions.csv (sample data).', { icon: 'i-download' });
  });

  // ---------- settings ----------
  let cards = [{ uid: 'A1B2C3D4', name: 'My student card' }];
  function renderCards() {
    $('[data-bind="cardList"]').innerHTML = cards.map((c, i) =>
      `<li><span class="uid">${esc(c.uid)}</span><span class="name">${esc(c.name)}</span><button type="button" class="btn btn-outline btn-remove" data-remove="${i}" aria-label="Remove card ${esc(c.uid)}">Remove</button></li>`).join('')
      || '<li class="waiting">No cards yet. Add one to start sessions with a tap.</li>';
  }
  $('[data-bind="cardList"]').addEventListener('click', (e) => {
    const b = e.target.closest('[data-remove]');
    if (!b) return;
    const i = Number(b.dataset.remove);
    const [removed] = cards.splice(i, 1);
    renderCards();
    toast(`Card ${esc(removed.uid)} removed.`, { action: { label: 'Undo', fn: () => { cards.splice(i, 0, removed); renderCards(); } }, ms: 6000 });
  });
  $('[data-action="add-card"]').addEventListener('click', (e) => {
    const btn = e.currentTarget;
    btn.disabled = true;
    const li = document.createElement('li');
    li.className = 'waiting';
    li.textContent = 'Waiting for a card… tap it on the box.';
    $('[data-bind="cardList"]').append(li);
    setTimeout(() => {
      const uid = Array.from({ length: 4 }, () => Math.floor(Math.random() * 256).toString(16).padStart(2, '0')).join('').toUpperCase();
      cards.push({ uid, name: `Card ${cards.length + 1}` });
      renderCards();
      btn.disabled = false;
      toast(`Card ${uid} added ${mqtt('study/rfid', { uid, action: 'start' }, '→')}`, { icon: 'i-card' });
    }, 2000);
  });
  const numField = (id, lo, hi) => {
    const inp = $(id);
    const v = Number(inp.value);
    const ok = Number.isInteger(v) && v >= lo && v <= hi;
    if (inp.getAttribute('aria-describedby')) setErr(inp, ok ? '' : `Enter a whole number from ${lo} to ${hi}.`);
    else if (ok) inp.removeAttribute('aria-invalid'); else inp.setAttribute('aria-invalid', 'true');
    return ok ? v : null;
  };
  $('#form-settings').addEventListener('submit', (e) => {
    e.preventDefault();
    const vals = {
      focus: numField('#st-focus', 1, 120),
      short: numField('#st-short', 1, 120),
      long: numField('#st-long', 1, 120),
      every: numField('#st-every', 1, 12),
      remind: numField('#st-remind', 10, 240),
    };
    const bad = Object.entries(vals).find(([, v]) => v === null);
    if (bad) {
      $(`#st-${bad[0]}`).focus();
      toast('Some values need fixing before saving.', { icon: 'i-alert' });
      return;
    }
    Object.assign(settings, vals);
    bind('pFocus', settings.focus);
    bind('pShort', settings.short);
    bind('pLong', settings.long);
    T.round = Math.min(T.round, settings.every);
    renderRounds();
    if (!T.running) previewPreset();
    renderSession();
    toast('Settings saved.');
  });

  // ---------- desktop windows ----------
  const win = (id) => $(`.win[data-win="${id}"]`);
  const COLS = [['climate', 'light', 'session'], ['timer'], ['lcd', 'log']];
  const SHARE = [0.30, 0.33, 0.37];
  const MAXW = [340, 380, 420];
  let userMoved = false;
  let z = 10;

  function arrange() {
    if (!isDesktop() || document.body.dataset.screen !== 'workspace') return;
    const canvas = $('.canvas');
    const GAP = 28;
    const avail = canvas.clientWidth - GAP * 4;
    let x = GAP;
    COLS.forEach((col, ci) => {
      const w = Math.round(Math.min(MAXW[ci], avail * SHARE[ci]));
      let y = GAP, any = false;
      col.forEach((id) => {
        const el = win(id);
        if (el.classList.contains('is-closed')) return;
        any = true;
        el.style.setProperty('--w', `${w}px`);
        el.style.setProperty('--x', `${x}px`);
        el.style.setProperty('--y', `${y}px`);
        y += el.offsetHeight + 20;
      });
      if (any) x += w + GAP;
    });
    userMoved = false;
  }
  $('[data-action="arrange"]').addEventListener('click', () => {
    $$('.win').forEach((w) => { w.classList.remove('is-closed', 'is-min'); });
    syncDock();
    arrange();
  });

  function syncDock() {
    $$('[data-toggle]').forEach((b) => b.setAttribute('aria-pressed', String(!win(b.dataset.toggle).classList.contains('is-closed'))));
    $$('.win').forEach((w) => {
      const min = w.classList.contains('is-min');
      const btn = $('[data-win-action="min"]', w);
      btn.setAttribute('aria-expanded', String(!min));
    });
  }
  $$('[data-toggle]').forEach((b) => b.addEventListener('click', () => {
    const w = win(b.dataset.toggle);
    w.classList.toggle('is-closed');
    if (!w.classList.contains('is-closed')) { w.classList.remove('is-min'); w.style.zIndex = ++z; }
    syncDock();
  }));
  $$('.win').forEach((w) => {
    $('[data-win-action="min"]', w).addEventListener('click', () => { w.classList.toggle('is-min'); syncDock(); });
    $('[data-win-action="close"]', w).addEventListener('click', () => {
      w.classList.add('is-closed');
      syncDock();
      const b = $(`[data-toggle="${w.dataset.win}"]`);
      if (b && b.offsetParent) b.focus();
    });
    w.addEventListener('pointerdown', () => { if (isDesktop()) w.style.zIndex = ++z; });

    const head = $('.win-head', w);
    head.addEventListener('pointerdown', (e) => {
      if (!isDesktop() || e.button !== 0 || e.target.closest('button')) return;
      const canvas = $('.canvas').getBoundingClientRect();
      const sx = e.clientX, sy = e.clientY;
      const ox = parseFloat(w.style.getPropertyValue('--x')) || 0;
      const oy = parseFloat(w.style.getPropertyValue('--y')) || 0;
      head.setPointerCapture(e.pointerId);
      w.classList.add('is-dragging');
      const move = (ev) => {
        const nx = clamp(ox + ev.clientX - sx, 0, canvas.width - w.offsetWidth);
        const ny = clamp(oy + ev.clientY - sy, 0, canvas.height - 46);
        w.style.setProperty('--x', `${nx}px`);
        w.style.setProperty('--y', `${ny}px`);
        userMoved = true;
      };
      const up = () => {
        w.classList.remove('is-dragging');
        head.removeEventListener('pointermove', move);
        head.removeEventListener('pointerup', up);
        head.removeEventListener('pointercancel', up);
      };
      head.addEventListener('pointermove', move);
      head.addEventListener('pointerup', up);
      head.addEventListener('pointercancel', up);
    });
  });

  let resizeT;
  window.addEventListener('resize', () => {
    clearTimeout(resizeT);
    resizeT = setTimeout(() => { if (!userMoved) arrange(); }, 120);
  });

  // ---------- boot ----------
  renderDht();
  renderLight();
  renderSession();
  renderRounds();
  renderTimer();
  renderLcd();
  renderBars();
  renderLogList();
  renderCards();
  tickClock();
  route();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => { if (!userMoved) arrange(); });

  setInterval(() => { renderTimer(); renderSession(); }, 250);
  setInterval(tickClock, 1000);
  setInterval(stepDht, 5000);
  setInterval(stepLight, 3000);
})();
