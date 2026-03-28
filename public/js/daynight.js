// Day/Night system synced
const DayNight = {
  init() {
    this.sky = document.getElementById('skyGradient');
    this.bgLight = document.getElementById('bgLight');
    this.bgDark = document.getElementById('bgDark');
    this.treeLight = document.getElementById('treeLight');
    this.treeDark = document.getElementById('treeDark');
    this.sun = document.getElementById('sunImg');
    this.moon = document.getElementById('moonImg');
    this.timeEl = document.getElementById('timeDisplay');
    this.update();
    setInterval(() => this.update(), 30000); // every 30s
  },

  getBeijingTime() {
    const now = new Date();
    const utc = now.getTime() + now.getTimezoneOffset() * 60000;
    return new Date(utc + 8 * 3600000);
  },

  update() {
    const bj = this.getBeijingTime();
    const h = bj.getHours();
    const m = bj.getMinutes();
    const t = h + m / 60; // decimal hours

    // Display time
    this.timeEl.textContent = `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}`;

    // Sunrise 5-7, Sunset 17-19
    let dayFactor;
    if (t >= 7 && t <= 17) dayFactor = 1;
    else if (t <= 5 || t >= 19) dayFactor = 0;
    else if (t > 5 && t < 7) dayFactor = (t - 5) / 2;
    else dayFactor = 1 - (t - 17) / 2;

    const dayColor = [135, 206, 235]; // light blue
    const nightColor = [15, 15, 45];  // dark blue
    const r = Math.round(nightColor[0] + (dayColor[0] - nightColor[0]) * dayFactor);
    const g = Math.round(nightColor[1] + (dayColor[1] - nightColor[1]) * dayFactor);
    const b = Math.round(nightColor[2] + (dayColor[2] - nightColor[2]) * dayFactor);
    this.sky.style.background = `linear-gradient(180deg, rgb(${r},${g},${b}) 0%, rgb(${Math.round(r*0.7)},${Math.round(g*0.8)},${Math.round(b*0.9)}) 100%)`;

    this.bgLight.style.opacity = dayFactor;
    this.bgDark.style.opacity = 1 - dayFactor;
    this.treeLight.style.opacity = dayFactor;
    this.treeDark.style.opacity = 1 - dayFactor;

    const gameArea = document.getElementById('gameArea');
    const w = gameArea.offsetWidth;
    const h2 = gameArea.offsetHeight;

    // Sun visible 5:00-19:00
    if (t >= 5 && t <= 19) {
      const sunProgress = (t - 5) / 14;
      const sx = sunProgress * (w - 80);
      const sy = h2 * 0.05 + Math.sin(sunProgress * Math.PI) * (-h2 * 0.25);
      this.sun.style.left = sx + 'px';
      this.sun.style.top = (h2 * 0.3 - Math.sin(sunProgress * Math.PI) * h2 * 0.25) + 'px';
      this.sun.style.opacity = Math.min(1, dayFactor * 2);
    } else {
      this.sun.style.opacity = 0;
    }

    // Moon visible 18:00-6:00
    let moonT = t >= 18 ? t - 18 : t + 6;
    if (t >= 18 || t <= 6) {
      const moonProgress = moonT / 12;
      const mx = moonProgress * (w - 60);
      this.moon.style.left = mx + 'px';
      this.moon.style.top = (h2 * 0.3 - Math.sin(moonProgress * Math.PI) * h2 * 0.25) + 'px';
      this.moon.style.opacity = Math.min(1, (1 - dayFactor) * 2);
    } else {
      this.moon.style.opacity = 0;
    }

    if (window.Clouds) Clouds.setDarkness(1 - dayFactor);
  }
};
