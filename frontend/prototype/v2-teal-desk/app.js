/* Trạm học tập: prototype v2 behaviour.
   Everything is simulated in the browser. Nothing is sent over MQTT; the UI
   only shows which topic and payload (docs/topics.md) the real app would use. */
(() => {
  'use strict';

  // ---------- helpers ----------
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const pad = (n) => String(n).padStart(2, '0');
  const hm = (d) => `${pad(d.getHours())}:${pad(d.getMinutes())}`;
  const mmss = (s) => `${pad(Math.floor(s / 60))}:${pad(s % 60)}`;
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const vn1 = (v) => v.toFixed(1).replace('.', ',');
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const bind = (k, v) => $$(`[data-bind="${k}"]`).forEach((el) => { el.textContent = v; });
  const DOW_SHORT = ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'];
  const DOW_LONG = ['Chủ Nhật', 'Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy'];
  const dateShort = (d) => `${DOW_SHORT[d.getDay()]} ${pad(d.getDate())}/${pad(d.getMonth() + 1)}`;
  let seed = 11;
  const rnd = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };
  const payload = (topic, obj) => `${topic} ← ${JSON.stringify(obj)}`;

  function toast(html, opts = {}) {
    const t = document.createElement('div');
    t.className = `toast${opts.warn ? ' warn' : ''}`;
    t.setAttribute('role', 'status');
    t.innerHTML = `<svg class="ic" aria-hidden="true"><use href="#${opts.icon || 'i-check'}"/></svg><div>${html}</div>`;
    const close = () => { if (!t.isConnected) return; t.classList.add('out'); setTimeout(() => t.remove(), 200); };
    if (opts.action) {
      const b = document.createElement('button');
      b.className = 'btn btn-outline';
      b.textContent = opts.action.label;
      b.addEventListener('click', () => { opts.action.fn(); close(); });
      t.append(b);
    }
    $('.toasts').append(t);
    setTimeout(close, opts.ms || 4200);
  }

  // ---------- state ----------
  const now0 = Date.now();
  const cfg = { focus: 25, short: 5, long: 15, every: 4, goal: 8, remind: 50, hot: 30, dark: 1200 };
  let lastMsg = now0 - 2000;

  // ---------- feed (command log) ----------
  const feed = [];
  function log(kind, text, at = Date.now(), fresh = true) {
    feed.unshift({ kind, text, at, fresh });
    feed.sort((a, b) => b.at - a.at);
    if (feed.length > 9) feed.length = 9;
    renderFeed();
  }
  const DIR = {
    out: ['dir-out', 'i-out', 'Gửi đi'],
    in: ['dir-in', 'i-in', 'Nhận về'],
    tg: ['dir-tg', 'i-bell', 'Telegram'],
  };
  function renderFeed() {
    $('[data-feed]').innerHTML = feed.map((f) => {
      const [cls, ic, label] = DIR[f.kind];
      return `<li class="${f.fresh ? 'is-new' : ''}"><time>${hm(new Date(f.at))}</time><span class="dir ${cls}"><svg class="ic" aria-hidden="true"><use href="#${ic}"/></svg>${label}</span><span class="msg">${f.kind === 'tg' ? esc(f.text) : `<code>${esc(f.text)}</code>`}</span></li>`;
    }).join('');
    feed.forEach((f) => { f.fresh = false; });
  }

  // ---------- routing ----------
  const SCREENS = ['signin', 'register', 'home', 'session', 'history', 'settings'];
  const TITLES = { signin: 'Đăng nhập', register: 'Tạo tài khoản', home: 'Tổng quan', session: 'Phiên học', history: 'Lịch sử', settings: 'Cài đặt' };
  function route() {
    const parts = (location.hash || '#/signin').replace(/^#\/?/, '').split('/');
    const screen = SCREENS.includes(parts[0]) ? parts[0] : 'signin';
    document.body.dataset.screen = screen;
    const isAuth = screen === 'signin' || screen === 'register';
    $('[data-auth]').hidden = !isAuth;
    $('.app').hidden = isAuth;
    $$('[data-form]').forEach((f) => { f.hidden = f.dataset.form !== screen; });
    $$('[data-screen-id]').forEach((s) => { s.hidden = s.dataset.screenId !== screen; });
    $$('[data-nav]').forEach((a) => {
      if (a.dataset.nav === screen) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current');
    });
    bind('pageTitle', TITLES[screen]);
    document.title = `${TITLES[screen]} · Trạm học tập`;
    if (screen === 'settings') selectTab(parts[1] || currentTab, false);
    if (screen === 'history') drawHistory();
    window.scrollTo(0, 0);
    requestAnimationFrame(drawSquares);
  }
  window.addEventListener('hashchange', route);

  // ---------- auth ----------
  const emailOk = (v) => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v.trim());
  function setErr(input, msg) {
    const ids = (input.getAttribute('aria-describedby') || '').split(' ');
    const el = ids.map((id) => document.getElementById(id)).find((e) => e && e.classList.contains('field-error'));
    if (msg) input.setAttribute('aria-invalid', 'true'); else input.removeAttribute('aria-invalid');
    if (el) el.textContent = msg || '';
    return !msg;
  }
  const RULES = {
    email: (v) => (!v.trim() ? 'Vui lòng nhập email.' : !emailOk(v) ? 'Email chưa đúng dạng, ví dụ ban@student.hcmus.edu.vn.' : ''),
    password: (v) => (v.length < 8 ? `Mật khẩu cần ít nhất 8 ký tự (hiện có ${v.length}).` : ''),
    name: (v) => (!v.trim() ? 'Vui lòng nhập họ và tên.' : ''),
    password2: (v) => (v !== $('#rg-pass').value ? 'Hai mật khẩu chưa khớp.' : ''),
  };
  function wireForm(form, done) {
    const inputs = $$('input[name]', form);
    inputs.forEach((i) => i.addEventListener('blur', () => { if (i.value || i.hasAttribute('aria-invalid')) setErr(i, RULES[i.name](i.value)); }));
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const bad = inputs.filter((i) => !setErr(i, RULES[i.name](i.value)));
      if (bad.length) { bad[0].focus(); return; }
      const btn = $('button[type="submit"]', form);
      btn.classList.add('is-loading');
      btn.disabled = true;
      setTimeout(() => { btn.classList.remove('is-loading'); btn.disabled = false; done(); }, 700);
    });
  }
  wireForm($('#form-signin'), () => { location.hash = '#/home'; toast('Đăng nhập thành công. Hộp đang kết nối.'); });
  wireForm($('#form-register'), () => { location.hash = '#/home'; toast('Đã tạo tài khoản. Chào mừng bạn đến với Trạm học tập.'); });

  $$('[data-reveal]').forEach((b) => b.addEventListener('click', () => {
    const inp = document.getElementById(b.dataset.reveal);
    const show = inp.type === 'password';
    inp.type = show ? 'text' : 'password';
    b.setAttribute('aria-pressed', String(show));
    b.setAttribute('aria-label', show ? 'Ẩn mật khẩu' : 'Hiện mật khẩu');
  }));
  $('#rg-pass').addEventListener('input', (e) => {
    const v = e.target.value;
    const score = (v.length >= 8) + /[A-Z]/.test(v) + /\d/.test(v) + /[^A-Za-z0-9]/.test(v);
    $('.strength').dataset.level = v ? Math.max(1, score) : 0;
    bind('strength', !v ? 'Dùng chữ hoa, chữ số và ký tự đặc biệt để mật khẩu mạnh hơn.'
      : ['Mật khẩu yếu.', 'Mật khẩu yếu.', 'Mật khẩu trung bình.', 'Mật khẩu khá.', 'Mật khẩu mạnh.'][score]);
  });
  document.addEventListener('click', (e) => {
    if (e.target.closest('[data-action="forgot"]')) {
      e.preventDefault();
      toast('Bản mẫu: app thật sẽ gửi đường dẫn đặt lại mật khẩu qua email.', { icon: 'i-alert', warn: true });
    }
  });

  // ---------- greeting, clock, MQTT age ----------
  function tickClock() {
    const d = new Date();
    const h = d.getHours();
    bind('greeting', h < 11 ? 'Chào buổi sáng' : h < 13 ? 'Chào buổi trưa' : h < 18 ? 'Chào buổi chiều' : 'Chào buổi tối');
    bind('dateLong', `${DOW_LONG[d.getDay()]}, ${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()}`);
    const age = Math.max(0, Math.round((Date.now() - lastMsg) / 1000));
    bind('age', `${age} giây`);
  }

  // ---------- DHT22 + LDR ----------
  const env = { temp: 29.5, hum: 70, raw: 2100, t: [], h: [] };
  for (let i = 0; i < 30; i++) {
    const k = i / 29;
    env.t.push(28.4 + 1.1 * k + (rnd() - 0.5) * 0.3);
    env.h.push(73.5 - 3.5 * k + (rnd() - 0.5) * 0.9);
  }
  env.t[29] = env.temp; env.h[29] = env.hum;

  function spark(sel, arr, lo, hi) {
    const pts = arr.map((v, i) => `${(i / (arr.length - 1)) * 160},${(36 - ((v - lo) / (hi - lo)) * 32).toFixed(1)}`).join(' ');
    $$(`${sel} polyline`).forEach((p) => p.setAttribute('points', pts));
  }
  function setState(key, text, kind) {
    $$(`[data-state="${key}"]`).forEach((el) => { el.textContent = text; el.className = `state${kind ? ` state-${kind}` : ''}`; });
  }
  function renderEnv() {
    bind('temp', vn1(env.temp));
    bind('hum', Math.round(env.hum));
    bind('raw', env.raw);
    const hot = env.temp >= cfg.hot;
    const warm = env.temp > 28;
    setState('temp', hot ? 'Nóng' : warm ? 'Hơi ấm' : env.temp < 22 ? 'Hơi lạnh' : 'Dễ chịu', hot ? 'bad' : warm ? '' : 'ok');
    const humOk = env.hum >= 40 && env.hum <= 75;
    setState('hum', humOk ? 'Bình thường' : env.hum > 75 ? 'Ẩm' : 'Khô', humOk ? 'ok' : '');
    const enough = env.raw >= cfg.dark;
    setState('light', enough ? 'Đủ sáng' : 'Thiếu sáng', enough ? 'ok' : 'bad');
    bind('lightState', enough ? 'Đủ sáng' : 'Thiếu sáng');
    $$('.meter').forEach((m) => {
      m.classList.toggle('dim', !enough);
      $('.meter-fill', m).style.width = `${(env.raw / 4095) * 100}%`;
      $('.meter-mark', m).style.left = `${(cfg.dark / 4095) * 100}%`;
    });
    bind('tip', !enough ? 'Góc học đang thiếu sáng. Bật đèn bàn để đỡ mỏi mắt nhé.'
      : hot ? `Phòng đang nóng (từ ${cfg.hot} °C). Bạn hoàn thành nhiều vòng nhất ở 26–28 °C.`
      : warm ? 'Phòng đang hơi ấm. Bạn hoàn thành nhiều vòng nhất ở 26–28 °C, thử bật quạt nhé.'
      : 'Điều kiện đang tốt cho một vòng tập trung.');
    spark('.spark-temp', env.t, 27.6, 30.6);
    spark('.spark-hum', env.h, 64, 77);
  }
  function stepEnv() {
    env.temp = clamp(env.temp + (Math.random() - 0.5) * 0.2, 27, 31.5);
    env.hum = clamp(env.hum + (Math.random() - 0.5) * 0.8, 60, 78);
    env.raw = Math.round(clamp(env.raw + (Math.random() - 0.5) * 120, 1700, 2500));
    env.t.push(env.temp); env.t.shift();
    env.h.push(env.hum); env.h.shift();
    lastMsg = Date.now();
    renderEnv();
  }

  // ---------- RFID session ----------
  const sess = { active: true, uid: 'A1B2C3D4', start: now0 - (56 * 60 + 18) * 1000 };
  function renderSession() {
    const warn = $('[data-bind="breakWarn"]');
    if (!sess.active) {
      bind('sessionElapsed', '0:00:00');
      bind('uid', '—'); bind('sessionStart', '—');
      bind('sessionTag', 'Chưa bắt đầu'); $('[data-bind="sessionTag"]').className = 'tag tag-off';
      bind('cardState', 'Chưa quẹt');
      bind('tapLabel', 'Mô phỏng quẹt thẻ để bắt đầu');
      warn.hidden = true;
      return;
    }
    const s = Math.floor((Date.now() - sess.start) / 1000);
    bind('sessionElapsed', `${Math.floor(s / 3600)}:${pad(Math.floor(s / 60) % 60)}:${pad(s % 60)}`);
    bind('uid', sess.uid);
    bind('sessionStart', hm(new Date(sess.start)));
    bind('sessionTag', 'Đang học'); $('[data-bind="sessionTag"]').className = 'tag tag-teal';
    bind('cardState', 'Đang học');
    bind('tapLabel', 'Mô phỏng quẹt thẻ để kết thúc');
    warn.hidden = s < cfg.remind * 60;
    bind('breakMin', Math.floor(s / 60));
    bind('breakAt', hm(new Date(sess.start + cfg.remind * 60000)));
  }
  $('[data-action="tap"]').addEventListener('click', () => {
    sess.active = !sess.active;
    const action = sess.active ? 'start' : 'stop';
    if (sess.active) sess.start = Date.now(); else sessions[0].end = hm(new Date());
    log('in', payload('study/rfid', { uid: 'A1B2C3D4', action }).replace('←', '→'));
    renderSession();
    $('[data-bind="rate"]').hidden = sess.active;   // one-tap rating appears when a session ends
    if (sess.active) sessions[0].rate = 0;
    if (historyDrawn) renderRows();
    toast(sess.active ? 'Đã quẹt thẻ: bắt đầu phiên học.' : 'Đã quẹt thẻ: kết thúc phiên học.', { icon: 'i-card' });
  });

  // ---------- one-tap session rating ----------
  // Kept in the browser only: the real app needs a place to store it (nothing in docs/topics.md yet).
  const RATES = { 1: 'Mất tập trung', 2: 'Tạm ổn', 3: 'Tập trung tốt' };
  $$('[data-rate]').forEach((b) => b.addEventListener('click', () => {
    const box = $('[data-bind="rate"]');
    const v = Number(b.dataset.rate);
    box.hidden = true;
    if (!v) return;
    sessions[0].rate = v;
    if (historyDrawn) renderRows();
    toast(`Đã lưu đánh giá: ${RATES[v].toLowerCase()}.`, { action: { label: 'Hoàn tác', fn: () => { sessions[0].rate = 0; box.hidden = false; if (historyDrawn) renderRows(); } }, ms: 6000 });
  }));

  // ---------- timer ----------
  const MODE = { focus: 'Tập trung', short: 'Nghỉ ngắn', long: 'Nghỉ dài', custom: 'Tùy chỉnh' };
  const T = { preset: 'focus', mode: 'focus', total: 25 * 60, endAt: now0 + (18 * 60 + 42) * 1000, left: 0, running: true, round: 3, advance: false, today: 2 };
  const minutesOf = (p) => (p === 'custom' ? Number($('#custom-min').value) : cfg[p]);
  const timeLeft = () => (T.running ? Math.max(0, Math.ceil((T.endAt - Date.now()) / 1000)) : T.left);

  function drawSquares() {
    $$('[data-sq]').forEach((sq) => {
      const w = sq.clientWidth, h = sq.clientHeight;
      if (!w) return;
      const i = 2;
      const d = `M${w / 2},${i} H${w - i} V${h - i} H${i} V${i} Z`;
      $$('path', sq).forEach((p) => { p.setAttribute('d', d); p.setAttribute('pathLength', '100'); });
    });
    renderTimer();
  }
  function renderCycle() {
    const html = Array.from({ length: cfg.every }, (_, i) => {
      const done = i < T.round - 1 || (i === T.round - 1 && T.advance);
      const now = i === T.round - 1 && !T.advance;
      return `<i class="${done ? 'done' : now ? 'now' : ''}">${i + 1}</i>`;
    }).join('');
    $$('[data-cycle]').forEach((c) => { c.innerHTML = html; c.setAttribute('aria-label', `Vòng ${T.round} trên ${cfg.every}`); });
    bind('roundText', `Vòng ${T.round}/${cfg.every} · sau vòng ${cfg.every} nghỉ dài`);
    const g = Array.from({ length: cfg.goal }, (_, i) => `<i class="${i < T.today ? 'done' : i === T.today && T.running && T.mode !== 'short' && T.mode !== 'long' ? 'now' : ''}"></i>`).join('');
    $$('[data-goal]').forEach((el) => { el.innerHTML = g; el.style.gridTemplateColumns = `repeat(${cfg.goal}, 1fr)`; el.setAttribute('aria-label', `Đã xong ${T.today} trên ${cfg.goal} vòng`); });
    bind('today', T.today);
    bind('todayMin', T.today * cfg.focus);
  }
  function renderTimer() {
    if (T.running && timeLeft() === 0) finishRound();
    const l = timeLeft();
    bind('count', mmss(l));
    const isFocus = T.mode === 'focus' || T.mode === 'custom';
    bind('modeLabel', T.running ? MODE[T.mode] : l === 0 ? 'Đã xong' : l === T.total ? 'Sẵn sàng' : 'Đã dừng');
    bind('countSub', T.running ? `còn lại trong ${mmss(T.total)}${isFocus ? '' : ' · giờ nghỉ'}` : l === T.total ? `${MODE[T.mode]} · ${T.total / 60} phút` : 'Đồng hồ trên trang đã dừng');
    const pct = T.total ? ((T.total - l) / T.total) * 100 : 0;
    $$('[data-sq]').forEach((sq) => {
      sq.classList.toggle('is-paused', !T.running);
      sq.classList.toggle('is-break', !isFocus);
      $('.sq-bar', sq).setAttribute('stroke-dasharray', `${pct.toFixed(2)} 100`);
    });
    $$('[data-action="timer-stop"]').forEach((b) => { b.disabled = !T.running; });
  }
  function finishRound() {
    T.running = false; T.left = 0;
    if (T.mode === 'focus' || T.mode === 'custom') {
      T.today += 1; T.advance = true;
      selectPreset(T.round % cfg.every === 0 ? 'long' : 'short', false);
    } else selectPreset('focus', false);
    renderCycle();
    log('tg', 'Hết giờ: còi trên hộp kêu 3 hồi');
    toast('Hết giờ! Còi trên hộp kêu 3 hồi. Đứng dậy vươn vai nhé.', { icon: 'i-bell', warn: true, ms: 6000 });
  }
  function updatePayloadPreview() {
    const m = minutesOf(T.preset);
    bind('timerPayload', payload('study/timer', { minutes: Number.isFinite(m) ? m : 0 }));
  }
  function selectPreset(p, preview = true) {
    T.preset = p;
    $$('[data-preset]').forEach((b) => b.setAttribute('aria-checked', String(b.dataset.preset === p)));
    $('[data-stepper]').hidden = p !== 'custom';
    if (p !== 'custom') setErr($('#custom-min'), '');
    updatePayloadPreview();
    if (preview && !T.running) { T.mode = p; T.total = minutesOf(p) * 60; T.left = T.total; renderTimer(); }
  }
  $$('[data-preset]').forEach((b) => b.addEventListener('click', () => selectPreset(b.dataset.preset)));
  $('.seg[role="radiogroup"]').addEventListener('keydown', (e) => {
    const btns = $$('[data-preset]');
    const i = btns.findIndex((b) => b.getAttribute('aria-checked') === 'true');
    const n = e.key === 'ArrowRight' || e.key === 'ArrowDown' ? 1 : e.key === 'ArrowLeft' || e.key === 'ArrowUp' ? -1 : 0;
    if (!n) return;
    e.preventDefault();
    const next = btns[(i + n + btns.length) % btns.length];
    next.focus(); selectPreset(next.dataset.preset);
  });
  const checkCustom = () => {
    const v = Number($('#custom-min').value);
    return setErr($('#custom-min'), Number.isInteger(v) && v >= 1 && v <= 120 ? '' : 'Nhập số phút nguyên từ 1 đến 120.');
  };
  $('#custom-min').addEventListener('input', () => { if (checkCustom()) selectPreset('custom'); else updatePayloadPreview(); });
  $$('[data-step]').forEach((b) => b.addEventListener('click', () => {
    const inp = $('#custom-min');
    inp.value = clamp((Number(inp.value) || 0) + Number(b.dataset.step), 1, 120);
    checkCustom(); selectPreset('custom');
  }));
  document.addEventListener('click', (e) => {
    if (e.target.closest('[data-action="timer-send"]')) {
      if (T.preset === 'custom' && !checkCustom()) {
        if (document.body.dataset.screen !== 'session') location.hash = '#/session';
        setTimeout(() => $('#custom-min').focus(), 50);
        return;
      }
      const minutes = minutesOf(T.preset);
      T.mode = T.preset;
      if ((T.mode === 'focus' || T.mode === 'custom') && T.advance) { T.round = (T.round % cfg.every) + 1; T.advance = false; }
      T.total = minutes * 60;
      T.endAt = Date.now() + T.total * 1000;
      T.running = true;
      renderCycle(); renderTimer();
      log('out', payload('study/timer', { minutes }));
      toast(`Đã gửi xuống hộp: ${MODE[T.mode].toLowerCase()} ${minutes} phút.<code>${esc(payload('study/timer', { minutes }))}</code>`, { icon: 'i-send' });
    }
    if (e.target.closest('[data-action="timer-stop"]')) {
      T.left = timeLeft(); T.running = false;
      renderTimer(); renderCycle();
      toast('Đã dừng đồng hồ trên trang. docs/topics.md chưa có lệnh dừng nên hộp vẫn đếm tiếp.', { icon: 'i-alert', warn: true, ms: 6500 });
    }
  });

  // ---------- LCD ----------
  const toAscii = (s) => s.normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/đ/g, 'd').replace(/Đ/g, 'D').replace(/[^\x20-\x7E]/g, '?');
  function wrap16(t) {
    if (t.length <= 16) return [t, ''];
    const i = t.lastIndexOf(' ', 16);
    if (i > 0 && t.length - i - 1 <= 16) return [t.slice(0, i), t.slice(i + 1)];
    return [t.slice(0, 16), t.slice(16, 32)];
  }
  function paintLcd(el, text) {
    const lines = wrap16(text);
    $$('.lcd-row', el).forEach((row, r) => {
      row.innerHTML = [...lines[r].padEnd(16, ' ').slice(0, 16)].map((c) => `<span>${c === ' ' ? '&nbsp;' : esc(c)}</span>`).join('');
    });
    el.setAttribute('aria-label', `Màn hình LCD: ${lines.filter(Boolean).join(' / ') || 'trống'}`);
    return lines;
  }
  const lcdInput = $('#lcd-text');
  const lcdSent = { raw: 'Ôn tập chương 3', text: 'On tap chuong 3', at: now0 - 35 * 60000 };
  function lcdDraft() {
    const raw = lcdInput.value.trim().replace(/\s+/g, ' ');
    const text = toAscii(raw);
    return { raw, text: text.slice(0, 32), over: text.length > 32 };
  }
  function renderLcd() {
    const d = lcdDraft();
    const lines = paintLcd($('[data-lcd="draft"]'), d.text);
    bind('line1', lines[0].length); bind('line2', lines[1].length);
    bind('lcdCount', d.text.length);
    $('[data-bind="lcdCount"]').classList.toggle('over', d.over);
    const conv = $('[data-bind="lcdConv"]');
    if (!d.raw) { conv.textContent = 'Nhập lời nhắc để hiện trên hộp.'; conv.classList.remove('is-clean'); }
    else if (d.over) { conv.textContent = `Dài quá 32 ký tự. Hộp chỉ hiện: “${d.text}”.`; conv.classList.remove('is-clean'); }
    else if (d.text !== d.raw) { conv.textContent = `LCD không có dấu tiếng Việt. Hộp sẽ hiện: “${d.text}”.`; conv.classList.remove('is-clean'); }
    else { conv.textContent = 'Không có dấu, hộp hiện đúng như bạn gõ.'; conv.classList.add('is-clean'); }
    bind('lcdPayload', payload('study/lcd', { text: d.text }));
  }
  function renderLcdShown() {
    paintLcd($('[data-lcd="shown"]'), lcdSent.text);
    bind('lcdSentAt', hm(new Date(lcdSent.at)));
    bind('lcdSentRaw', lcdSent.raw);
  }
  lcdInput.addEventListener('input', renderLcd);
  $$('[data-quick]').forEach((b) => b.addEventListener('click', () => { lcdInput.value = b.dataset.quick; renderLcd(); lcdInput.focus(); }));
  $('#form-lcd').addEventListener('submit', (e) => {
    e.preventDefault();
    const d = lcdDraft();
    if (!d.raw) { lcdInput.focus(); return; }
    Object.assign(lcdSent, { raw: d.raw, text: d.text, at: Date.now() });
    renderLcdShown();
    log('out', payload('study/lcd', { text: d.text }));
    toast(`Đã gửi lên màn hình.<code>${esc(payload('study/lcd', { text: d.text }))}</code>`, { icon: 'i-lcd' });
  });

  // ---------- sessions / week ----------
  const today = new Date();
  const daysAgo = (n) => { const d = new Date(today); d.setDate(d.getDate() - n); return d; };
  const sessions = [
    { d: daysAgo(0), start: hm(new Date(sess.start)), end: 'đang học', rounds: '2+1', card: 'A1B2C3D4', t: 29.5, light: 'Đủ sáng' },
    { d: daysAgo(1), start: '09:10', end: '09:40', rounds: '1', card: 'A1B2C3D4', t: 28.1, light: 'Đủ sáng', rate: 3 },
    { d: daysAgo(2), start: '20:00', end: '21:00', rounds: '2', card: 'A1B2C3D4', t: 27.4, light: 'Thiếu sáng', rate: 2 },
    { d: daysAgo(3), start: '18:30', end: '22:10', rounds: '7', card: 'A1B2C3D4', t: 27.0, light: 'Đủ sáng', rate: 3 },
    { d: daysAgo(4), start: '14:00', end: '15:30', rounds: '3', card: 'A1B2C3D4', t: 31.2, light: 'Đủ sáng', rate: 1 },
    { d: daysAgo(5), start: '19:20', end: '21:45', rounds: '5', card: 'A1B2C3D4', t: 28.6, light: 'Đủ sáng', rate: 3 },
  ];
  function renderWeek() {
    const vals = [4, 6, 3, 7, 2, 1, T.today];
    const max = Math.max(...vals, 1);
    $('[data-weekbars]').innerHTML = vals.map((v, i) => {
      const d = daysAgo(6 - i);
      const isToday = i === 6;
      return `<div class="wb${isToday ? ' today' : ''}"><span class="v">${v}</span><span class="col" style="height:${Math.round((v / max) * 110)}px"></span><span class="d">${isToday ? 'Hôm nay' : DOW_SHORT[d.getDay()]}</span></div>`;
    }).join('');
    $('[data-weekbars]').setAttribute('aria-label', `Số vòng 7 ngày qua: ${vals.join(', ')}`);
  }

  // ---------- history ----------
  let historyDrawn = false;
  let range = 30;
  const RANGE = { 7: [26, 3, 2], 30: [98, 11, 9], 90: [281, 29, 24] };
  function renderKpis() {
    const [rounds, early, rem] = RANGE[range];
    bind('rangeText', `${range} ngày gần nhất`);
    bind('kRounds', rounds);
    bind('kRoundsSub', `trung bình ${vn1(rounds / range)} vòng/ngày`);
    bind('kHours', vn1((rounds * cfg.focus) / 60));
    bind('kHoursSub', `${rounds} vòng × ${cfg.focus} phút`);
    bind('kEarly', early);
    bind('kRem', rem);
  }
  $$('[data-range]').forEach((b) => b.addEventListener('click', () => {
    range = Number(b.dataset.range);
    $$('[data-range]').forEach((x) => x.setAttribute('aria-checked', String(x === b)));
    renderKpis();
  }));
  function drawCalendar() {
    const cells = [];
    ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'].forEach((d) => cells.push(`<span class="dh">${d}</span>`));
    const first = daysAgo(29);
    const lead = (first.getDay() + 6) % 7;
    for (let i = 0; i < lead; i++) cells.push('<span class="c empty"></span>');
    for (let i = 29; i >= 0; i--) {
      const d = daysAgo(i);
      const wd = (d.getDay() + 6) % 7;
      let v = wd >= 5 ? Math.floor(rnd() * 3) : 1 + Math.floor(rnd() * 4);
      if (rnd() < 0.12) v = 0;
      if (i === 0) v = Math.min(4, T.today);
      cells.push(`<span class="c l${v}${i === 0 ? ' today' : ''}" title="${dateShort(d)}: mức ${v}">${d.getDate()}</span>`);
    }
    $('[data-cal]').innerHTML = cells.join('');
  }
  function drawHours() {
    const el = $('[data-hourbars]');
    const vals = { 6: 0, 7: 1, 8: 3, 9: 5, 10: 4, 11: 2, 12: 0, 13: 1, 14: 6, 15: 5, 16: 2, 17: 1, 18: 4, 19: 14, 20: 18, 21: 16, 22: 11, 23: 3 };
    const max = Math.max(...Object.values(vals));
    let html = '';
    for (let h = 6; h <= 23; h++) {
      html += `<div class="hb${h >= 19 && h <= 22 ? ' best' : ''}" title="${h} giờ: ${vals[h]} vòng"><span class="col" style="--v:${(vals[h] / max).toFixed(3)}"></span><span class="d">${h % 3 === 0 ? h : ''}</span></div>`;
    }
    html += '<span class="best-mark"><span class="bm-full">Khung giờ tốt nhất</span><span class="bm-short">Tốt nhất</span></span>';
    el.innerHTML = html;
    requestAnimationFrame(() => {
      const bars = $$('.hb', el);
      const a = bars[13], b = bars[16];
      const mark = $('.best-mark', el);
      const left = a.offsetLeft;
      mark.style.left = `${left}px`;
      mark.style.width = `${b.offsetLeft + b.offsetWidth - left}px`;
    });
  }
  function drawLine() {
    const svg = $('[data-linechart]');
    const X0 = 52, X1 = 590, Y0 = 16, Y1 = 192;
    const temp = [], hum = [];
    for (let i = 0; i <= 24; i++) {
      const hour = (today.getHours() - 24 + i + 24) % 24;
      const k = Math.cos(((hour - 14) / 24) * 2 * Math.PI);
      temp.push(28.4 + 2.6 * k + (rnd() - 0.5) * 0.3);
      hum.push(67 - 9 * k + (rnd() - 0.5) * 1.2);
    }
    const x = (i) => X0 + (i / 24) * (X1 - X0);
    const yT = (v) => Y1 - ((v - 24) / 10) * (Y1 - Y0);
    const yH = (v) => Y1 - ((v - 45) / 40) * (Y1 - Y0);
    let g = '';
    [26, 28, 30, 32].forEach((t, k) => {
      const y = yT(t);
      g += `<line class="grid-l" x1="${X0}" x2="${X1}" y1="${y}" y2="${y}"/>`;
      g += `<text x="${X0 - 8}" y="${y + 4}" text-anchor="end">${t}°</text>`;
      g += `<text x="${X1 + 8}" y="${y + 4}">${[53, 61, 69, 77][k]}%</text>`;
    });
    g += `<line class="axis" x1="${X0}" x2="${X1}" y1="${Y1}" y2="${Y1}"/>`;
    for (let i = 0; i <= 24; i += 6) {
      const d = new Date(today.getTime() - (24 - i) * 3600000);
      g += `<text x="${x(i)}" y="${Y1 + 26}" text-anchor="${i === 0 ? 'start' : i === 24 ? 'end' : 'middle'}">${d.getHours()} giờ</text>`;
    }
    const path = (arr, fy) => arr.map((v, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)},${fy(v).toFixed(1)}`).join(' ');
    g += `<path class="h" d="${path(hum, yH)}"/><path class="t" d="${path(temp, yT)}"/>`;
    svg.innerHTML = g;
  }
  function renderRows() {
    $('[data-rows]').innerHTML = sessions.map((s) =>
      `<tr><td>${dateShort(s.d)}</td><td>${s.start} → ${s.end}</td><td class="r">${s.rounds}</td><td>${s.card}</td><td>${vn1(s.t)} °C</td><td>${s.light}</td><td>${RATES[s.rate] || '—'}</td></tr>`).join('');
  }
  function drawHistory() {
    renderKpis();
    if (historyDrawn) { drawHours(); return; }
    historyDrawn = true;
    drawCalendar(); drawHours(); drawLine(); renderRows();
  }
  $('[data-action="export"]').addEventListener('click', () => {
    const rows = [['ngay', 'bat_dau', 'ket_thuc', 'vong', 'the', 'nhiet_do_tb', 'anh_sang', 'danh_gia']]
      .concat(sessions.map((s) => [s.d.toISOString().slice(0, 10), s.start, s.end, s.rounds, s.card, s.t, s.light, s.rate || '']));
    const blob = new Blob(['﻿' + rows.map((r) => r.join(',')).join('\n')], { type: 'text/csv;charset=utf-8' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob); a.download = 'phien-hoc.csv'; a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
    toast('Đã xuất phien-hoc.csv (dữ liệu mẫu).', { icon: 'i-download' });
  });

  // ---------- settings ----------
  let currentTab = 'account';
  function selectTab(name, focus = true) {
    if (!$(`[data-panel="${name}"]`)) name = 'account';
    currentTab = name;
    $$('[data-tab]').forEach((t) => {
      const on = t.dataset.tab === name;
      t.setAttribute('aria-selected', String(on));
      t.tabIndex = on ? 0 : -1;
      if (on && focus) t.focus();
    });
    $$('[data-panel]').forEach((p) => { p.hidden = p.dataset.panel !== name; });
  }
  $$('[data-tab]').forEach((t) => t.addEventListener('click', () => {
    history.replaceState(null, '', `#/settings/${t.dataset.tab}`);
    selectTab(t.dataset.tab);
  }));
  $('.set-nav').addEventListener('keydown', (e) => {
    const tabs = $$('[data-tab]');
    const i = tabs.findIndex((t) => t.getAttribute('aria-selected') === 'true');
    const n = ['ArrowDown', 'ArrowRight'].includes(e.key) ? 1 : ['ArrowUp', 'ArrowLeft'].includes(e.key) ? -1 : 0;
    if (!n) return;
    e.preventDefault();
    const t = tabs[(i + n + tabs.length) % tabs.length];
    history.replaceState(null, '', `#/settings/${t.dataset.tab}`);
    selectTab(t.dataset.tab);
  });
  function syncRange(r) {
    const p = ((r.value - r.min) / (r.max - r.min)) * 100;
    r.style.setProperty('--p', `${p}%`);
    const out = $(`[data-out="${r.id}"]`);
    if (out) out.textContent = `${r.value}${r.dataset.unit ? ` ${r.dataset.unit}` : ''}`;
  }
  $$('input[type="range"]').forEach((r) => { syncRange(r); r.addEventListener('input', () => syncRange(r)); });

  $('[data-panel="account"]').addEventListener('submit', (e) => {
    e.preventDefault();
    const okName = setErr($('#st-name'), RULES.name($('#st-name').value));
    const okMail = setErr($('#st-email'), RULES.email($('#st-email').value));
    if (!okName || !okMail) { (okName ? $('#st-email') : $('#st-name')).focus(); return; }
    $('.side-user-name').textContent = $('#st-name').value.trim();
    $('.avatar').textContent = $('#st-name').value.trim().split(/\s+/).pop().charAt(0).toUpperCase();
    toast('Đã lưu thông tin tài khoản.');
  });
  $('[data-panel="pomodoro"]').addEventListener('submit', (e) => {
    e.preventDefault();
    Object.assign(cfg, { focus: +$('#rg-focus').value, short: +$('#rg-short').value, long: +$('#rg-long').value, every: +$('#rg-every').value, goal: +$('#rg-goal').value });
    bind('pFocus', cfg.focus); bind('pShort', cfg.short); bind('pLong', cfg.long);
    T.round = Math.min(T.round, cfg.every);
    if (!T.running) selectPreset(T.preset);
    updatePayloadPreview(); renderCycle(); renderKpis();
    toast('Đã lưu cài đặt Pomodoro.');
  });
  $('[data-panel="alerts"]').addEventListener('submit', (e) => {
    e.preventDefault();
    Object.assign(cfg, { remind: +$('#rg-remind').value, hot: +$('#rg-hot').value, dark: +$('#rg-dark').value });
    renderEnv(); renderSession();
    toast('Đã lưu cài đặt cảnh báo.');
  });

  let cards = [{ uid: 'A1B2C3D4', name: 'Thẻ sinh viên' }];
  function renderCards() {
    $('[data-cards]').innerHTML = cards.map((c, i) =>
      `<li><span class="uid">${esc(c.uid)}</span><span class="name">${esc(c.name)}</span><button type="button" class="btn btn-danger-ghost" data-remove="${i}" aria-label="Xóa thẻ ${esc(c.uid)}">Xóa</button></li>`).join('')
      || '<li class="waiting">Chưa có thẻ nào. Thêm thẻ để bắt đầu phiên học bằng cách quẹt.</li>';
  }
  $('[data-cards]').addEventListener('click', (e) => {
    const b = e.target.closest('[data-remove]');
    if (!b) return;
    const i = Number(b.dataset.remove);
    const [removed] = cards.splice(i, 1);
    renderCards();
    toast(`Đã xóa thẻ ${esc(removed.uid)}.`, { action: { label: 'Hoàn tác', fn: () => { cards.splice(i, 0, removed); renderCards(); } }, ms: 6000 });
  });
  $('[data-action="add-card"]').addEventListener('click', (e) => {
    const btn = e.currentTarget;
    btn.disabled = true;
    const li = document.createElement('li');
    li.className = 'waiting';
    li.textContent = 'Đang chờ thẻ… hãy quẹt thẻ lên mặt hộp.';
    $('[data-cards]').append(li);
    setTimeout(() => {
      const uid = Array.from({ length: 4 }, () => Math.floor(Math.random() * 256).toString(16).padStart(2, '0')).join('').toUpperCase();
      cards.push({ uid, name: `Thẻ ${cards.length + 1}` });
      renderCards();
      btn.disabled = false;
      toast(`Đã thêm thẻ ${uid}.`, { icon: 'i-card' });
    }, 2000);
  });

  // ---------- boot ----------
  log('in', payload('study/rfid', { uid: 'A1B2C3D4', action: 'start' }).replace('←', '→'), sess.start, false);
  log('out', payload('study/lcd', { text: 'On tap chuong 3' }), lcdSent.at, false);
  log('tg', 'Nhắc nghỉ: đã học 50 phút liên tục', sess.start + 50 * 60000, false);
  log('out', payload('study/timer', { minutes: 25 }), now0 - (6 * 60 + 18) * 1000, false);

  renderEnv();
  renderSession();
  renderCycle();
  updatePayloadPreview();
  renderLcd();
  renderLcdShown();
  renderWeek();
  renderCards();
  tickClock();
  route();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(drawSquares);
  let rT;
  window.addEventListener('resize', () => { clearTimeout(rT); rT = setTimeout(() => { drawSquares(); if (historyDrawn && document.body.dataset.screen === 'history') drawHours(); }, 120); });

  setInterval(() => { renderTimer(); renderSession(); }, 250);
  setInterval(tickClock, 1000);
  setInterval(stepEnv, 4000);
  if (new URLSearchParams(location.search).get('demo') === 'rate') $('[data-action="tap"]').click();
})();
