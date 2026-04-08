/* Smart Bus Stop — Frontend Logic */

let currentDifficulty = 'medium';
let autoRunInterval = null;

function updateClock() {
  const now = new Date();
  document.getElementById('clock').textContent =
    now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}
setInterval(updateClock, 1000);
updateClock();

document.querySelectorAll('.seg').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.seg').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentDifficulty = btn.dataset.d;
  });
});

document.getElementById('btnReset').addEventListener('click', async () => {
  stopAutoRun();
  document.getElementById('historyBody').innerHTML = '';
  document.getElementById('notifList').innerHTML =
    '<div class="notif-item info">Environment reset. Ready.</div>';
  const res = await fetch('/api/reset', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ difficulty: currentDifficulty }),
  });
  const data = await res.json();
  updateUI(data.state, 0, { step: 0 });
});

document.querySelectorAll('.action-btn').forEach(btn => {
  btn.addEventListener('click', () => doStep(btn.dataset.action));
});

document.getElementById('btnAuto').addEventListener('click', autoStep);

document.getElementById('btnAutoRun').addEventListener('click', () => {
  if (autoRunInterval) { stopAutoRun(); return; }
  let count = 0;
  document.getElementById('btnAutoRun').textContent = '⏹ Stop';
  autoRunInterval = setInterval(async () => {
    const res = await fetch('/api/auto_step', { method: 'POST' });
    const data = await res.json();
    handleStepResponse(data);
    count++;
    if (data.done || count >= 10) stopAutoRun();
  }, 600);
});

function stopAutoRun() {
  if (autoRunInterval) { clearInterval(autoRunInterval); autoRunInterval = null; }
  document.getElementById('btnAutoRun').textContent = '⚡ Run 10 Steps';
}

async function doStep(action) {
  highlightAction(action);
  const res = await fetch('/api/step', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action }),
  });
  const data = await res.json();
  handleStepResponse(data);
}

async function autoStep() {
  const res = await fetch('/api/auto_step', { method: 'POST' });
  const data = await res.json();
  highlightAction(data.action);
  handleStepResponse(data);
}

function handleStepResponse(data) {
  updateUI(data.state, data.reward, data.info);
  addHistoryRow(data);
  if (data.done) {
    addNotification('🏁 Episode complete! Check your score.', 'info');
    stopAutoRun();
  }
}

function updateUI(state, reward, info) {
  const crowd = state.crowd_size;
  document.getElementById('crowdVal').textContent = crowd;
  document.getElementById('waitVal').textContent = state.avg_waiting_time.toFixed(1);
  document.getElementById('inflowVal').textContent = state.passenger_inflow_rate.toFixed(1);
  document.getElementById('etaVal').textContent = state.bus_arrival_eta.toFixed(1);
  document.getElementById('stepNum').textContent = (info && info.step) ? info.step : 0;
  document.getElementById('lastReward').textContent = reward ? reward.toFixed(2) : '0.00';

  document.getElementById('statCrowd').classList.toggle('alert', crowd > 40);
  document.getElementById('statWait').classList.toggle('alert', state.avg_waiting_time > 10);

  renderCrowd(crowd);

  if (info && info.action === 'send_bus') {
    const bus = document.getElementById('busIcon');
    bus.classList.remove('arriving');
    void bus.offsetWidth;
    bus.classList.add('arriving');
  }

  fetch('/api/grade').then(r => r.json()).then(g => {
    setMeter('mEfficiency', 'mEffVal', g.efficiency_score);
    setMeter('mCrowd', 'mCrowdVal', g.crowd_control_score);
    setMeter('mComm', 'mCommVal', g.communication_score);
    document.getElementById('overallScore').textContent = g.overall_score.toFixed(3);
  });

  if (state.last_notification) {
    addNotification(state.last_notification, notifType(info ? info.action : '', crowd));
  }
}

function setMeter(fillId, valId, score) {
  document.getElementById(fillId).style.width = (score * 100).toFixed(1) + '%';
  document.getElementById(valId).textContent = (score * 100).toFixed(0) + '%';
}

function renderCrowd(count) {
  const display = document.getElementById('crowdDisplay');
  display.innerHTML = '';
  const show = Math.min(count, 20);
  const icons = ['🧍', '🧍‍♀️', '🧍‍♂️'];
  for (let i = 0; i < show; i++) {
    const span = document.createElement('span');
    span.className = 'person-icon';
    span.textContent = icons[i % icons.length];
    display.appendChild(span);
  }
  if (count > 20) {
    const more = document.createElement('span');
    more.className = 'person-icon';
    more.style.fontSize = '0.65rem';
    more.style.color = '#f5c842';
    more.textContent = `+${count - 20}`;
    display.appendChild(more);
  }
}

function addNotification(msg, type) {
  const list = document.getElementById('notifList');
  const item = document.createElement('div');
  item.className = 'notif-item ' + (type || 'info');
  item.textContent = msg;
  list.prepend(item);
  while (list.children.length > 8) list.removeChild(list.lastChild);
}

function notifType(action, crowd) {
  if (action === 'send_bus') return 'success';
  if (action === 'delay_bus') return 'warning';
  if (crowd > 40) return 'danger';
  return 'info';
}

function highlightAction(action) {
  document.querySelectorAll('.action-btn').forEach(b => b.classList.remove('active-action'));
  const btn = document.querySelector(`.action-btn[data-action="${action}"]`);
  if (btn) btn.classList.add('active-action');
}

function addHistoryRow(data) {
  const tbody = document.getElementById('historyBody');
  const s = data.state;
  const action = (data.info && data.info.action) ? data.info.action : (data.action || '');
  const step = (data.info && data.info.step) ? data.info.step : 0;
  const tr = document.createElement('tr');
  tr.innerHTML =
    `<td>${step}</td>` +
    `<td><span class="badge ${action}">${action}</span></td>` +
    `<td>${s.crowd_size}</td>` +
    `<td>${s.avg_waiting_time.toFixed(1)}</td>` +
    `<td>${s.bus_arrival_eta.toFixed(1)}</td>` +
    `<td style="color:${data.reward >= 0 ? '#2ecc71' : '#e74c3c'}">${data.reward.toFixed(2)}</td>` +
    `<td>${(data.score || 0).toFixed(3)}</td>`;
  tbody.prepend(tr);
  while (tbody.children.length > 50) tbody.removeChild(tbody.lastChild);
}

fetch('/api/state').then(r => r.json()).then(state => {
  updateUI(state, 0, { step: 0 });
}).catch(() => {});
