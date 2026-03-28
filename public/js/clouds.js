// Cloud animation system
const Clouds = {
  container: null,
  clouds: [],
  darkness: 0,

  init() {
    this.container = document.getElementById('cloudsContainer');
    const cloudFiles = ['cloud01_nobg.png','cloud02_nobg.png','cloud03_nobg.png','cloud04_nobg.png','cloud05_nobg.png','cloud06_nobg.png','cloud07_nobg.png'];
    for (let i = 0; i < 5; i++) {
      const img = document.createElement('img');
      img.className = 'cloud';
      img.src = `/img/UI/clouds/${cloudFiles[Math.floor(Math.random() * cloudFiles.length)]}`;
      const size = 80 + Math.random() * 120;
      img.style.width = size + 'px';
      img.style.top = (5 + Math.random() * 25) + '%';
      img.style.left = (-20 + Math.random() * 120) + '%';
      const speed = 0.01 + Math.random() * 0.03; // % per frame
      this.container.appendChild(img);
      this.clouds.push({ el: img, speed, left: parseFloat(img.style.left) });
    }
    this.animate();
  },

  animate() {
    this.clouds.forEach(c => {
      c.left += c.speed;
      if (c.left > 110) c.left = -25;
      c.el.style.left = c.left + '%';
    });
    requestAnimationFrame(() => this.animate());
  },

  setDarkness(d) {
    this.darkness = d; 
    this.clouds.forEach(c => {
      c.el.style.filter = `brightness(${1 - d * 0.6})`;
    });
  }
};
