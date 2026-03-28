// API helper
const API = {
  async get(url) { const r = await fetch(url); return r.json(); },
  async post(url, data) { const r = await fetch(url, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data) }); const j = await r.json(); if (!r.ok) throw j; return j; },
  async put(url, data) { const r = await fetch(url, { method:'PUT', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data) }); return r.json(); },
  async del(url) { const r = await fetch(url, { method:'DELETE' }); return r.json(); },
  async upload(file) {
    const fd = new FormData(); fd.append('photo', file);
    const r = await fetch('/api/upload', { method:'POST', body:fd }); return r.json();
  },
  async uploadScan(url, file, userId, geo) {
    const fd = new FormData();
    fd.append('photo', file);
    fd.append('userId', userId);
    if (geo) { fd.append('lat', geo.lat); fd.append('lon', geo.lon); }
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort(), 13000000);
    try {
      const r = await fetch(url, { method:'POST', body:fd, signal:ctrl.signal });
      clearTimeout(t);
      const j = await r.json();
      if (!r.ok) throw j;
      return j;
    } catch(e) { clearTimeout(t); throw e.name==='AbortError' ? {error:'Request timeout'} : e; }
  }
};
