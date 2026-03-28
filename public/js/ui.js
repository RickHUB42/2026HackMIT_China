// UI: panels, cards, registration, login, shop, ranking, tasks, settings, deco bar

const AVATARS = ['man.png','woman.png','noddle.png','rice.png','tree.png'];
let avatarPickerTarget = null;
let selectedGender = 'Male';
let selectedAvatar = 'man.png';

// --- Panels ---
function openPanel(name) {
  document.getElementById(name + 'Panel').classList.remove('hidden');
  if (name === 'shop') loadShop();
  if (name === 'ranking') loadRanking('carbon');
  if (name === 'tasks') loadTasks();
  if (name === 'settings') loadSettings();
  if (name === 'recipe') { loadSavedRecipes(); loadDeliveryItems(); }
}
function closePanel(name) { document.getElementById(name + 'Panel').classList.add('hidden'); }

// --- Info Cards ---
function toggleCard(side) {
  const el = document.getElementById(side === 'left' ? 'cardLeft' : 'cardRight');
  el.classList.toggle('open');
}
function switchRightTab(tab) {
  document.querySelectorAll('.card-tab-btn').forEach(b => b.classList.toggle('active', b.dataset.tab === tab));
  document.getElementById('nutritionCard').classList.toggle('hidden', tab !== 'nutrition');
  document.getElementById('treeStatusCard').classList.toggle('hidden', tab !== 'treestatus');
}

// --- Register ---
function showRegisterPanel() {
  document.getElementById('loginPanel').classList.add('hidden');
  document.getElementById('registerPanel').classList.remove('hidden');
}
function showLoginPanel() {
  document.getElementById('registerPanel').classList.add('hidden');
  document.getElementById('loginPanel').classList.remove('hidden');
}
function selectGender(btn) {
  document.querySelectorAll('.gender-btn').forEach(b => b.classList.remove('selected'));
  btn.classList.add('selected');
  selectedGender = btn.dataset.g;
}
async function doRegister() {
  const name = document.getElementById('regName').value.trim();
  const email = document.getElementById('regEmail').value.trim();
  if (!name) return alert('Please enter your name');
  const res = await API.post('/api/register', { username: name, email, gender: selectedGender, avatar: selectedAvatar });
  if (res.id) {
    localStorage.setItem('userId', res.id);
    document.getElementById('registerPanel').classList.add('hidden');
    App.init();
  }
}
async function doLogin() {
  const email = document.getElementById('loginEmail').value.trim();
  const code = document.getElementById('loginCode').value.trim();
  if (!email || !code) return alert('Please enter email and code');
  try {
    const res = await API.post('/api/login', { email, code });
    localStorage.setItem('userId', res.id);
    document.getElementById('loginPanel').classList.add('hidden');
    App.init();
  } catch (e) {
    alert(e.error || 'Login failed');
  }
}

// --- Avatar Picker ---
function showAvatarPicker(target) {
  avatarPickerTarget = target;
  const grid = document.getElementById('avatarGrid');
  grid.innerHTML = '';
  AVATARS.forEach(a => {
    const img = document.createElement('img');
    img.src = `/img/UI/head/${a}`;
    img.onclick = () => pickAvatar(a);
    grid.appendChild(img);
  });
  document.getElementById('avatarPicker').classList.remove('hidden');
}
async function pickAvatar(a) {
  selectedAvatar = a;
  document.getElementById('avatarPicker').classList.add('hidden');
  if (avatarPickerTarget === 'reg') {
    document.getElementById('regAvatarPreview').src = `/img/UI/head/${a}`;
  } else if (avatarPickerTarget === 'settings' && Game.user) {
    await API.put(`/api/user/${Game.user.id}`, { avatar: a });
    document.getElementById('settingsAvatarImg').src = `/img/UI/head/${a}`;
    Game.user.avatar = a;
  }
}

// --- Shop ---
async function loadShop() {
  const items = await API.get('/api/shop/items');
  const list = document.getElementById('shopList');
  list.innerHTML = '<div class="shop-grid">' + items.map(it => `
    <div class="shop-item" onclick="buyItem('${it.name}')">
      <img src="${it.image}"><p>${it.name}</p><p class="price">💰 ${it.price}</p>
    </div>`).join('') + '</div>';
}
async function buyItem(name) {
  if (!Game.user) return;
  const res = await API.post('/api/shop/buy', { userId: Game.user.id, itemName: name });
  if (res.ok) { await App.refreshUser(); showToast('Purchased!'); }
  else showToast(res.error || 'Failed');
}

// --- Ranking ---
async function loadRanking(type) {
  document.querySelectorAll('.rank-tab').forEach(b => b.classList.toggle('active', b.textContent.toLowerCase() === type));
  const rows = await API.get(`/api/ranking/${type}`);
  const list = document.getElementById('rankingList');
  list.innerHTML = rows.map((r, i) => `
    <div class="rank-row">
      <img src="/img/UI/head/${r.avatar || 'man.png'}">
      <div class="rank-info"><strong>${r.username}</strong><br><small>Carbon: ${r.carbon_emission}, Nutrition: ${r.nutrition_score}</small></div>
      <div class="rank-num">No.${i + 1}</div>
    </div>`).join('');
  if (Game.user) {
    const self = document.getElementById('rankingSelf');
    const rank = rows.findIndex(r => r.id === Game.user.id);
    self.innerHTML = `<div class="rank-row"><img src="/img/UI/head/${Game.user.avatar}"><div class="rank-info"><strong>${Game.user.username}</strong><br><small>Carbon: ${Game.user.carbon_emission}, Nutrition: ${Game.user.nutrition_score}</small></div><div class="rank-num">No.${rank >= 0 ? rank + 1 : '?'}</div></div>`;
  }
}

// --- Tasks (scan history) ---
async function loadTasks() {
  if (!Game.user) return;
  const [scans, achievements] = await Promise.all([
    API.get(`/api/user/${Game.user.id}/scans`),
    API.get(`/api/user/${Game.user.id}/achievements`)
  ]);
  const list = document.getElementById('tasksList');
  let html = '';
  // Scan history as blue-bordered packs
  if (scans.length) {
    html += '<h3 style="padding:8px;color:#333;">Scan History</h3>';
    scans.forEach(s => {
      const isSummary = s.mode === 'summary';
      html += `<div class="scan-pack ${isSummary ? 'scan-summary' : 'scan-suggestion'}">
        <span class="scan-mode">${isSummary ? '📊' : '🍳'} ${s.mode}</span>
        <small>${s.created_at}</small>
        ${s.carbon_total ? `<span class="scan-carbon">${s.carbon_total.toFixed(4)} CO₂</span>` : ''}
      </div>`;
    });
  }
  // Achievements
  if (achievements.length) {
    html += '<h3 style="padding:8px;color:#333;">Achievements</h3>';
    html += achievements.map(t => `<div class="task-row">${t.title}<br><small>${t.achieved_at}</small></div>`).join('');
  }
  list.innerHTML = html || '<p class="empty-msg">No tasks yet</p>';
}

// --- Settings ---
function loadSettings() {
  if (!Game.user) return;
  document.getElementById('settingsAvatarImg').src = `/img/UI/head/${Game.user.avatar}`;
  document.getElementById('settingsName').textContent = Game.user.username;
  document.getElementById('settingsId').textContent = Game.user.id;
  document.getElementById('settingsEmail').textContent = Game.user.email || 'Not set';
  document.getElementById('settingsCE').textContent = Game.user.carbon_emission;
  document.getElementById('settingsNS').textContent = Game.user.nutrition_score;
}
async function changeName() {
  const name = prompt('Enter new name:');
  if (!name || !Game.user) return;
  await API.put(`/api/user/${Game.user.id}`, { username: name });
  Game.user.username = name;
  loadSettings();
}
async function sendVerification(ctx, btn) {
  let email;
  if (ctx === 'login') email = document.getElementById('loginEmail').value.trim();
  else if (ctx === 'switch') email = document.getElementById('settingsSwitchEmail').value.trim();
  else email = Game.user && Game.user.email;
  if (!email) return alert('Please enter email first');
  try {
    await API.post('/api/send-code', { email });
    if (btn) {
      btn.disabled = true;
      let sec = 60;
      const orig = btn.textContent;
      btn.textContent = sec + 's';
      const t = setInterval(() => { if (--sec <= 0) { clearInterval(t); btn.disabled = false; btn.textContent = orig; } else btn.textContent = sec + 's'; }, 1000);
    }
  } catch (e) {
    alert(e.error || 'Failed to send code');
  }
}

async function confirmEmailCode(btn) {
  const code = document.getElementById('settingsVerifyCode').value.trim();
  const email = Game.user && Game.user.email;
  if (!email || !code) return alert('Please enter the code');
  try {
    await API.post('/api/verify-email', { email, code });
    btn.textContent = 'Authorized';
    btn.disabled = true;
    btn.style.background = '#888';
  } catch (e) {
    alert(e.error || 'Invalid or expired code');
  }
}

function logoutAccount() {
  if (!confirm('Are you sure you want to log out?')) return;
  localStorage.removeItem('userId');
  closePanel('settings');
  location.reload();
}

// --- Recipe Panel: Saved Recipes / Delivery tabs ---
function switchRecipeTab(tab) {
  document.querySelectorAll('.recipe-tab').forEach(b => b.classList.toggle('active', b.textContent.toLowerCase().includes(tab)));
  document.getElementById('recipeSavedList').classList.toggle('hidden', tab !== 'saved');
  document.getElementById('recipeDeliveryList').classList.toggle('hidden', tab !== 'delivery');
}

async function loadSavedRecipes() {
  if (!Game.user) return;
  const recipes = await API.get(`/api/user/${Game.user.id}/recipes`);
  const el = document.getElementById('recipeSavedList');
  if (!recipes.length) { el.innerHTML = '<p class="empty-msg">No saved recipes. Use Suggestion Mode to discover recipes!</p>'; return; }
  el.innerHTML = recipes.map(r => `
    <div class="saved-recipe">
      <h4>${r.title}</h4>
      <p class="recipe-ing">${r.ingredients}</p>
      <button class="btn-del" onclick="deleteRecipe(${r.id})">✕</button>
    </div>`).join('');
}

async function deleteRecipe(rid) {
  if (!Game.user) return;
  await API.del(`/api/user/${Game.user.id}/recipes/${rid}`);
  loadSavedRecipes();
}

async function loadDeliveryItems() {
  const items = await API.get('/api/delivery/items');
  const el = document.getElementById('recipeDeliveryList');
  if (!items.length) { el.innerHTML = '<p class="empty-msg">No delivery items</p>'; return; }
  el.innerHTML = '<div class="delivery-list">' + items.map((it, i) => `
    <div class="delivery-row">
      <span class="delivery-num">${i + 1}</span>
      <img src="${it.image}" alt="${it.name}">
      <span class="delivery-name">${it.name}</span>
    </div>`).join('') + '</div><p class="delivery-note">Sorted by environmental friendliness</p>';
}

// --- Deco Bar ---
async function openDecoBar() {
  if (!Game.user) return;
  document.getElementById('bottomBar').classList.add('hidden');
  document.getElementById('decoBar').classList.remove('hidden');
  const decos = await API.get(`/api/user/${Game.user.id}/decorations`);
  const allItems = await API.get('/api/shop/items');
  const list = document.getElementById('decoBarList');
  list.innerHTML = '';
  allItems.forEach(it => {
    const owned = decos.find(d => d.item_name === it.name);
    const qty = owned ? owned.quantity : 0;
    const slot = document.createElement('div');
    slot.className = 'deco-slot' + (qty === 0 ? ' empty' : '');
    slot.innerHTML = `<img src="${it.image}"><span class="deco-qty">${qty}</span>`;
    if (qty > 0) {
      slot.draggable = true;
      slot.addEventListener('dragstart', (e) => e.dataTransfer.setData('text', it.name));
      slot.addEventListener('touchstart', (e) => startDecoDrag(it.name, e), { passive: false });
    }
    list.appendChild(slot);
  });
}
function closeDecoBar() {
  document.getElementById('decoBar').classList.add('hidden');
  document.getElementById('bottomBar').classList.remove('hidden');
}

// Deco drag-to-tree
let draggingDeco = null;
function startDecoDrag(name, e) {
  draggingDeco = name;
  const drag = document.getElementById('dragItem');
  drag.src = `/img/Decos/${name}.png`;
  drag.classList.remove('hidden');
  document.addEventListener('touchmove', onDecoDragMove, { passive: false });
  document.addEventListener('touchend', onDecoDrop);
}
function onDecoDragMove(e) {
  e.preventDefault();
  const drag = document.getElementById('dragItem');
  drag.style.left = (e.touches[0].clientX - 20) + 'px';
  drag.style.top = (e.touches[0].clientY - 20) + 'px';
}
async function onDecoDrop(e) {
  document.removeEventListener('touchmove', onDecoDragMove);
  document.removeEventListener('touchend', onDecoDrop);
  document.getElementById('dragItem').classList.add('hidden');
  if (!draggingDeco || !Game.user) return;
  const ga = document.getElementById('gameArea');
  const rect = ga.getBoundingClientRect();
  const cx = (e.changedTouches ? e.changedTouches[0].clientX : e.clientX);
  const cy = (e.changedTouches ? e.changedTouches[0].clientY : e.clientY);
  const x = ((cx - rect.left) / rect.width) * 100;
  const y = ((cy - rect.top) / rect.height) * 100;
  if (x >= 0 && x <= 100 && y >= 0 && y <= 100) {
    await API.post(`/api/user/${Game.user.id}/place-deco`, { itemName: draggingDeco, x, y });
    Game.loadPlacedDecos();
    openDecoBar();
  }
  draggingDeco = null;
}

// Desktop drag & drop for decos
document.addEventListener('DOMContentLoaded', () => {
  const ga = document.getElementById('gameArea');
  ga.addEventListener('dragover', e => e.preventDefault());
  ga.addEventListener('drop', async (e) => {
    e.preventDefault();
    const name = e.dataTransfer.getData('text');
    if (!name || !Game.user) return;
    const rect = ga.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    await API.post(`/api/user/${Game.user.id}/place-deco`, { itemName: name, x, y });
    Game.loadPlacedDecos();
    openDecoBar();
  });
});

// --- Nutrition bars ---
function renderNutritionBars(data) {
  const nutrients = ['protein','fat','carbohydrate','fiber','calcium','iron','zinc','vitamin_a','vitamin_c','vitamin_d'];
  const container = document.getElementById('nutritionBars');
  if (!data || !data.length) { container.innerHTML = '<p class="empty-msg">No data</p>'; return; }
  const d = data[0];
  container.innerHTML = nutrients.map(n => {
    const val = d[n] || 0;
    const max = 100;
    const pct = Math.min(100, (val / max) * 100);
    return `<div class="nutri-bar"><label>${n}: ${val.toFixed(1)}</label><div class="nutri-bar-track"><div class="nutri-bar-fill" style="width:${pct}%"></div></div></div>`;
  }).join('');
}

// --- Tree status + CE ---
const TREE_REQ = [{ w:1,f:0 },{ w:2,f:1 },{ w:6,f:2 },{ w:12,f:4 }];
function renderTreeStatus(user) {
  const container = document.getElementById('treeProgress');
  if (user.tree_stage >= 4) {
    container.innerHTML = '<p>🌳 Tree fully grown!</p>';
  } else {
    const req = TREE_REQ[user.tree_stage];
    container.innerHTML = `
      <div class="tree-prog"><div class="tree-prog-label">Water: ${user.water_count}/${req.w}</div><div class="tree-prog-track"><div class="tree-prog-fill" style="width:${(user.water_count/req.w)*100}%"></div></div></div>
      <div class="tree-prog"><div class="tree-prog-label">Fertilize: ${user.fertilize_count}/${req.f}</div><div class="tree-prog-track"><div class="tree-prog-fill" style="width:${req.f?((user.fertilize_count/req.f)*100):100}%"></div></div></div>
      <p>Stage: ${user.tree_stage + 1} → ${user.tree_stage + 2}</p>`;
  }
  document.getElementById('ceDisplay').textContent = `${user.carbon_emission} kg CO₂`;
}

// --- Cooldown timer ---
function updateCooldown(user) {
  const badge = document.getElementById('waterCooldown');
  if (!user.last_water_time) { badge.classList.add('hidden'); return; }
  const diff = Date.now() - new Date(user.last_water_time).getTime();
  const remaining = 4 * 3600 * 1000 - diff;
  if (remaining <= 0 || user.water_today >= 3) { badge.classList.add('hidden'); return; }
  badge.classList.remove('hidden');
  const mins = Math.ceil(remaining / 60000);
  const h = Math.floor(mins / 60);
  const m = mins % 60;
  badge.textContent = `${h}:${String(m).padStart(2,'0')}`;
}

// --- Recipe list (today's meals) ---
async function loadRecipeList() {
  if (!Game.user) return;
  const meals = await API.get(`/api/user/${Game.user.id}/meals`);
  const el = document.getElementById('recipeListContent');
  if (!meals.length) { el.innerHTML = '<p>No meals recorded today</p>'; return; }
  el.innerHTML = meals.map(m => `<div style="padding:4px 0;border-bottom:1px solid rgba(255,255,255,0.2);">${m.meal_name} - ${m.carbon_footprint.toFixed(3)} CO₂</div>`).join('');
}
