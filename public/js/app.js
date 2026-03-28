// In-game toast notification
let _toastTimer;
function showToast(msg, ms = 2500) {
  const el = document.getElementById('gameToast');
  el.textContent = msg;
  el.classList.remove('hidden');
  el.classList.add('show');
  clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => { el.classList.remove('show'); setTimeout(() => el.classList.add('hidden'), 300); }, ms);
}

// Main app entry
const App = {
  async init() {
    DayNight.init();
    Clouds.init();

    const userId = localStorage.getItem('userId');
    if (!userId) {
      document.getElementById('registerPanel').classList.remove('hidden');
      return;
    }
    try {
      const user = await API.get(`/api/user/${userId}`);
      if (!user || user.error) { document.getElementById('registerPanel').classList.remove('hidden'); return; }
      Game.user = user;
      this.applyUser(user);
      // Daily settle
      await API.post(`/api/user/${userId}/settle`).catch(() => {});
      await this.refreshUser();
    } catch {
      document.getElementById('registerPanel').classList.remove('hidden');
    }
  },

  applyUser(user) {
    Game.updateTree(user.tree_stage || 0);
    document.getElementById('currencyVal').textContent = user.currency;
    renderTreeStatus(user);
    updateCooldown(user);
    Game.loadPlacedDecos();
    loadRecipeList();
    this.loadNutrition();
  },

  async refreshUser() {
    if (!Game.user) return;
    const user = await API.get(`/api/user/${Game.user.id}`);
    Game.user = user;
    this.applyUser(user);
  },

  async loadNutrition() {
    if (!Game.user) return;
    const data = await API.get(`/api/user/${Game.user.id}/nutrition`);
    renderNutritionBars(data);
  }
};

// Cooldown timer update
setInterval(() => { if (Game.user) updateCooldown(Game.user); }, 30000);

// Scale #mainPage to fit viewport proportionally
function scaleApp() {
  const el = document.getElementById('mainPage');
  const W = 420, H = 750;
  const vw = window.innerWidth, vh = window.innerHeight;
  const s = Math.min(vw / W, vh / H);
  if (vw <= 480) { el.style.transform = ''; el.style.width = '100vw'; el.style.height = '100vh'; return; }
  el.style.width = W + 'px';
  el.style.height = H + 'px';
  el.style.transform = s < 1 ? `scale(${s})` : (s > 1 ? `scale(${s})` : '');
  el.style.transformOrigin = 'center center';
}
window.addEventListener('resize', scaleApp);

document.addEventListener('DOMContentLoaded', () => { scaleApp(); App.init(); });
