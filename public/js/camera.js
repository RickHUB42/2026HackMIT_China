// Camera page with Summary / Suggestion modes
let cameraStream = null;
let cameraMode = 'summary';

function setCameraMode(mode) {
  cameraMode = mode;
  document.querySelectorAll('.cam-mode-btn').forEach(b => b.classList.toggle('active', b.dataset.mode === mode));
  document.getElementById('cameraModeHint').textContent =
    mode === 'summary' ? 'Scan your meal to analyze nutrition & carbon footprint'
                       : 'Scan your fridge to get recipe suggestions';
}

function openCamera() {
  document.getElementById('cameraPage').classList.remove('hidden');
  const video = document.getElementById('cameraVideo');
  navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' }, audio: false })
    .then(stream => { cameraStream = stream; video.srcObject = stream; })
    .catch(() => showToast('Camera access denied'));
}

function closeCamera() {
  document.getElementById('cameraPage').classList.add('hidden');
  document.getElementById('cameraLoading').classList.add('hidden');
  if (cameraStream) { cameraStream.getTracks().forEach(t => t.stop()); cameraStream = null; }
}

async function takePhoto() {
  const video = document.getElementById('cameraVideo');
  const canvas = document.getElementById('cameraCanvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0);

  const loading = document.getElementById('cameraLoading');
  document.getElementById('loadingText').textContent =
    cameraMode === 'summary' ? 'Analyzing your meal...' : 'Detecting fridge contents...';
  loading.classList.remove('hidden');

  canvas.toBlob(async (blob) => {
    const file = new File([blob], `photo_${Date.now()}.jpg`, { type: 'image/jpeg' });
    if (!Game.user) { loading.classList.add('hidden'); return; }

    // Get geolocation
    const geo = await new Promise(r => {
      navigator.geolocation.getCurrentPosition(
        p => r({ lat: p.coords.latitude, lon: p.coords.longitude }),
        () => r(null), { timeout: 5000 }
      );
    });

    try {
      if (cameraMode === 'summary') {
        const res = await API.uploadScan('/api/scan/summary', file, Game.user.id, geo);
        loading.classList.add('hidden');
        closeCamera();
        showSummaryResult(res);
        await App.refreshUser();
      } else {
        const res = await API.uploadScan('/api/scan/suggestion', file, Game.user.id);
        loading.classList.add('hidden');
        closeCamera();
        showSuggestionResult(res);
      }
    } catch (e) {
      loading.classList.add('hidden');
      closeCamera();
      showToast(e.error || 'Scan failed');
    }
  }, 'image/jpeg', 0.85);
}

function showSummaryResult(res) {
  const page = document.getElementById('summaryResultPage');
  page.classList.remove('hidden');

  if (res.image) {
    document.getElementById('summaryBgImg').style.backgroundImage = `url(${res.image})`;
  }

  const results = res.results || [];
  let html = '<table class="summary-table"><tr><th>Food</th><th>Mass(kg)</th><th>CO₂e/kg</th><th>Geo CO₂</th></tr>';
  results.forEach(r => {
    const em = r.emissions_per_kg ? r.emissions_per_kg.toFixed(2) : 'N/A';
    const geo = r.geo_emissions ? r.geo_emissions.toFixed(4) : 'N/A';
    html += `<tr><td>${r.food}</td><td>${r.mass_kg.toFixed(3)}</td><td>${em}</td><td>${geo}</td></tr>`;
  });
  html += '</table>';
  document.getElementById('summaryTable').innerHTML = html;
  const coinText = res.coins_earned ? ` | +${res.coins_earned} 🪙` : '';
  document.getElementById('summaryTotalCarbon').innerHTML =
    `<p class="carbon-total">Total Carbon: <strong>${(res.carbon_total || 0).toFixed(4)} kg CO₂e</strong>${coinText}</p>`;

  document.getElementById('feedbackBubble').classList.add('hidden');
  if (results.length) {
    const meal = results.map(r => `${r.food} (${r.mass_kg.toFixed(2)}kg)`).join(', ');
    API.post('/api/scan/feedback', { delta: '0,'.repeat(26), meal })
      .then(fb => {
        if (fb.feedback) {
          document.getElementById('feedbackText').textContent = fb.feedback;
          document.getElementById('feedbackBubble').classList.remove('hidden');
        }
      }).catch(() => {});
  }
}

function closeSummaryResult() {
  document.getElementById('summaryResultPage').classList.add('hidden');
}

function showSuggestionResult(res) {
  const page = document.getElementById('suggestionResultPage');
  page.classList.remove('hidden');

  const foods = res.foods || {};
  const foodKeys = Object.keys(foods);
  document.getElementById('detectedFoods').innerHTML = foodKeys.length
    ? '<h3>Detected Foods</h3>' + foodKeys.map(f => `<span class="food-tag">${f} (${foods[f]}kg)</span>`).join(' ')
    : '<p>No foods detected</p>';

  const recipes = res.recipes || [];
  let html = '<h3>Recommended Recipes</h3>';
  recipes.forEach(r => {
    html += `<div class="recipe-card">
      <h4>${r.title}</h4>
      <p class="recipe-ing">${r.ingredients}</p>
      <button class="btn-green btn-sm" onclick="saveRecipe('${r.title.replace(/'/g,"\\'")}','${(r.ingredients||'').replace(/'/g,"\\'")}','${(r.instructions||'').replace(/'/g,"\\'")}')">Save</button>
    </div>`;
  });
  document.getElementById('suggestedRecipes').innerHTML = html;
}

function closeSuggestionResult() {
  document.getElementById('suggestionResultPage').classList.add('hidden');
}

async function saveRecipe(title, ingredients, instructions) {
  if (!Game.user) return;
  try {
    await API.post(`/api/user/${Game.user.id}/recipes`, { title, ingredients, instructions });
    showToast('Recipe saved!');
  } catch (e) {
    showToast('Failed to save');
  }
}
