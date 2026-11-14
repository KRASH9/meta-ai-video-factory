from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import random
from html import escape

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "topics.json"
OUTPUT_DIR = ROOT / "output"
PLAN_FILE = OUTPUT_DIR / "daily-plan.md"
DASHBOARD_FILE = OUTPUT_DIR / "index.html"
HISTORY_FILE = OUTPUT_DIR / "history.html"
META_AI_CHAT_URL = "https://www.meta.ai/share/c/iqLO8gdyHr?utm_source=android_meta_ai_sl"

WARSAW = ZoneInfo("Europe/Warsaw")
generated_at = datetime.now(WARSAW)
today = generated_at.date()
generated_at_label = generated_at.strftime("%Y-%m-%d %H:%M:%S %Z")
date_seed = today.strftime("%Y-%m-%d")

# Seasonal direction follows the current calendar season in Warsaw / Central Europe.
month = today.month
if month in (9, 10, 11):
    season_name = "autumn"
    seasonal_direction = (
        "Set the scene unmistakably in autumn in Central Europe, appropriate to the current part of the season. "
        "Use believable autumn details such as fallen yellow, amber and brown leaves, damp paths, bare or partly bare branches, "
        "cool overcast light, gentle rain, low natural mist, quiet grey-blue water and muted earthy colors. "
        "In late autumn, show mostly fallen leaves and increasingly bare trees. "
        "Do not show lush summer greenery, tropical vegetation, blossoms, sakura, summer sunshine or snow unless it is naturally present."
    )
elif month in (12, 1, 2):
    season_name = "winter"
    seasonal_direction = (
        "Set the scene in winter in Central Europe: bare trees, cold muted light, frost, occasional realistic snow, "
        "winter rain, still water or subdued evergreen forest. Do not show lush summer foliage, autumn foliage or spring blossoms."
    )
elif month in (3, 4, 5):
    season_name = "spring"
    seasonal_direction = (
        "Set the scene in spring in Central Europe: fresh new leaves, delicate blossoms where seasonally plausible, "
        "soft rain, brighter but gentle daylight and renewed greenery. Do not show peak summer heat or autumn foliage."
    )
else:
    season_name = "summer"
    seasonal_direction = (
        "Set the scene in summer in Central Europe: full green foliage, warm but natural daylight, rivers, lakes, "
        "meadows and gentle summer weather. Do not show autumn leaves, winter frost or snow."
    )

config = json.loads(CONFIG.read_text(encoding="utf-8"))
categories = config.get("categories", {})

required_categories = [
    "Nature & Water",
    "Forest & Weather",
    "Cozy Quiet Places"
]

missing = [name for name in required_categories if not categories.get(name)]
if missing:
    raise ValueError(f"Missing or empty topic categories: {', '.join(missing)}")

rng = random.Random(date_seed)
selected = []
used_scenes = set()

for category in required_categories:
    options = categories[category]
    available = [scene for scene in options if scene not in used_scenes]
    if not available:
        raise ValueError(f"No unused scenes available in category: {category}")
    scene = rng.choice(available)
    selected.append((category, scene))
    used_scenes.add(scene)

camera_approaches = [
    "Use a stable, mostly steady smartphone frame with only very subtle, slow natural movement if it improves the view. No shake, jitter, vibration, wobble, bouncing, fast panning, tilting, zooming or abrupt reframing.",
    "Keep the smartphone camera steady and immersive. A barely noticeable slow adjustment is acceptable, but no handheld shake, jitter, fast movement, sweeping motion or sudden perspective shifts.",
    "Choose a simple, natural composition and hold it mostly steady. Allow only very subtle slow camera movement; never use a drone, sweeping move, fast pan, tilt, zoom or shaky handheld motion."
]

captions = {
    "Nature & Water": "Take a moment. Let nature slow you down. 🌿",
    "Forest & Weather": "A quiet moment away from the noise. 🍃",
    "Cozy Quiet Places": "Some places make you breathe a little easier. 🤍"
}

# Keep a small brand core, then match the remaining tags to the actual scene.
brand_hashtags = ["#QuietPlace", "#SlowLiving"]

def build_hashtags(category, scene):
    text = scene.lower()
    tags = []
    if any(word in text for word in ("rain", "rainy", "shower", "wet")):
        tags += ["#RainSounds", "#RainyDay", "#AutumnRain"]
    if any(word in text for word in ("forest", "woodland", "birch", "pine", "tree", "trees")):
        tags += ["#ForestSounds", "#AutumnForest", "#ForestWalk"]
    if any(word in text for word in ("lake", "river", "waterfall", "water", "shore", "beach", "waves", "pond", "tide")):
        tags += ["#NatureSounds", "#WaterSounds", "#PeacefulNature"]
    if any(word in text for word in ("mist", "fog", "cloud", "overcast")):
        tags += ["#MistyMorning", "#QuietMoments", "#MoodyNature"]
    if any(word in text for word in ("street", "village", "cottage", "courtyard", "veranda", "cabin", "bench", "cobblestone")):
        tags += ["#QuietPlaces", "#HiddenPlaces", "#SlowLiving"]
    if season_name == "autumn":
        tags += ["#AutumnVibes", "#LateAutumn"]
    elif season_name == "winter":
        tags += ["#WinterNature", "#WinterMood"]
    elif season_name == "spring":
        tags += ["#SpringNature", "#SpringMood"]
    else:
        tags += ["#SummerNature", "#SummerMood"]
    # Preserve order and avoid duplicates; use up to five relevant tags.
    unique = list(dict.fromkeys(brand_hashtags + tags))
    return " ".join(unique[:5])

def build_prompt(scene, camera_note):
    return (
        f"Create a quiet, beautiful nature video for TikTok and Instagram in vertical 9:16 format, showing {scene}. "
        "Choose a fresh, varied natural place and composition; avoid repeating the same type of scenery every day. "
        "The mood is calm, peaceful, beautiful and immersive, like a real visitor quietly capturing a special place on a good smartphone. "
        f"{camera_note} "
        "Use natural, soft, realistic light, believable everyday colors and ordinary smartphone detail. "
        "No people, crowds, speech, talking or music with lyrics. Use only soft, authentic ambient sound from this place. "
        "Aim for a seamless natural loop: the ending should flow smoothly into the beginning, with matching framing and no visible cut. "
        "Use cyclical, physically believable natural movement where suitable, such as a wave coming and going, grass swaying back and forth, "
        "leaves moving gently or steady snowfall. Keep movement calm and consistent. "
        "No drone shots, sweeping camera moves, fast cuts, transitions or slow motion. "
        "No cinematic grading, dramatic sun rays, exaggerated fog or mist, artificial bokeh, visual effects, text, subtitles, logos or watermarks. "
        "Beautiful, clean and realistic, but not overly polished or synthetic; small natural imperfections are welcome. "
        "Avoid flicker, stutter, morphing, warping, duplicated objects, abrupt changes or unstable backgrounds."
    )

video_packages = []

lines = [
    "# QUIET PLACE — Daily Content Plan",
    "",
    f"Date: {today.isoformat()}",
    f"Prompts generated at: {generated_at_label} (Warsaw local time)",
    "Brand: Quiet Place",
    "Mission: Leave the noise behind.",
    f"Seasonal direction: {season_name.title()} in Central Europe.",
    "",
    "Three ready-to-produce videos. Individual copy-ready files are included in this package.",
    f"The goal is a believable quiet moment, not a cinematic travel scene. Seasonal setting: {season_name.title()} in Central Europe.",
    ""
]

for index, (category, scene) in enumerate(selected, start=1):
    camera_note = camera_approaches[index - 1]
    prompt = build_prompt(scene, camera_note)
    caption = captions[category]
    video_hashtags = build_hashtags(category, scene)
    video_packages.append({"index": index, "category": category, "scene": scene, "prompt": prompt, "caption": caption, "hashtags": video_hashtags})
    video_dir = OUTPUT_DIR / f"video-{index:02d}"
    video_dir.mkdir(parents=True, exist_ok=True)

    (video_dir / "01-meta-ai-prompt.txt").write_text(prompt + "\n", encoding="utf-8")
    (video_dir / "02-tiktok-caption-and-hashtags.txt").write_text(
        f"{caption}\n\n{video_hashtags}\n", encoding="utf-8"
    )
    (video_dir / "03-quality-checklist.txt").write_text(
        "QUIET PLACE — VIDEO QUALITY CHECK\n\n"
        "[ ] Vertical 9:16 format\n"
        "[ ] Looks like a real place filmed casually on a good smartphone\n"
        "[ ] Natural light and believable colors\n"
        "[ ] Camera is mostly steady; no shake, jitter, fast pans, tilts or zooms\n"
        "[ ] Natural motion is smooth and physically believable; no flicker, stutter, morphing or warping\n"
        "[ ] Ending flows naturally into the beginning where a seamless loop is intended\n"
        "[ ] Ambient environmental sound only; no music\n"
        "[ ] No text, logos, visual effects or transitions\n"
        "[ ] No visible generation defects or strange objects\n"
        "[ ] Suitable for the calm Quiet Place identity\n",
        encoding="utf-8"
    )
    (video_dir / "04-tiktok-publishing-checklist.txt").write_text(
        "QUIET PLACE — TIKTOK PUBLISHING CHECK\n\n"
        "[ ] Watch the full exported video before posting\n"
        "[ ] Confirm vertical 9:16 framing and 10-second duration target if applicable\n"
        "[ ] Copy the prepared caption and hashtags\n"
        "[ ] Choose a clear cover frame\n"
        "[ ] Review visibility, comments and other post settings\n"
        "[ ] Because this video is generated with AI and depicts a realistic-looking scene, "
        "check TikTok's AI-generated content disclosure setting before publishing\n"
        "[ ] Publish manually in TikTok and confirm the post appears on the profile\n",
        encoding="utf-8"
    )

    lines.extend([
        f"## Video {index} — {category}",
        "",
        f"**Scene:** {scene}",
        "",
        f"**Camera approach:** {camera_note}",
        "",
        "**Meta AI prompt:**",
        "",
        prompt,
        "",
        "**TikTok caption:**",
        "",
        caption,
        "",
        "**Hashtags:**",
        "",
        video_hashtags,
        "",
        f"**Copy-ready folder:** video-{index:02d}/",
        "",
        "**Quality checklist:**",
        "",
        "- [ ] Vertical 9:16 format",
        "- [ ] Natural, believable smartphone footage",
        "- [ ] Stable, mostly steady camera; no shake, jitter or fast camera moves",
        "- [ ] Smooth natural movement; no flicker, stutter or warping",
        "- [ ] Seamless loop where the scene supports it",
        "- [ ] Ambient sound only",
        "- [ ] No visual defects, text or logos",
        "- [ ] Suitable for Quiet Place",
        ""
    ])

lines.extend([
    "---",
    "",
    "## Daily quality standards",
    "",
    "- Authentic everyday realism matters more than cinematic beauty.",
    "- Each video should feel like a casual phone recording of a real place.",
    "- Use natural light, believable colors and ordinary camera framing.",
    "- Keep the camera stable and mostly steady; allow only very subtle slow movement, never jitter or fast sweeping.\n"
    "- Prefer seamless natural loops with matching start/end framing and cyclical movement where suitable.\n"
    "- Keep subject movement smooth and physically believable; reject flicker, stutter, morphing or warping.",
    "- Use natural ambient sound only; no background music.",
    "- The three videos must use different scenes and camera approaches.",
    "- Scene selection comes from config/topics.json.",
    "- This planner does not yet keep a persistent history of previously published scenes.",
    "- Never publish a defective or unsuitable video.",
    ""
])

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PLAN_FILE.write_text("\n".join(lines), encoding="utf-8")


# Mobile dashboard: copy a prompt, then open the Meta AI website.
cards = []
for item in video_packages:
    prompt_json = json.dumps(item["prompt"], ensure_ascii=False).replace("</", "<\\/")
    post_json = json.dumps(item["caption"] + "\n\n" + item["hashtags"], ensure_ascii=False)
    cards.append(
        f"""
        <article class="card">
          <div class="eyebrow">VIDEO {item["index"]} · {escape(item["category"])}</div>
          <h2>{escape(item["scene"])}</h2>
          <button class="copy" data-prompt='{escape(prompt_json, quote=True)}'>Copy Meta AI prompt</button>
          <button class="copy-post" data-post='{escape(post_json, quote=True)}'>Copy TikTok caption + hashtags</button>
          <p class="caption">{escape(item["caption"])}</p>
          <p class="tags">{escape(item["hashtags"])}</p>
          <div class="tracker" data-video="{item["index"]}" data-date="DATE_PLACEHOLDER">
            <label>Status
              <select data-field="status">
                <option value="planned">Planned</option>
                <option value="created">Created</option>
                <option value="checked">Quality checked</option>
                <option value="published">Published</option>
              </select>
            </label>
            <label>TikTok post URL<input data-field="url" type="url" placeholder="Paste published video link"></label>
            <div class="metrics">
              <label>Views<input data-field="views" type="number" min="0" inputmode="numeric" placeholder="0"></label>
              <label>Likes<input data-field="likes" type="number" min="0" inputmode="numeric" placeholder="0"></label>
              <label>Comments<input data-field="comments" type="number" min="0" inputmode="numeric" placeholder="0"></label>
              <label>Shares<input data-field="shares" type="number" min="0" inputmode="numeric" placeholder="0"></label>
            </div>
            <button class="save-record" type="button">Save tracking data</button>
            <small class="saved-note" aria-live="polite">Not saved yet</small>
          </div>
        </article>
        """
    )

dashboard = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Quiet Place — Daily Studio</title>
<style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;padding:22px;background:#101110;color:#f3f3ef;font:16px/1.5 system-ui,-apple-system,sans-serif}
main{max-width:680px;margin:auto}.muted{color:#a8aaa4}.card{background:#1b1d1a;border:1px solid #343731;border-radius:16px;padding:18px;margin:16px 0}
.eyebrow{font-size:12px;letter-spacing:.12em;color:#b9c5a8;font-weight:700}h1{font-size:28px;margin:8px 0}h2{font-size:19px;line-height:1.35;margin:10px 0 16px}
button,a.primary{display:block;width:100%;border:0;border-radius:12px;padding:15px 16px;text-align:center;font-size:16px;font-weight:700;text-decoration:none;cursor:pointer}
.copy{background:#e4e8dc;color:#172016}.copy-post{background:#30362e;color:#f3f3ef;margin-top:10px}.primary{background:#9eb18c;color:#11190f;margin:20px 0}.caption{margin:14px 0 4px}.tags{font-size:13px;color:#b6b9b0;overflow-wrap:anywhere}
.status{min-height:24px;color:#b9c5a8;font-size:14px;margin-top:8px}.note{font-size:13px;color:#a8aaa4;margin:18px 0}
.tracker{border-top:1px solid #343731;margin-top:18px;padding-top:14px;display:grid;gap:10px}.tracker label{display:grid;gap:5px;color:#c7c9c1;font-size:13px}
.tracker input,.tracker select{width:100%;min-width:0;background:#101310;color:#f3f3ef;border:1px solid #454a40;border-radius:9px;padding:11px;font:inherit}
.metrics{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}.save-record,.export{background:#b9c5a8;color:#172016}.saved-note{color:#a8aaa4}
.analytics{background:#1b1d1a;border:1px solid #343731;border-radius:16px;padding:18px;margin:18px 0}.totals{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.metric{background:#101310;border-radius:10px;padding:12px}.metric strong{display:block;font-size:22px}.metric span{font-size:12px;color:#a8aaa4}
</style>
</head>
<body><main>
<div class="eyebrow">QUIET PLACE · LEAVE THE NOISE BEHIND</div>
<h1>Daily Content Studio</h1>
<p class="muted">DATE_PLACEHOLDER · PROMPTS_CREATED_PLACEHOLDER · 3 videos · prompts + TikTok publishing text</p>
<a class="primary" href="META_AI_URL_PLACEHOLDER" target="_blank" rel="noopener">PUBLICATION</a>
<a class="primary" style="background:#252a24;color:#f3f3ef" href="https://www.tiktok.com/@quiet.place_7" target="_blank" rel="noopener">Open Quiet Place on TikTok</a>
<a class="primary" style="background:#30362e;color:#f3f3ef" href="history.html">PUBLICATION HISTORY &amp; ANALYTICS</a>
<div id="status" class="status" aria-live="polite">Copy a video prompt for Meta AI, then copy its caption and hashtags for TikTok.</div>
<section class="analytics">
  <div class="eyebrow">PUBLICATION TRACKER</div><h2>Daily performance</h2>
  <div class="totals">
    <div class="metric"><strong id="total-views">0</strong><span>Views</span></div>
    <div class="metric"><strong id="total-likes">0</strong><span>Likes</span></div>
    <div class="metric"><strong id="total-comments">0</strong><span>Comments</span></div>
    <div class="metric"><strong id="total-shares">0</strong><span>Shares</span></div>
  </div>
  <p class="note">Totals update when you save each video's data.</p>
  <button class="export" id="export-csv" type="button">Export tracking CSV</button>
</section>
""" + "\n".join(cards) + """
<p class="note">This dashboard prepares and copies text only. Generate and save videos in Meta AI, then upload them manually in TikTok. For realistic AI-generated scenes, check TikTok's AI disclosure setting before posting.</p>
</main>
<script>
const trackerKey='quiet-place-publication-tracker-v1';
let trackerData={};
try{trackerData=JSON.parse(localStorage.getItem(trackerKey)||'{}')||{};}catch(e){trackerData={};}
const trackerCards=[...document.querySelectorAll('.tracker')];
function recordId(card){return card.dataset.date+'-video-'+card.dataset.video;}
function updateTotals(){
  const totals={views:0,likes:0,comments:0,shares:0};
  Object.values(trackerData).forEach(record=>Object.keys(totals).forEach(k=>totals[k]+=Number(record[k]||0)));
  Object.entries(totals).forEach(([k,v])=>{const el=document.getElementById('total-'+k);if(el)el.textContent=v.toLocaleString();});
}
trackerCards.forEach(card=>{
  const id=recordId(card),saved=trackerData[id]||{};
  card.querySelectorAll('[data-field]').forEach(field=>{if(saved[field.dataset.field]!==undefined)field.value=saved[field.dataset.field];});
  if(saved.updatedAt)card.querySelector('.saved-note').textContent='Saved '+saved.updatedAt;
  card.querySelector('.save-record').addEventListener('click',()=>{
    const record={date:card.dataset.date,video:card.dataset.video};
    card.querySelectorAll('[data-field]').forEach(field=>record[field.dataset.field]=field.value);
    record.updatedAt=new Date().toLocaleString();
    trackerData[id]=record;
    try{localStorage.setItem(trackerKey,JSON.stringify(trackerData));card.querySelector('.saved-note').textContent='Saved '+record.updatedAt;updateTotals();}
    catch(e){card.querySelector('.saved-note').textContent='Could not save on this browser';}
  });
});
updateTotals();
document.getElementById('export-csv').addEventListener('click',()=>{
  const columns=['date','video','status','url','views','likes','comments','shares','updatedAt'];
  const rows=[columns.join(','),...Object.values(trackerData).map(r=>columns.map(k=>'"'+String(r[k]??'').replace(/"/g,'""')+'"').join(','))];
  const blob=new Blob([rows.join('\\n')],{type:'text/csv;charset=utf-8;'});
  const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='quiet-place-publication-tracker.csv';a.click();URL.revokeObjectURL(url);
});
document.querySelectorAll('.copy,.copy-post').forEach(button=>{
  button.addEventListener('click',async()=>{
    const prompt=JSON.parse(button.dataset.prompt || button.dataset.post);
    const originalLabel=button.textContent;
    try{
      if(navigator.clipboard && window.isSecureContext){await navigator.clipboard.writeText(prompt);}
      else{
        const field=document.createElement('textarea');field.value=prompt;
        field.style.position='fixed';field.style.opacity='0';document.body.appendChild(field);
        field.focus();field.select();const ok=document.execCommand('copy');field.remove();
        if(!ok) throw new Error('Clipboard unavailable');
      }
      document.getElementById('status').textContent=button.classList.contains('copy-post')?'TikTok caption and hashtags copied. Paste them into your TikTok post.':'Meta AI prompt copied. Paste it into your Meta AI chat.';
      button.textContent='Copied ✓';setTimeout(()=>button.textContent=originalLabel,1800);
    }catch(e){
      document.getElementById('status').textContent='Copy was blocked. Use the individual prompt .txt file instead.';
    }
  });
});
</script>
</body></html>"""
dashboard = dashboard.replace("DATE_PLACEHOLDER", today.isoformat()).replace("PROMPTS_CREATED_PLACEHOLDER", "Created " + generated_at.strftime("%H:%M:%S %Z") + " (Warsaw time)").replace("META_AI_URL_PLACEHOLDER", META_AI_CHAT_URL)
DASHBOARD_FILE.write_text(dashboard, encoding="utf-8")

# Dedicated history page, sharing the same browser-local tracker store as the daily studio.
history_page = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Quiet Place — Publication History</title>
<style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;padding:20px;background:#101110;color:#f3f3ef;font:15px/1.5 system-ui,-apple-system,sans-serif}
main{max-width:760px;margin:auto}.muted,small{color:#a8aaa4}.eyebrow{font-size:12px;letter-spacing:.12em;color:#b9c5a8;font-weight:700}
h1{font-size:27px;margin:8px 0}h2{font-size:19px;margin:8px 0 14px}
a{color:#c7d4b8}.back{display:inline-block;margin:8px 0 18px;text-decoration:none}
.panel,.entry{background:#1b1d1a;border:1px solid #343731;border-radius:15px;padding:16px;margin:14px 0}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.metric{background:#101310;border-radius:10px;padding:12px}.metric strong{display:block;font-size:22px}.metric span{font-size:12px;color:#a8aaa4}
.controls{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}.controls select,.controls button{background:#252a24;color:#f3f3ef;border:1px solid #454a40;border-radius:9px;padding:10px;font:inherit}
.entry h3{font-size:16px;margin:5px 0 8px}.meta{font-size:12px;color:#a8aaa4}.stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px;margin:12px 0}.stats div{background:#101310;padding:8px;border-radius:8px;font-size:12px}.stats b{display:block;font-size:16px}
.pill{display:inline-block;border:1px solid #53604c;border-radius:20px;padding:2px 8px;font-size:11px;color:#c7d4b8}
.empty{padding:20px;text-align:center;color:#a8aaa4}.danger{color:#e6b4a9}.url{overflow-wrap:anywhere}
</style></head><body><main>
<div class="eyebrow">QUIET PLACE · LEAVE THE NOISE BEHIND</div><h1>Publication History &amp; Analytics</h1>
<p class="muted">Your saved TikTok publication records, across daily content plans.</p>
<a class="back" href="index.html">← Back to Daily Content Studio</a>
<section class="panel"><div class="eyebrow">CHANNEL OVERVIEW</div><h2>All saved publications</h2>
<div class="grid">
<div class="metric"><strong id="count">0</strong><span>Publications tracked</span></div>
<div class="metric"><strong id="views">0</strong><span>Total views</span></div>
<div class="metric"><strong id="likes">0</strong><span>Total likes</span></div>
<div class="metric"><strong id="engagement">0</strong><span>Interactions (likes + comments + shares)</span></div>
</div></section>
<section class="panel"><h2>Browse records</h2><div class="controls">
<select id="sort"><option value="newest">Newest first</option><option value="views">Most views</option><option value="likes">Most likes</option></select>
<select id="status"><option value="all">All statuses</option><option value="published">Published</option><option value="created">Created</option><option value="checked">Quality checked</option><option value="planned">Planned</option></select>
</div><div id="records"></div></section>
<p class="muted">Data is read from the same browser storage as Daily Content Studio. It stays on this device and browser; clearing site data or switching devices can remove or hide it. Export CSV from the studio regularly as a backup.</p>
</main><script>
const key='quiet-place-publication-tracker-v1';let data={};
try{data=JSON.parse(localStorage.getItem(key)||'{}')||{};}catch(e){data={};}
const fmt=n=>Number(n||0).toLocaleString();
const records=Object.values(data).sort((a,b)=>(b.date||'').localeCompare(a.date||'')||Number(b.video)-Number(a.video));
const sum=k=>records.reduce((s,r)=>s+Number(r[k]||0),0);
document.getElementById('count').textContent=records.length;
document.getElementById('views').textContent=fmt(sum('views'));
document.getElementById('likes').textContent=fmt(sum('likes'));
document.getElementById('engagement').textContent=fmt(sum('likes')+sum('comments')+sum('shares'));
function render(){
 const sort=document.getElementById('sort').value,status=document.getElementById('status').value;
 let list=records.filter(r=>status==='all'||(r.status||'planned')===status);
 if(sort==='views')list.sort((a,b)=>Number(b.views||0)-Number(a.views||0));
 if(sort==='likes')list.sort((a,b)=>Number(b.likes||0)-Number(a.likes||0));
 const root=document.getElementById('records');
 if(!list.length){root.innerHTML='<div class="empty">No saved publication records yet. Save a video in Daily Content Studio and it will appear here.</div>';return;}
 root.innerHTML=list.map(r=>{
 const statusLabel=(r.status||'planned').replace('checked','quality checked');
 const link=r.url?'<p class="url"><a href="'+String(r.url).replace(/&/g,'&amp;').replace(/"/g,'&quot;')+'" target="_blank" rel="noopener">Open TikTok publication ↗</a></p>':'<p class="meta">No TikTok URL saved</p>';
 return '<article class="entry"><div class="meta">'+(r.date||'Date not set')+' · Video '+(r.video||'?')+'</div><h3>Quiet Place publication</h3><span class="pill">'+statusLabel+'</span>'+link+
 '<div class="stats"><div><b>'+fmt(r.views)+'</b>Views</div><div><b>'+fmt(r.likes)+'</b>Likes</div><div><b>'+fmt(r.comments)+'</b>Comments</div><div><b>'+fmt(r.shares)+'</b>Shares</div></div><div class="meta">Last saved: '+(r.updatedAt||'—')+'</div></article>';
 }).join('');
}
document.getElementById('sort').addEventListener('change',render);
document.getElementById('status').addEventListener('change',render);
render();
</script></body></html>"""
HISTORY_FILE.write_text(history_page, encoding="utf-8")


print(f"Quiet Place package created: {OUTPUT_DIR}")
print(f"Date: {today.isoformat()}")
print("Videos planned: 3")
for index, (category, scene) in enumerate(selected, start=1):
    print(f"{index}. {category}: {scene}")
