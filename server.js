const express = require('express');
const initSqlJs = require('sql.js');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const nodemailer = require('nodemailer');
const { spawn } = require('child_process');

const app = express();

// Email verification codes (in-memory)
const verifyMap = new Map(); // email -> { code, expires }
const mailer = nodemailer.createTransport({
  host: 'smtp.qq.com', port: 465, secure: true,
  auth: { user: '3566853396@qq.com', pass: 'asckdkzgkcoldadf' }
});
app.use(express.json());
app.use('/img', express.static(path.join(__dirname, 'img')));
app.use('/Fonts', express.static(path.join(__dirname, 'Fonts')));
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));
app.use('/py', express.static(path.join(__dirname, 'py')));
app.use(express.static(path.join(__dirname, 'public')));

if (!fs.existsSync('uploads')) fs.mkdirSync('uploads');
if (!fs.existsSync('recipe-suggestions')) fs.mkdirSync('recipe-suggestions');

let db;
const DB_PATH = 'game.db';

function saveDb() { fs.writeFileSync(DB_PATH, Buffer.from(db.export())); }

function run(sql, params) { db.run(sql, params); saveDb(); }
function get(sql, params) { const stmt = db.prepare(sql); if (params) stmt.bind(params); return stmt.step() ? stmt.getAsObject() : null; }
function all(sql, params) {
  const stmt = db.prepare(sql);
  if (params) stmt.bind(params);
  const rows = [];
  while (stmt.step()) rows.push(stmt.getAsObject());
  stmt.free();
  return rows;
}

const TREE_REQ = [{ water:1, fert:0 },{ water:2, fert:1 },{ water:6, fert:2 },{ water:12, fert:4 }];

function genId() {
  const existing = all('SELECT id FROM users').map(r => r.id);
  let id;
  do { id = Math.floor(Math.random() * 90000) + 10000; } while (existing.includes(id));
  return id;
}

function checkAchievements(uid) {
  const user = get('SELECT * FROM users WHERE id=?', [uid]);
  if (!user) return;
  const has = (t) => get('SELECT 1 FROM achievements WHERE user_id=? AND title=?', [uid, t]);
  if (user.water_count >= 1 && !has('First Watering')) run('INSERT INTO achievements(user_id,title) VALUES(?,?)', [uid, 'First Watering']);
  if (user.fertilize_count >= 1 && !has('First Fertilizing')) run('INSERT INTO achievements(user_id,title) VALUES(?,?)', [uid, 'First Fertilizing']);
  [1,2,3,4].forEach(s => {
    if (user.tree_stage >= s && !has(`Tree Stage ${s}`)) run('INSERT INTO achievements(user_id,title) VALUES(?,?)', [uid, `Tree Stage ${s}`]);
  });
}

function tryGrowTree(uid) {
  const user = get('SELECT * FROM users WHERE id=?', [uid]);
  if (!user || user.tree_stage >= 4) return;
  const req = TREE_REQ[user.tree_stage];
  if (user.water_count >= req.water && user.fertilize_count >= req.fert)
    run('UPDATE users SET tree_stage=tree_stage+1, water_count=0, fertilize_count=0 WHERE id=?', [uid]);
}

// Run a Python script and return stdout as JSON
function runPython(scriptPath, args = [], timeoutMs = 120000) {
  return new Promise((resolve, reject) => {
    const proc = spawn('python', [scriptPath, ...args], { cwd: path.join(__dirname, 'py', 'models') });
    let stdout = '', stderr = '', done = false;
    const timer = setTimeout(() => { if (!done) { done = true; proc.kill(); reject(new Error('Python timeout')); } }, timeoutMs);
    proc.stdout.on('data', d => stdout += d);
    proc.stderr.on('data', d => stderr += d);
    proc.on('close', code => {
      if (done) return;
      done = true; clearTimeout(timer);
      if (code !== 0) return reject(new Error(stderr || `Python exit ${code}`));
      try { resolve(JSON.parse(stdout)); } catch { resolve(stdout.trim()); }
    });
  });
}

async function start() {
  const SQL = await initSqlJs();
  if (fs.existsSync(DB_PATH)) {
    db = new SQL.Database(fs.readFileSync(DB_PATH));
  } else {
    db = new SQL.Database();
  }

  db.run(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY, username TEXT NOT NULL, email TEXT DEFAULT '',
    email_verified INTEGER DEFAULT 0, gender TEXT DEFAULT 'Male', avatar TEXT DEFAULT 'man.png',
    currency INTEGER DEFAULT 30, tree_stage INTEGER DEFAULT 0,
    water_count INTEGER DEFAULT 0, fertilize_count INTEGER DEFAULT 0,
    water_today INTEGER DEFAULT 0, fertilize_today INTEGER DEFAULT 0,
    last_water_time TEXT DEFAULT '', last_settle_date TEXT DEFAULT '',
    nutrition_score REAL DEFAULT 0, carbon_emission REAL DEFAULT 0,
    summary_today INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
  );
  CREATE TABLE IF NOT EXISTS meals (
    id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, meal_name TEXT,
    grams REAL DEFAULT 0, calories REAL DEFAULT 0, carbon_footprint REAL DEFAULT 0,
    image_path TEXT DEFAULT '', created_at TEXT DEFAULT (datetime('now'))
  );
  CREATE TABLE IF NOT EXISTS decorations (
    id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, item_name TEXT, quantity INTEGER DEFAULT 0,
    UNIQUE(user_id, item_name)
  );
  CREATE TABLE IF NOT EXISTS placed_decos (
    id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, item_name TEXT, x REAL, y REAL
  );
  CREATE TABLE IF NOT EXISTS achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, title TEXT,
    achieved_at TEXT DEFAULT (datetime('now'))
  );
  CREATE TABLE IF NOT EXISTS nutrition_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
    vitamin_a REAL DEFAULT 0, vitamin_c REAL DEFAULT 0, vitamin_d REAL DEFAULT 0,
    vitamin_e REAL DEFAULT 0, thiamin REAL DEFAULT 0, riboflavin REAL DEFAULT 0,
    niacin REAL DEFAULT 0, vitamin_b6 REAL DEFAULT 0, folate REAL DEFAULT 0,
    vitamin_b12 REAL DEFAULT 0, calcium REAL DEFAULT 0, iron REAL DEFAULT 0,
    magnesium REAL DEFAULT 0, phosphorus REAL DEFAULT 0, zinc REAL DEFAULT 0,
    protein REAL DEFAULT 0, fat REAL DEFAULT 0, carbohydrate REAL DEFAULT 0,
    fiber REAL DEFAULT 0, sodium REAL DEFAULT 0, log_date TEXT DEFAULT (date('now'))
  );
  CREATE TABLE IF NOT EXISTS scan_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
    mode TEXT DEFAULT 'summary', image_path TEXT DEFAULT '',
    result_json TEXT DEFAULT '{}', carbon_total REAL DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
  );
  CREATE TABLE IF NOT EXISTS recipe_suggestions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
    title TEXT, ingredients TEXT, instructions TEXT,
    created_at TEXT DEFAULT (datetime('now'))
  );`);

  // Add summary_today column if missing (migration)
  try { db.run('ALTER TABLE users ADD COLUMN summary_today INTEGER DEFAULT 0'); } catch(e) {}
  saveDb();

  // Register
  app.post('/api/register', (req, res) => {
    const { username, email, gender, avatar } = req.body;
    if (!username) return res.status(400).json({ error: 'Username required' });
    const id = genId();
    run('INSERT INTO users(id,username,email,gender,avatar) VALUES(?,?,?,?,?)', [id, username, email||'', gender||'Male', avatar||'man.png']);
    res.json({ id, username });
  });

  // Send verification code
  app.post('/api/send-code', async (req, res) => {
    const { email } = req.body;
    if (!email) return res.status(400).json({ error: 'Email required' });
    const code = String(Math.floor(100000 + Math.random() * 900000));
    verifyMap.set(email, { code, expires: Date.now() + 5 * 60 * 1000 });
    try {
      await mailer.sendMail({
        from: '3566853396@qq.com', to: email,
        subject: 'Your Verification Code',
        text: `Your code is: ${code} (valid for 5 minutes)`
      });
      res.json({ ok: true });
    } catch (e) {
      res.status(500).json({ error: 'Failed to send email' });
    }
  });

  // Verify email code (settings confirm)
  app.post('/api/verify-email', (req, res) => {
    const { email, code } = req.body;
    if (!email || !code) return res.status(400).json({ error: 'Email and code required' });
    const entry = verifyMap.get(email);
    if (!entry || entry.code !== code || Date.now() > entry.expires)
      return res.status(400).json({ error: 'Invalid or expired code' });
    verifyMap.delete(email);
    res.json({ ok: true });
  });

  // Login with verification code
  app.post('/api/login', (req, res) => {
    const { email, code } = req.body;
    if (!email || !code) return res.status(400).json({ error: 'Email and code required' });
    const entry = verifyMap.get(email);
    if (!entry || entry.code !== code || Date.now() > entry.expires)
      return res.status(400).json({ error: 'Invalid or expired code' });
    verifyMap.delete(email);
    const user = get('SELECT * FROM users WHERE email=?', [email]);
    if (!user) return res.status(404).json({ error: 'User not found' });
    res.json(user);
  });

  // Get user
  app.get('/api/user/:id', (req, res) => {
    const user = get('SELECT * FROM users WHERE id=?', [+req.params.id]);
    if (!user) return res.status(404).json({ error: 'Not found' });
    res.json(user);
  });

  // Update user
  app.put('/api/user/:id', (req, res) => {
    const { username, avatar, email } = req.body;
    const sets = [], vals = [];
    if (username !== undefined) { sets.push('username=?'); vals.push(username); }
    if (avatar !== undefined) { sets.push('avatar=?'); vals.push(avatar); }
    if (email !== undefined) { sets.push('email=?'); vals.push(email); }
    if (!sets.length) return res.status(400).json({ error: 'Nothing' });
    vals.push(+req.params.id);
    run(`UPDATE users SET ${sets.join(',')} WHERE id=?`, vals);
    res.json({ ok: true });
  });

  // Water (requires summary scan today)
  app.post('/api/user/:id/water', (req, res) => {
    const uid = +req.params.id;
    let user = get('SELECT * FROM users WHERE id=?', [uid]);
    if (!user) return res.status(404).json({ error: 'Not found' });
    const today = new Date().toISOString().slice(0,10);
    if (user.last_settle_date !== today) {
      run('UPDATE users SET water_today=0, fertilize_today=0, summary_today=0, last_settle_date=? WHERE id=?', [today, uid]);
      user = get('SELECT * FROM users WHERE id=?', [uid]);
    }
    if (!user.summary_today) return res.status(400).json({ error: 'Scan a meal first (Summary Mode) before watering' });
    if (user.water_today >= 3) return res.status(400).json({ error: 'Max 3 waters/day' });
    if (user.last_water_time) {
      const diff = Date.now() - new Date(user.last_water_time).getTime();
      if (diff < 4*3600*1000) return res.status(400).json({ error: 'Cooldown', remaining: 4*3600*1000-diff });
    }
    run('UPDATE users SET water_count=water_count+1, water_today=water_today+1, last_water_time=? WHERE id=?', [new Date().toISOString(), uid]);
    tryGrowTree(uid); checkAchievements(uid);
    res.json({ ok: true });
  });

  // Fertilize
  app.post('/api/user/:id/fertilize', (req, res) => {
    const uid = +req.params.id;
    let user = get('SELECT * FROM users WHERE id=?', [uid]);
    if (!user) return res.status(404).json({ error: 'Not found' });
    const today = new Date().toISOString().slice(0,10);
    if (user.last_settle_date !== today) run('UPDATE users SET water_today=0, fertilize_today=0, summary_today=0, last_settle_date=? WHERE id=?', [today, uid]);
    user = get('SELECT * FROM users WHERE id=?', [uid]);
    if (user.fertilize_today >= 1) return res.status(400).json({ error: 'Already fertilized' });
    if (user.water_today < 3) return res.status(400).json({ error: 'Need 3 waters first' });
    run('UPDATE users SET fertilize_count=fertilize_count+1, fertilize_today=1 WHERE id=?', [uid]);
    tryGrowTree(uid); checkAchievements(uid);
    res.json({ ok: true });
  });

  // Ranking
  app.get('/api/ranking/:type', (req, res) => {
    const page = parseInt(req.query.page)||0;
    const order = req.params.type === 'carbon' ? 'carbon_emission ASC' : 'nutrition_score DESC';
    res.json(all(`SELECT id,username,avatar,carbon_emission,nutrition_score FROM users ORDER BY ${order} LIMIT 20 OFFSET ?`, [page*20]));
  });

  // Shop
  app.get('/api/shop/items', (req, res) => {
    const files = fs.readdirSync(path.join(__dirname,'img','Decos')).filter(f=>f.endsWith('.png'));
    res.json(files.map(f=>({ name:f.replace('.png',''), image:`/img/Decos/${f}`, price:5 })));
  });

  app.post('/api/shop/buy', (req, res) => {
    const { userId, itemName } = req.body;
    const user = get('SELECT * FROM users WHERE id=?', [userId]);
    if (!user) return res.status(404).json({ error: 'Not found' });
    if (user.currency < 5) return res.status(400).json({ error: 'Not enough currency' });
    run('UPDATE users SET currency=currency-5 WHERE id=?', [userId]);
    const existing = get('SELECT * FROM decorations WHERE user_id=? AND item_name=?', [userId, itemName]);
    if (existing) run('UPDATE decorations SET quantity=quantity+1 WHERE user_id=? AND item_name=?', [userId, itemName]);
    else run('INSERT INTO decorations(user_id,item_name,quantity) VALUES(?,?,1)', [userId, itemName]);
    res.json({ ok: true });
  });

  app.get('/api/user/:id/decorations', (req, res) => res.json(all('SELECT * FROM decorations WHERE user_id=?', [+req.params.id])));

  app.post('/api/user/:id/place-deco', (req, res) => {
    const uid = +req.params.id;
    const { itemName, x, y } = req.body;
    const deco = get('SELECT * FROM decorations WHERE user_id=? AND item_name=? AND quantity>0', [uid, itemName]);
    if (!deco) return res.status(400).json({ error: 'No deco' });
    run('UPDATE decorations SET quantity=quantity-1 WHERE user_id=? AND item_name=?', [uid, itemName]);
    run('INSERT INTO placed_decos(user_id,item_name,x,y) VALUES(?,?,?,?)', [uid, itemName, x, y]);
    res.json({ ok: true });
  });

  app.get('/api/user/:id/placed-decos', (req, res) => res.json(all('SELECT * FROM placed_decos WHERE user_id=?', [+req.params.id])));
  app.get('/api/user/:id/achievements', (req, res) => res.json(all('SELECT * FROM achievements WHERE user_id=? ORDER BY achieved_at DESC', [+req.params.id])));

  app.get('/api/user/:id/meals', (req, res) => {
    const today = new Date().toISOString().slice(0,10);
    res.json(all("SELECT * FROM meals WHERE user_id=? AND date(created_at)=?", [+req.params.id, today]));
  });

  app.get('/api/user/:id/nutrition', (req, res) => {
    const today = new Date().toISOString().slice(0,10);
    res.json(all('SELECT * FROM nutrition_log WHERE user_id=? AND log_date=?', [+req.params.id, today]));
  });

  const upload = multer({ dest:'uploads/', limits:{ fileSize:10*1024*1024 } });
  app.post('/api/upload', upload.single('photo'), (req, res) => {
    if (!req.file) return res.status(400).json({ error:'No file' });
    const ext = path.extname(req.file.originalname)||'.jpg';
    const newPath = req.file.path + ext;
    fs.renameSync(req.file.path, newPath);
    res.json({ path: '/'+newPath.replace(/\\/g,'/') });
  });

  // Summary Mode
  app.post('/api/scan/summary', upload.single('photo'), async (req, res) => {
    if (!req.file) return res.status(400).json({ error:'No file' });
    const uid = +req.body.userId;
    if (!uid) return res.status(400).json({ error:'userId required' });
    const ext = path.extname(req.file.originalname)||'.jpg';
    const newPath = req.file.path + ext;
    fs.renameSync(req.file.path, newPath);
    const absPath = path.resolve(newPath);
    const lat = req.body.lat || '31.2304';
    const lon = req.body.lon || '121.4737';
    try {
      const result = await runPython('food_pipeline.py', [absPath, lat, lon, '--json']);
      // Save scan history
      const carbonTotal = Array.isArray(result) ? result.reduce((s,r) => s + (r.geo_emissions || r.emissions_per_kg * r.mass_kg || 0), 0) : 0;
      run('INSERT INTO scan_history(user_id,mode,image_path,result_json,carbon_total) VALUES(?,?,?,?,?)',
        [uid, 'summary', '/'+newPath.replace(/\\/g,'/'), JSON.stringify(result), carbonTotal]);
      // Carbon-based currency: reward if below threshold
      const CARBON_THRESHOLD = 2.0; // kg CO2e per meal avg
      let coinReward = 0;
      if (carbonTotal < CARBON_THRESHOLD && carbonTotal >= 0) {
        coinReward = Math.max(1, Math.round((CARBON_THRESHOLD - carbonTotal) / CARBON_THRESHOLD * 20));
      }
      run('UPDATE users SET carbon_emission=carbon_emission+?, summary_today=1, currency=currency+? WHERE id=?', [carbonTotal, coinReward, uid]);
      // Save as meal
      if (Array.isArray(result)) {
        const mealName = result.map(r => r.food).join(', ');
        run('INSERT INTO meals(user_id,meal_name,grams,carbon_footprint,image_path) VALUES(?,?,?,?,?)',
          [uid, mealName, result.reduce((s,r) => s + r.mass_kg*1000, 0), carbonTotal, '/'+newPath.replace(/\\/g,'/')]);
      }
      res.json({ ok:true, results: result, image: '/'+newPath.replace(/\\/g,'/'), carbon_total: carbonTotal, coins_earned: coinReward });
    } catch(e) {
      console.error('Summary scan error:', e.message);
      res.status(500).json({ error: e.message || 'Pipeline failed' });
    }
  });

  // Suggestion Mode
  app.post('/api/scan/suggestion', upload.single('photo'), async (req, res) => {
    if (!req.file) return res.status(400).json({ error:'No file' });
    const uid = +req.body.userId;
    if (!uid) return res.status(400).json({ error:'userId required' });
    const ext = path.extname(req.file.originalname)||'.jpg';
    const newPath = req.file.path + ext;
    fs.renameSync(req.file.path, newPath);
    const absPath = path.resolve(newPath);
    try {
      const result = await runPython('RecipeSuggestion.py', [absPath]);
      // Save scan history
      run('INSERT INTO scan_history(user_id,mode,image_path,result_json) VALUES(?,?,?,?)',
        [uid, 'suggestion', '/'+newPath.replace(/\\/g,'/'), JSON.stringify(result)]);
      res.json({ ok:true, ...result });
    } catch(e) {
      console.error('Suggestion scan error:', e.message);
      res.status(500).json({ error: e.message || 'Pipeline failed' });
    }
  });

  // Feedback
  app.post('/api/scan/feedback', async (req, res) => {
    const { delta, meal } = req.body;
    if (!delta || !meal) return res.status(400).json({ error:'delta and meal required' });
    try {
      const result = await runPython('personal_feedback.py', []);
      // Actually call via stdin since args are complex - use inline python
      const proc = spawn('python', ['-c', `
import sys; sys.path.insert(0,'${path.join(__dirname,'py','models').replace(/\\/g,'/')}')
from personal_feedback import feedback
print(feedback('''${delta}''','''${meal}'''))
`]);
      let out = '';
      proc.stdout.on('data', d => out += d);
      proc.on('close', () => res.json({ feedback: out.trim() }));
    } catch(e) {
      res.status(500).json({ error: e.message });
    }
  });

  // Recipe suggestions crud
  app.get('/api/user/:id/recipes', (req, res) => {
    res.json(all('SELECT * FROM recipe_suggestions WHERE user_id=? ORDER BY created_at DESC LIMIT 20', [+req.params.id]));
  });

  app.post('/api/user/:id/recipes', (req, res) => {
    const uid = +req.params.id;
    const { title, ingredients, instructions } = req.body;
    // Enforce max 20
    const count = get('SELECT COUNT(*) as c FROM recipe_suggestions WHERE user_id=?', [uid]);
    if (count && count.c >= 20) {
      // Delete oldest
      run('DELETE FROM recipe_suggestions WHERE id=(SELECT id FROM recipe_suggestions WHERE user_id=? ORDER BY created_at ASC LIMIT 1)', [uid]);
    }
    run('INSERT INTO recipe_suggestions(user_id,title,ingredients,instructions) VALUES(?,?,?,?)',
      [uid, title, ingredients||'', instructions||'']);
    res.json({ ok:true });
  });

  app.delete('/api/user/:id/recipes/:rid', (req, res) => {
    run('DELETE FROM recipe_suggestions WHERE id=? AND user_id=?', [+req.params.rid, +req.params.id]);
    res.json({ ok:true });
  });

  // Scan his.
  app.get('/api/user/:id/scans', (req, res) => {
    res.json(all('SELECT * FROM scan_history WHERE user_id=? ORDER BY created_at DESC LIMIT 20', [+req.params.id]));
  });

  // Deliveries
  const DELIVERY_ORDER = [
    'Freshly ground coffee breakfast set',
    'Beef Double-Packed Salad',
    'ribeye steak',
    'iced coffee',
    'Cream Fruit Cake',
    'ribeye steak and pasta'
  ];
  app.get('/api/delivery/items', (req, res) => {
    const dir = path.join(__dirname, 'py', 'Meituan', 'pics');
    if (!fs.existsSync(dir)) return res.json([]);
    const files = fs.readdirSync(dir).filter(f => /\.(jpg|png|jpeg)$/i.test(f));
    const items = files.map(f => ({ name: f.replace(/\.[^.]+$/, ''), image: `/py/Meituan/pics/${encodeURIComponent(f)}` }));
    items.sort((a, b) => {
      const ai = DELIVERY_ORDER.indexOf(a.name), bi = DELIVERY_ORDER.indexOf(b.name);
      return (ai === -1 ? 999 : ai) - (bi === -1 ? 999 : bi);
    });
    res.json(items);
  });

  // Legacy recipe suggest endpoint
  app.get('/api/recipes/suggest', (req, res) => res.json({ suggestions:[], message:'Use camera Suggestion Mode' }));

  app.post('/api/user/:id/settle', (req, res) => {
    const uid = +req.params.id;
    const user = get('SELECT * FROM users WHERE id=?', [uid]);
    if (!user) return res.status(404).json({ error:'Not found' });
    const today = new Date().toISOString().slice(0,10);
    if (user.last_settle_date === today) return res.json({ ok:true, msg:'Already settled' });
    // Daily bonus based on avg carbon per scan: lower avg = more bonus
    const scans = all('SELECT carbon_total FROM scan_history WHERE user_id=? AND date(created_at)=?', [uid, today]);
    let bonus = 0;
    if (scans.length) {
      const avg = scans.reduce((s,r) => s + r.carbon_total, 0) / scans.length;
      const DAILY_THRESHOLD = 2.0;
      if (avg < DAILY_THRESHOLD) bonus = Math.max(1, Math.round((DAILY_THRESHOLD - avg) / DAILY_THRESHOLD * 10));
    }
    run('UPDATE users SET currency=currency+?, last_settle_date=?, water_today=0, fertilize_today=0, summary_today=0 WHERE id=?', [bonus, today, uid]);
    res.json({ ok:true, bonus });
  });

  app.listen(3000, () => console.log('Server running on http://localhost:3000'));
}

start();
