// Game logic: tree stages, watering, fertilizing, decorations
const STAGE_IMG = { 0:1, 1:2, 2:3, 3:4 };
const TREE_SIZES = { 1:{h:7,b:16}, 2:{h:18,b:11}, 3:{h:60,b:12}, 4:{h:84,b:8} };
const Game = {
  user: null,
  actionMode: null,
  _inTreeZone: false,
  _clickTimer: null,
  updateTree(stage) {
    const s = Math.max(0, Math.min(3, stage || 0));
    const img = STAGE_IMG[s];
    const sz = TREE_SIZES[img];
    ['treeLight','treeDark'].forEach(id => {
      const el = document.getElementById(id);
      el.src = `/img/Tree/Tree_Stage${img}_${id.includes('Light')?'Light':'Dark'}.png`;
      el.style.height = sz.h + '%';
      el.style.bottom = sz.b + '%';
      el.classList.remove('hidden');
    });
  },
  async loadPlacedDecos() {
    if (!this.user) return;
    const decos = await API.get(`/api/user/${this.user.id}/placed-decos`);
    const container = document.getElementById('placedDecos');
    container.innerHTML = '';
    decos.forEach(d => {
      const img = document.createElement('img');
      img.className = 'placed-deco';
      img.src = `/img/Decos/${d.item_name}.png`;
      img.style.left = d.x + '%';
      img.style.top = d.y + '%';
      container.appendChild(img);
    });
  },
  isInTreeZone(clientX, clientY) {
    const treeEl = document.getElementById('treeLight');
    const rect = treeEl.getBoundingClientRect();
    const pad = 20;
    return clientX >= rect.left - pad && clientX <= rect.right + pad &&
           clientY >= rect.top - pad && clientY <= rect.bottom + pad;
  },
  startAction(type, e) {
    if (!this.user) return;
    if (this.actionMode) { this.cancelAction(); return; }
    this.actionMode = type;
    this._inTreeZone = false;
    const drag = document.getElementById('dragItem');
    drag.src = type === 'water' ? '/img/items/watering-can.png' : '/img/items/fertilizer.png';
    // Spawn at pointer position
    const sx = e ? (e.touches ? e.touches[0].clientX : e.clientX) : window.innerWidth / 2;
    const sy = e ? (e.touches ? e.touches[0].clientY : e.clientY) : window.innerHeight / 2;
    drag.style.left = (sx - 30) + 'px';
    drag.style.top = (sy - 30) + 'px';
    drag.classList.remove('hidden', 'highlight');
    let moved = false;
    const onMove = (e) => {
      moved = true;
      const x = e.touches ? e.touches[0].clientX : e.clientX;
      const y = e.touches ? e.touches[0].clientY : e.clientY;
      drag.style.left = (x - 30) + 'px';
      drag.style.top = (y - 30) + 'px';
      const inZone = Game.isInTreeZone(x, y);
      drag.classList.toggle('highlight', inZone);
      document.getElementById('treeLight').classList.toggle('drop-hover', inZone);
      document.getElementById('treeDark').classList.toggle('drop-hover', inZone);
      if (e.touches) e.preventDefault();
    };
    const cleanup = () => {
      Game.actionMode = null;
      drag.classList.add('hidden');
      drag.classList.remove('highlight');
      document.getElementById('treeLight').classList.remove('drop-hover');
      document.getElementById('treeDark').classList.remove('drop-hover');
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('touchmove', onMove);
      document.removeEventListener('mouseup', onDrop);
      document.removeEventListener('touchend', onDrop);
    };
    const onDrop = async (e) => {
      if (!Game.actionMode) return;
      if (!moved) return; 
      const savedType = Game.actionMode;
      const cx = e.clientX || (e.changedTouches && e.changedTouches[0].clientX) || 0;
      const cy = e.clientY || (e.changedTouches && e.changedTouches[0].clientY) || 0;
      const inZone = Game.isInTreeZone(cx, cy);
      cleanup();
      if (!inZone) return;
      try {
        await API.post(`/api/user/${Game.user.id}/${savedType === 'water' ? 'water' : 'fertilize'}`);
      } catch (err) {
        const msg = err && err.error ? err.error : 'Action failed';
        showToast(msg);
        return;
      }
      const anime = document.getElementById('actionAnime');
      anime.src = (savedType === 'water' ? '/img/Anime/Watering.gif' : '/img/Anime/Fertilize.gif') + '?t=' + Date.now();
      anime.style.left = (cx - 60) + 'px';
      anime.style.top = (cy - 60) + 'px';
      anime.classList.remove('hidden');
      setTimeout(() => anime.classList.add('hidden'), 2000);
      await App.refreshUser();
    };
    document.addEventListener('mousemove', onMove);
    document.addEventListener('touchmove', onMove, { passive: false });
    setTimeout(() => {
      document.addEventListener('mouseup', onDrop);
      document.addEventListener('touchend', onDrop);
    }, 0);
  },
  cancelAction() {
    this.actionMode = null;
    this._inTreeZone = false;
    if (this._clickTimer) { clearTimeout(this._clickTimer); this._clickTimer = null; }
    const drag = document.getElementById('dragItem');
    drag.classList.add('hidden');
    drag.classList.remove('highlight');
    document.getElementById('treeLight').classList.remove('drop-hover');
    document.getElementById('treeDark').classList.remove('drop-hover');
  }
};
function startAction(type, e) { Game.startAction(type, e); }