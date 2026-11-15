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
CONTENT_FILE = OUTPUT_DIR / "content.html"
HISTORY_FILE = OUTPUT_DIR / "history.html"
CALENDAR_FILE = OUTPUT_DIR / "calendar.html"
ANALYTICS_FILE = OUTPUT_DIR / "analytics.html"
META_AI_CHAT_URL = "https://www.meta.ai/share/c/1PlNrwtGII?utm_source=android_meta_ai_sl"

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

# Captions are written from the selected scene, not just its broad category.
# Each video gets a distinct description that names the actual subject and its movement/atmosphere.
def build_caption(category, scene):
    text = scene.lower()
    rules = [
        (("lake", "shoreline", "shore", "reed-lined"), "A quiet shoreline, soft autumn air and water that barely moves. Stay here for a moment. 🌊"),
        (("waves", "pebble beach", "tide", "wet sand"), "Waves arrive, retreat, and leave the world a little quieter. 🌊"),
        (("rain drops", "ripples", "pond"), "Tiny raindrops, endless ripples. Sometimes the smallest moments are the most peaceful. 🍂"),
        (("stone footbridge", "river", "drifting on the water"), "An old stone bridge, a slow-moving river and leaves carried downstream. 🍁"),
        (("water flowing", "rock ledge", "waterfall"), "Just the sound of water finding its way through the autumn forest. 💧"),
        (("driftwood", "grey-blue water"), "Driftwood by the water. A simple view with nowhere else to be. 🌫️"),
        (("wooden pier", "misty"), "A quiet pier disappearing into the mist. Would you sit here for a while? 🤍"),
        (("waterfall", "forest"), "A small forest waterfall and the steady rhythm of flowing water. Take a breath. 🌿"),
        (("narrow muddy path", "pine and birch"), "A rain-soaked path through pine and birch. No rush, no destination. 🌲"),
        (("bare birch branches", "breeze"), "Bare birch branches moving gently in the cold autumn breeze. 🍃"),
        (("drops of rain", "last brown leaves"), "Rain falling from the last autumn leaves. Listen closely. 🍂"),
        (("woodland trail", "wet amber"), "A woodland trail covered in wet amber leaves. The kind of walk that clears your head. 🍁"),
        (("grey november morning", "bare trees"), "A quiet November morning among bare trees. Nothing to chase, nowhere to be. 🌫️"),
        (("mist", "tree trunks"), "Soft mist drifting between the trees after the rain. Let the noise fade. 🌫️"),
        (("birch grove", "golden leaves"), "A few golden leaves still holding on in the birch grove. Autumn, at its quietest. 🍂"),
        (("wooden bench", "empty autumn park"), "An empty park bench beneath bare trees. Imagine having this whole afternoon to yourself. 🤍"),
        (("clouds passing", "hillside"), "Clouds moving slowly above the autumn hillside. A little space to breathe. ☁️"),
        (("rain falling", "fallen leaves"), "Rain tapping against fallen leaves beside the forest path. Just nature, nothing more. 🌧️"),
        (("rain running down the window", "cottage"), "Rain on a cottage window and a slow autumn afternoon. This is your sign to pause. 🌧️"),
        (("european street", "wet paving stones"), "An empty old street after the rain, with reflections on every stone. 🚶"),
        (("courtyard", "old stone flooring"), "A quiet stone courtyard after the shower. Even familiar places can feel like a retreat. 🍂"),
        (("village lane", "modest houses"), "A quiet village lane beneath the November sky. Would you take the long way home? 🏡"),
        (("wooden veranda", "garden"), "A sheltered veranda, a rain-washed garden and a moment to do absolutely nothing. 🤍"),
        (("outdoor table", "cottage window"), "A little table outside a cottage on a misty morning. Coffee would make this perfect. ☕"),
        (("garden path", "late-season plants"), "A garden path softened by rain and fallen leaves. Slow steps, quiet thoughts. 🍃"),
        (("cabin porch", "woodland"), "A cabin porch looking out over the quiet woods. Could you spend a whole day here? 🌲"),
        (("park shelter", "autumn rain"), "Watching the cold autumn rain from a quiet park shelter. No need to hurry. 🌧️"),
        (("empty bench", "cobblestone lane"), "An empty bench on a rain-darkened cobblestone lane. A small pocket of calm. 🤍"),
    ]
    for keywords, caption in rules:
        if all(word in text for word in keywords):
            return caption
    # Specific fallback uses the actual scene description so it never falls back to a category-only caption.
    clean = scene.strip().rstrip(".")
    return f"{clean[0].upper() + clean[1:]}. A quiet moment to leave the noise behind. 🤍"

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
        f"Create a beautiful, immersive nature video for TikTok and Instagram in vertical 9:16 format, showing {scene}. "
        "The setting must feel authentic to the current season in Warsaw and Central Europe. "
        f"{seasonal_direction} "
        "Keep the Quiet Place identity: peaceful and restorative, but visually captivating enough to make someone pause while scrolling. "
        "Give the scene one clear visual focal point and a pleasing sense of depth, with foreground, middle distance and background where natural. "
        "Use a richer, more expressive version of the real seasonal palette: warm amber, copper, golden yellow and deep earthy tones for autumn; "
        "natural contrast and gentle color separation without oversaturation, artificial filters or a fake cinematic look. "
        "Avoid flat, washed-out grey images. Even on an overcast day, preserve detail, subtle warmth and color in leaves, water and surroundings. "
        "Light should remain believable and soft; a natural warm reflection or gentle brighter patch is welcome when plausible, never artificial sunbeams. "
        f"{camera_note} "
        "Keep the camera smooth and stable, with only subtle slow movement. The scene itself should have gently noticeable, continuous natural motion: "
        "leaves drifting or swaying, water rippling, rain falling, branches moving softly or reflections changing. "
        "Make the motion soothing but visible; avoid a lifeless frozen frame and avoid gusty, chaotic movement. "
        "No people, crowds, speech, talking or music with lyrics. Use only soft, authentic ambient sound from this place. "
        "Aim for a seamless natural loop where suitable: the ending should flow smoothly into the beginning, with matching framing and no visible cut. "
        "Use cyclical, physically believable movement. No drone shots, sweeping camera moves, fast cuts, transitions or slow motion. "
        "No artificial bokeh, visual effects, text, subtitles, logos or watermarks. "
        "Beautiful, clean and realistic, with natural imperfections; not overly polished or synthetic. "
        "Avoid camera shake, jitter, vibration, flicker, stutter, morphing, warping, duplicated objects, abrupt changes or unstable backgrounds."
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
    caption = build_caption(category, scene)
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
        "[ ] Natural seasonal setting and visibly rich but believable seasonal colors\n"
        "[ ] Camera is mostly steady; no shake, jitter, fast pans, tilts or zooms\n"
        "[ ] Clear visual focal point, pleasing depth and visible but gentle natural movement\n"
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
    "- Use soft natural light, rich but believable seasonal colors, a clear focal point and visual depth.",
    "- Make scenes visually engaging without sacrificing the calm, realistic Quiet Place identity.",
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
              <label>Favorites / saves<input data-field="saves" type="number" min="0" inputmode="numeric" placeholder="0"></label>
            </div>
            <button class="save-record" type="button">Save tracking data</button>
            <small class="saved-note" aria-live="polite">Not saved yet</small>
          </div>
        </article>
        """
    )

dashboard = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Quiet Place — Studio</title>
<style>
:root{color-scheme:dark;--bg:#090909;--panel:#191919;--panel2:#222;--line:#303030;--muted:#a1a1a1;--text:#f5f5f5;--orange:#ff7a24;--green:#ff7a24}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 system-ui,-apple-system,sans-serif;padding:18px 16px 100px}
main{max-width:760px;margin:auto}.topline{display:flex;align-items:center;justify-content:space-between;color:#d0d0d0;font-size:12px;letter-spacing:.15em;font-weight:700}
.logo{display:flex;align-items:center;gap:8px}.logo-mark{width:9px;height:9px;border-radius:50%;background:var(--orange);box-shadow:0 0 16px #ff7a2470}
h1{font-size:27px;line-height:1.15;margin:20px 0 4px}h2{font-size:18px;margin:0 0 12px}h3{font-size:16px;margin:6px 0 10px}
.muted,.meta,.note{color:var(--muted)}.muted{font-size:13px}.panel,.card{background:var(--panel);border:1px solid var(--line);border-radius:17px;padding:16px;margin:14px 0}
.eyebrow{font-size:11px;letter-spacing:.14em;color:#c4c4c4;font-weight:700}.accent{color:var(--orange)}
.hero{background:linear-gradient(135deg,#24160e,#171717 58%);border:1px solid #49301e;border-radius:18px;padding:18px;margin:18px 0}
.hero p{color:#c8c8c8;font-size:13px;margin:5px 0 15px}.hero-actions{display:grid;grid-template-columns:1fr 1fr;gap:9px}
button,a.action{border:0;border-radius:11px;padding:12px 14px;text-align:center;font-size:13px;font-weight:700;text-decoration:none;cursor:pointer}
.action-primary{background:var(--orange);color:#1a1009}.action-secondary{background:#303030;color:#fff}
.kpis{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}.metric{background:#101010;border:1px solid #282828;border-radius:12px;padding:13px}.metric strong{display:block;font-size:23px;line-height:1.2}.metric span{font-size:11px;color:#a5a5a5}
.growth{height:120px;width:100%;display:block;margin-top:8px}.chart-labels{display:flex;justify-content:space-between;color:#777;font-size:10px}
.nav{position:fixed;z-index:10;bottom:0;left:0;right:0;background:#151515f2;border-top:1px solid #303030;backdrop-filter:blur(14px);display:flex;justify-content:center;padding:9px 8px max(12px,env(safe-area-inset-bottom))}
.nav-inner{width:min(760px,100%);display:grid;grid-template-columns:repeat(5,1fr);gap:4px}
.nav a{display:block;text-align:center;text-decoration:none;background:transparent;color:#888;padding:8px 3px;font-size:10px;border-radius:10px}.nav a.active{color:var(--orange);background:#2b1b12}.nav .nav-icon{display:block;font-size:17px;margin-bottom:2px}
.view{display:none}.view.active{display:block}
.card{margin:12px 0}.eyebrow{color:#c6c6c6}.copy{background:#efefea;color:#171717;width:100%;margin:8px 0 0}.copy-post{background:#303030;color:#fff;width:100%;margin-top:8px}
.caption{margin:12px 0 4px}.tags{font-size:12px;color:#b3b3b3;overflow-wrap:anywhere}.status{min-height:20px;color:#ffad72;font-size:12px;margin:8px 0}
.tracker{border-top:1px solid var(--line);margin-top:15px;padding-top:13px;display:grid;gap:9px}.tracker label{display:grid;gap:5px;color:#bdbdbd;font-size:12px}
.tracker input,.tracker select{width:100%;min-width:0;background:#101010;color:#fff;border:1px solid #414141;border-radius:9px;padding:10px;font:inherit}
.metrics{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.save-record,.export{background:var(--orange);color:#1a1009;width:100%}.saved-note{color:#999;font-size:11px}
.section-head{display:flex;align-items:center;justify-content:space-between;margin:22px 0 10px}.section-head small{color:#888}
.list-row{display:flex;justify-content:space-between;gap:12px;padding:12px 0;border-bottom:1px solid #303030;font-size:13px}.list-row:last-child{border:0}
.calendar-grid{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:5px;text-align:center}
.calendar-grid .weekday{font-size:10px;color:#999;padding:5px 0}
.calendar-day{background:#101010;color:#eee;border:1px solid #303030;border-radius:8px;min-height:38px;padding:7px 2px;font-size:12px;position:relative}
.calendar-day.has-post{border-color:#9b5529;color:#ffad72}
.calendar-day.selected{background:#ff7a24;color:#1a1009;border-color:#ff7a24;font-weight:800}
.calendar-day .dot{display:block;width:5px;height:5px;border-radius:50%;background:#ff7a24;margin:2px auto 0}
.calendar-day.selected .dot{background:#1a1009}
.calendar-day:disabled{opacity:.25}
.pill{display:inline-block;border:1px solid #61432e;border-radius:20px;padding:2px 8px;font-size:10px;color:#ffb17b}
.history-link{display:block;text-decoration:none;color:#ff9a52;border:1px solid #57351e;padding:13px;border-radius:11px;text-align:center;font-weight:700;margin:12px 0}
.open-content-cta{display:block;width:100%;margin:16px 0 22px;padding:16px;background:#ff7a24;color:#1a1009;border:0;border-radius:12px;font-weight:800;font-size:14px;letter-spacing:.04em;text-align:center;text-decoration:none}
.note{font-size:11px;margin:14px 0}
@media(min-width:600px){.kpis{grid-template-columns:repeat(4,minmax(0,1fr))}.hero{padding:22px}.card{padding:20px}}
</style></head><body><main>
<div class="topline"><div class="logo"><span class="logo-mark"></span> QUIET PLACE</div><span class="muted">LEAVE THE NOISE BEHIND</span></div>
<section id="overview" class="view active">
<h1>Overview</h1><p class="muted">DATE_PLACEHOLDER · Created PROMPTS_CREATED_PLACEHOLDER · 3 new videos ready</p>
<div class="hero"><div class="eyebrow accent">DAILY CONTENT STUDIO</div><h2 style="font-size:22px;margin-top:8px">Your next quiet moment starts here.</h2><p>Generate your nature videos with Meta AI, then prepare each post for TikTok.</p>
<div class="hero-actions"><a class="action action-primary" href="META_AI_URL_PLACEHOLDER" target="_blank" rel="noopener">OPEN CONTENT STUDIO →</a><a class="action action-secondary" href="https://www.tiktok.com/@quiet.place_7" target="_blank" rel="noopener">TikTok profile ↗</a></div></div>
<section class="panel"><div class="eyebrow">CHANNEL OVERVIEW</div><div class="section-head"><h2>Performance</h2><small>Saved records</small></div>
<div class="kpis"><div class="metric"><strong id="total-views">0</strong><span>Views</span></div><div class="metric"><strong id="total-likes">0</strong><span>Likes</span></div><div class="metric"><strong id="total-comments">0</strong><span>Comments</span></div><div class="metric"><strong id="total-shares">0</strong><span>Shares</span></div><div class="metric"><strong id="total-saves">0</strong><span>Favorites</span></div></div>
<svg class="growth" viewBox="0 0 600 120" preserveAspectRatio="none" aria-label="Illustrative performance trend"><defs><linearGradient id="area" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#ff7a24" stop-opacity=".35"/><stop offset="1" stop-color="#ff7a24" stop-opacity="0"/></linearGradient></defs><path d="M0 100 L55 82 L105 88 L160 55 L215 66 L270 32 L325 48 L380 26 L435 45 L490 18 L545 38 L600 12 L600 120 L0 120Z" fill="url(#area)"/><path d="M0 100 L55 82 L105 88 L160 55 L215 66 L270 32 L325 48 L380 26 L435 45 L490 18 L545 38 L600 12" fill="none" stroke="#ff7a24" stroke-width="3"/></svg>
<div class="chart-labels"><span>Recent</span><span>Performance history</span><span>Today</span></div>
<p class="note">The line is a visual placeholder until enough dated performance snapshots are recorded. Totals use saved publication data.</p>
</section>
<a class="history-link" href="https://krash9.github.io/meta-ai-video-factory/history.html?v=navfix2">OPEN PUBLICATION HISTORY &amp; ANALYTICS ↗</a>
<div class="section-head"><h2>Today's content</h2><small>3 videos</small></div>
<div id="today-summary"></div>
<a class="open-content-cta" href="https://krash9.github.io/meta-ai-video-factory/content.html?v=navfix2">VIEW 3 PROMPTS &amp; PUBLICATIONS →</a>
</section>
<section id="content" class="view">
<h1>Content Studio</h1><p class="muted">Your three seasonal prompts, captions and publishing trackers.</p>
<div id="status" class="status" aria-live="polite">Copy a prompt for Meta AI, then copy its caption and hashtags for TikTok.</div>
""" + "\n".join(cards) + """
<p class="note">Generate and save videos in Meta AI, then upload them manually in TikTok. Check TikTok's AI disclosure setting for realistic generated scenes.</p>
</section>
<section id="calendar" class="view"><h1>Publication Calendar</h1><p class="muted">Choose a date to see videos published or tracked on that day.</p>
<div class="panel"><div class="section-head"><button id="month-prev" class="action action-secondary" type="button">‹</button><h2 id="month-label">Month</h2><button id="month-next" class="action action-secondary" type="button">›</button></div>
<div class="calendar-grid" id="calendar-grid"></div><div class="section-head"><h2 id="selected-date-label">Selected date</h2><small id="selected-count">0 publications</small></div><div id="calendar-list"></div></div></section>
<section id="analytics" class="view"><h1>Analytics</h1><p class="muted">Compare saved performance across all publications.</p><div class="panel"><div class="kpis"><div class="metric"><strong id="a-views">0</strong><span>Total views</span></div><div class="metric"><strong id="a-likes">0</strong><span>Total likes</span></div><div class="metric"><strong id="a-comments">0</strong><span>Comments</span></div><div class="metric"><strong id="a-shares">0</strong><span>Shares</span></div><div class="metric"><strong id="a-saves">0</strong><span>Favorites</span></div></div><div class="section-head"><h2>Top publications</h2><small>By views</small></div><div id="top-posts"></div><button id="export-csv" class="action action-primary" type="button" style="width:100%;margin-top:16px">Export tracking CSV</button></div><a class="history-link" href="https://krash9.github.io/meta-ai-video-factory/history.html?v=navfix2">OPEN FULL HISTORY ↗</a></section>
</main>
<nav class="nav"><div class="nav-inner"><a class="active" href="https://krash9.github.io/meta-ai-video-factory/index.html?v=navfix2"><span class="nav-icon">⌂</span>Overview</a><a href="https://krash9.github.io/meta-ai-video-factory/calendar.html?v=navfix2"><span class="nav-icon">▦</span>Calendar</a><a href="https://krash9.github.io/meta-ai-video-factory/content.html?v=navfix2"><span class="nav-icon">▤</span>Content</a><a href="https://krash9.github.io/meta-ai-video-factory/analytics.html?v=navfix2"><span class="nav-icon">▥</span>Analytics</a><a href="https://krash9.github.io/meta-ai-video-factory/history.html?v=navfix2"><span class="nav-icon">↗</span>History</a></div></nav>
<script>
const trackerKey='quiet-place-publication-tracker-v1';let trackerData={};
try{trackerData=JSON.parse(localStorage.getItem(trackerKey)||'{}')||{};}catch(e){trackerData={};}
if(!trackerData['archive-20261108-coastal-sunset']){trackerData['archive-20261108-coastal-sunset']={date:'2026-11-08',time:'01:57',video:'Archive',title:'Coastal sunset',url:'https://vm.tiktok.com/ZN85xQcuy/',views:788,likes:43,comments:3,shares:1,saves:2,status:'published',updatedAt:'Imported from user-provided TikTok Studio screenshot'};localStorage.setItem(trackerKey,JSON.stringify(trackerData));}
const cards=[...document.querySelectorAll('.tracker')];
function recordId(card){return card.dataset.date+'-video-'+card.dataset.video;}
function fmt(v){return Number(v||0).toLocaleString();}
function records(){return Object.values(trackerData);}
let calendarMonth=new Date();calendarMonth.setDate(1);
let selectedCalendarDate=new Date().toISOString().slice(0,10);
function renderCalendar(){
 const grid=document.getElementById('calendar-grid');if(!grid)return;
 const year=calendarMonth.getFullYear(),month=calendarMonth.getMonth();
 document.getElementById('month-label').textContent=calendarMonth.toLocaleDateString('en-GB',{month:'long',year:'numeric'});
 const counts={};records().forEach(r=>{if(r.date)counts[r.date]=(counts[r.date]||0)+1;});
 const first=new Date(year,month,1),offset=(first.getDay()+6)%7,days=new Date(year,month+1,0).getDate();
 const names=['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
 grid.innerHTML=names.map(n=>'<div class="weekday">'+n+'</div>').join('');
 for(let i=0;i<offset;i++)grid.insertAdjacentHTML('beforeend','<div></div>');
 for(let day=1;day<=days;day++){
  const date=year+'-'+String(month+1).padStart(2,'0')+'-'+String(day).padStart(2,'0'),count=counts[date]||0;
  const b=document.createElement('button');b.type='button';b.className='calendar-day'+(count?' has-post':'')+(date===selectedCalendarDate?' selected':'');
  b.textContent=day;if(count){const dot=document.createElement('span');dot.className='dot';b.appendChild(dot);}
  b.addEventListener('click',()=>{selectedCalendarDate=date;renderCalendar();});grid.appendChild(b);
 }
 const dayRecords=records().filter(r=>r.date===selectedCalendarDate);
 document.getElementById('selected-date-label').textContent=new Date(selectedCalendarDate+'T12:00:00').toLocaleDateString('en-GB',{weekday:'long',day:'numeric',month:'long',year:'numeric'});
 document.getElementById('selected-count').textContent=dayRecords.length+' publication'+(dayRecords.length===1?'':'s');
 const list=document.getElementById('calendar-list');
 list.innerHTML=dayRecords.length?dayRecords.map(r=>'<div class="list-row"><span>'+String(r.title||('Video '+r.video)).replace(/</g,'&lt;')+'</span><span>'+fmt(r.views)+' views</span></div>').join(''):'<p class="muted">No publications saved for this date.</p>';
}
document.getElementById('month-prev').addEventListener('click',()=>{calendarMonth.setMonth(calendarMonth.getMonth()-1);renderCalendar();});
document.getElementById('month-next').addEventListener('click',()=>{calendarMonth.setMonth(calendarMonth.getMonth()+1);renderCalendar();});
function updateDashboard(){
 const totals={views:0,likes:0,comments:0,shares:0,saves:0};
 records().forEach(r=>Object.keys(totals).forEach(k=>totals[k]+=Number(r[k]||0)));
 Object.entries(totals).forEach(([k,v])=>{['total-'+k,'a-'+k].forEach(id=>{const el=document.getElementById(id);if(el)el.textContent=fmt(v);});});
 renderCalendar();
 const top=document.getElementById('top-posts');
 if(top)top.innerHTML=records().sort((a,b)=>Number(b.views||0)-Number(a.views||0)).slice(0,5).map(r=>'<div class="list-row"><span>'+r.date+' · Video '+r.video+'</span><b>'+fmt(r.views)+' views</b></div>').join('')||'<p class="muted">Add publication stats to see rankings.</p>';
 const summary=document.getElementById('today-summary');
 if(summary)summary.innerHTML=cards.map(c=>'<div class="list-row"><span>Video '+c.dataset.video+' · '+(c.querySelector('h2')?.textContent||'Scene')+'</span><span class="pill">Ready</span></div>').join('');
}
cards.forEach(card=>{
 const id=recordId(card),saved=trackerData[id]||{};
 card.querySelectorAll('[data-field]').forEach(f=>{if(saved[f.dataset.field]!==undefined)f.value=saved[f.dataset.field];});
 if(saved.updatedAt)card.querySelector('.saved-note').textContent='Saved '+saved.updatedAt;
 card.querySelector('.save-record').addEventListener('click',()=>{
  const rec={date:card.dataset.date,video:card.dataset.video};
  card.querySelectorAll('[data-field]').forEach(f=>rec[f.dataset.field]=f.value);
  rec.updatedAt=new Date().toLocaleString();trackerData[id]=rec;
  try{localStorage.setItem(trackerKey,JSON.stringify(trackerData));card.querySelector('.saved-note').textContent='Saved '+rec.updatedAt;updateDashboard();}
  catch(e){card.querySelector('.saved-note').textContent='Could not save on this browser';}
 });
});
document.querySelectorAll('.copy,.copy-post').forEach(btn=>btn.addEventListener('click',async()=>{
 const value=JSON.parse(btn.dataset.prompt||btn.dataset.post),label=btn.textContent;
 try{
  if(navigator.clipboard&&window.isSecureContext) await navigator.clipboard.writeText(value);
  else {const field=document.createElement('textarea');field.value=value;field.style.position='fixed';field.style.opacity='0';document.body.appendChild(field);field.focus();field.select();const ok=document.execCommand('copy');field.remove();if(!ok)throw new Error('copy failed');}
  const status=document.getElementById('status');if(status)status.textContent='Copied. Paste it into your selected app.';
  btn.textContent='Copied ✓';setTimeout(()=>btn.textContent=label,1600);
 }catch(e){const status=document.getElementById('status');if(status)status.textContent='Copy was blocked by the browser. Please try again.';}
}));
document.getElementById('export-csv').addEventListener('click',()=>{
 const cols=['date','video','status','url','views','likes','comments','shares','saves','updatedAt'];
 const rows=[cols.join(','),...records().map(r=>cols.map(k=>'"'+String(r[k]??'').replace(/"/g,'""')+'"').join(','))];
 const blob=new Blob([rows.join('\n')],{type:'text/csv;charset=utf-8;'}),url=URL.createObjectURL(blob),a=document.createElement('a');
 a.href=url;a.download='quiet-place-publication-tracker.csv';a.click();URL.revokeObjectURL(url);
});
updateDashboard();
</script></body></html>"""
dashboard = dashboard.replace("DATE_PLACEHOLDER", today.isoformat()).replace("PROMPTS_CREATED_PLACEHOLDER", generated_at.strftime("%H:%M:%S %Z") + " Warsaw time").replace("META_AI_URL_PLACEHOLDER", META_AI_CHAT_URL)
DASHBOARD_FILE.write_text(dashboard, encoding="utf-8")

content_page = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Quiet Place — Content Studio</title>
<style>
:root{color-scheme:dark;--bg:#090909;--panel:#191919;--line:#303030;--muted:#a1a1a1;--text:#f5f5f5;--orange:#ff7a24}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 system-ui,sans-serif;padding:18px 16px 50px}main{max-width:760px;margin:auto}
a{color:#ff9a52}.top{display:flex;justify-content:space-between;font-size:12px;letter-spacing:.14em;font-weight:700;color:#ccc}.back{display:inline-block;margin:18px 0;padding:10px 14px;border:1px solid #57351e;border-radius:10px;text-decoration:none}
h1{font-size:28px;margin:10px 0 4px}.muted{color:var(--muted);font-size:13px}.card{background:var(--panel);border:1px solid var(--line);border-radius:17px;padding:17px;margin:15px 0}
.eyebrow{font-size:11px;letter-spacing:.14em;color:#ccc;font-weight:700}h2{font-size:18px;line-height:1.4}
button{width:100%;padding:13px;border:0;border-radius:10px;font-weight:700;font-size:14px;margin:6px 0;cursor:pointer}
.copy{background:#efefea;color:#171717}.copy-post{background:#303030;color:white}.caption{margin:13px 0 4px}.tags{font-size:12px;color:#aaa;overflow-wrap:anywhere}
.tracker{border-top:1px solid var(--line);margin-top:15px;padding-top:13px;display:grid;gap:10px}.tracker label{display:grid;gap:5px;font-size:12px;color:#bbb}
.tracker input,.tracker select{width:100%;background:#101010;color:white;border:1px solid #414141;border-radius:9px;padding:11px;font:inherit}
.metrics{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.save-record{background:var(--orange);color:#1a1009}.saved-note{font-size:11px;color:#999}.status{color:#ffad72;font-size:12px}.prompt-updated{display:inline-block;margin:8px 0 12px;padding:8px 11px;border:1px solid #57351e;border-radius:8px;background:#21150f;color:#ffad72;font-size:11px;font-weight:800;letter-spacing:.08em}
.bottom-nav{position:fixed;bottom:0;left:0;right:0;background:#151515;display:grid;grid-template-columns:repeat(5,1fr);padding:10px 4px;z-index:20}.bottom-nav a{text-align:center;color:#999;text-decoration:none;font-size:11px;padding:6px 1px}.bottom-nav b{display:block;font-size:18px}.bottom-nav .active{color:#ff7a24}</style></head><body><main><div class="top"><span>🟠 QUIET PLACE</span><span>LEAVE THE NOISE BEHIND</span></div>
<a class="back" href="https://krash9.github.io/meta-ai-video-factory/index.html?v=navfix2">← Back to Overview</a><h1>Content Studio</h1><p class="muted">Three daily prompts · Meta AI video prompts · TikTok captions and tracking</p><p class="prompt-updated">PROMPTS UPDATED · PROMPT_UPDATED_AT_PLACEHOLDER WARSAW TIME</p><div id="status" class="status">Copy a prompt, create your video, then save publication details.</div>
""" + "\n".join(cards) + """
</main><nav class="bottom-nav"><a href="https://krash9.github.io/meta-ai-video-factory/index.html?v=navfix2"><b>⌂</b>Overview</a><a href="https://krash9.github.io/meta-ai-video-factory/calendar.html?v=navfix2"><b>▦</b>Calendar</a><a class="active" href="https://krash9.github.io/meta-ai-video-factory/content.html?v=navfix2"><b>▤</b>Content</a><a href="https://krash9.github.io/meta-ai-video-factory/analytics.html?v=navfix2"><b>▥</b>Analytics</a><a href="https://krash9.github.io/meta-ai-video-factory/history.html?v=navfix2"><b>↗</b>History</a></nav><script>
const key='quiet-place-publication-tracker-v1';let data={};try{data=JSON.parse(localStorage.getItem(key)||'{}')||{};}catch(e){}if(!data['archive-20261108-coastal-sunset']){data['archive-20261108-coastal-sunset']={date:'2026-11-08',time:'01:57',video:'Archive',title:'Coastal sunset',url:'https://vm.tiktok.com/ZN85xQcuy/',views:788,likes:43,comments:3,shares:1,saves:2,status:'published',updatedAt:'Imported from user-provided TikTok Studio screenshot'};localStorage.setItem(key,JSON.stringify(data));}
document.querySelectorAll('.copy,.copy-post').forEach(b=>b.addEventListener('click',async()=>{const value=JSON.parse(b.dataset.prompt||b.dataset.post);try{if(navigator.clipboard&&isSecureContext)await navigator.clipboard.writeText(value);else{const t=document.createElement('textarea');t.value=value;document.body.appendChild(t);t.select();if(!document.execCommand('copy'))throw Error();t.remove();}document.getElementById('status').textContent='Copied ✓';}catch(e){document.getElementById('status').textContent='Copy blocked by browser. Try again.';}}));
document.querySelectorAll('.tracker').forEach(card=>{const id=card.dataset.date+'-video-'+card.dataset.video,old=data[id]||{};card.querySelectorAll('[data-field]').forEach(f=>{if(old[f.dataset.field]!==undefined)f.value=old[f.dataset.field];});if(old.updatedAt)card.querySelector('.saved-note').textContent='Saved '+old.updatedAt;card.querySelector('.save-record').addEventListener('click',()=>{const r={date:card.dataset.date,video:card.dataset.video};card.querySelectorAll('[data-field]').forEach(f=>r[f.dataset.field]=f.value);r.updatedAt=new Date().toLocaleString();data[id]=r;try{localStorage.setItem(key,JSON.stringify(data));card.querySelector('.saved-note').textContent='Saved '+r.updatedAt;}catch(e){card.querySelector('.saved-note').textContent='Could not save';}});});
</script></body></html>"""
content_page = content_page.replace("DATE_PLACEHOLDER", today.isoformat())
content_page = content_page.replace("PROMPT_UPDATED_AT_PLACEHOLDER", generated_at.strftime("%d %b %Y · %H:%M:%S"))
CONTENT_FILE.write_text(content_page, encoding="utf-8")

# Dedicated history page, sharing the same browser-local tracker store as the daily studio.
history_page = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Quiet Place — Publication History</title>
<style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;padding:20px;background:#101110;color:#f3f3ef;font:15px/1.5 system-ui,-apple-system,sans-serif}
main{max-width:760px;margin:auto}.muted,small{color:#a1a1a1}.eyebrow{font-size:12px;letter-spacing:.12em;color:#ff9a52;font-weight:700}
h1{font-size:27px;margin:8px 0}h2{font-size:19px;margin:8px 0 14px}
a{color:#ffb17b}.back{display:inline-block;margin:8px 0 18px;text-decoration:none}
.history-actions{display:flex;flex-wrap:wrap;gap:10px;margin:12px 0 18px}.history-actions .back{margin:0;padding:10px 13px;border:1px solid #57351e;border-radius:10px;text-decoration:none}.history-actions .primary-back{background:#ff7a24;color:#1a1009;border-color:#ff7a24;font-weight:700}\n.panel,.entry{background:#191919;border:1px solid #303030;border-radius:15px;padding:16px;margin:14px 0}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.metric{background:#101010;border-radius:10px;padding:12px}.metric strong{display:block;font-size:22px}.metric span{font-size:12px;color:#a8aaa4}
.controls{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}.controls select,.controls button{background:#303030;color:#f3f3ef;border:1px solid #494949;border-radius:9px;padding:10px;font:inherit}
.entry h3{font-size:16px;margin:5px 0 8px}.meta{font-size:12px;color:#a8aaa4}.stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px;margin:12px 0}.stats div{background:#101010;padding:8px;border-radius:8px;font-size:12px}.stats b{display:block;font-size:16px}
.pill{display:inline-block;border:1px solid #61432e;border-radius:20px;padding:2px 8px;font-size:11px;color:#ffb17b}
.empty{padding:20px;text-align:center;color:#a8aaa4}.danger{color:#e6b4a9}.url{overflow-wrap:anywhere}.record-actions{display:flex;gap:8px;margin-top:14px}.record-actions button{flex:1;padding:10px;border-radius:9px;border:1px solid #494949;background:#303030;color:#f3f3ef;font:inherit}.record-actions .delete-record{border-color:#75433b;color:#ffb5a8}.edit-form{display:none;margin-top:12px;padding:12px;background:#101010;border:1px solid #494949;border-radius:10px;gap:9px}.edit-form.open{display:grid}.edit-form label{display:grid;gap:4px;color:#aaa;font-size:12px}.edit-form input,.edit-form select{width:100%;padding:10px;background:#191919;color:#fff;border:1px solid #494949;border-radius:8px;font:inherit}.edit-form .edit-actions{display:flex;gap:8px}.edit-form button{flex:1;padding:11px;border:0;border-radius:8px;background:#ff9a52;color:#1a1009;font-weight:700}.edit-form .cancel-edit{background:#333;color:#fff}
.bottom-nav{position:fixed;bottom:0;left:0;right:0;background:#151515;display:grid;grid-template-columns:repeat(5,1fr);padding:10px 4px;z-index:20}.bottom-nav a{text-align:center;color:#999;text-decoration:none;font-size:11px;padding:6px 1px}.bottom-nav b{display:block;font-size:18px}.bottom-nav .active{color:#ff7a24}</style></head><body><main>
<div class="eyebrow">QUIET PLACE · LEAVE THE NOISE BEHIND</div><h1>Publication History &amp; Analytics</h1>
<p class="muted">Your saved TikTok publication records, across daily content plans.</p>
<div class="history-actions"><a class="back" href="https://krash9.github.io/meta-ai-video-factory/index.html?v=navfix2">← Overview</a><a class="back primary-back" href="index.html#content">← Back to publications / Content Studio</a></div>
<section class="panel"><div class="eyebrow">CHANNEL OVERVIEW</div><h2>All saved publications</h2>
<div class="grid">
<div class="metric"><strong id="count">0</strong><span>Publications tracked</span></div>
<div class="metric"><strong id="views">0</strong><span>Total views</span></div>
<div class="metric"><strong id="likes">0</strong><span>Total likes</span></div>
<div class="metric"><strong id="engagement">0</strong><span>Interactions (likes + comments + shares)</span></div>
</div></section>
<section class="panel"><h2>Add an older TikTok publication</h2>
<p class="muted">Enter a link and the current or historical statistics. This record will be added to your publication archive.</p>
<div class="controls" style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr))">
<label>Publication date<input id="old-date" type="date" style="width:100%;padding:10px;background:#101010;color:#f3f3ef;border:1px solid #494949;border-radius:9px"></label>
<label>Video title / scene<input id="old-title" type="text" placeholder="e.g. Rainy forest" style="width:100%;padding:10px;background:#101010;color:#f3f3ef;border:1px solid #494949;border-radius:9px"></label>
<label style="grid-column:1/-1">TikTok video URL<input id="old-url" type="url" placeholder="https://www.tiktok.com/..." style="width:100%;padding:10px;background:#101010;color:#f3f3ef;border:1px solid #494949;border-radius:9px"></label>
<label>Views<input id="old-views" type="number" min="0" value="0" style="width:100%;padding:10px;background:#101010;color:#f3f3ef;border:1px solid #494949;border-radius:9px"></label>
<label>Likes<input id="old-likes" type="number" min="0" value="0" style="width:100%;padding:10px;background:#101010;color:#f3f3ef;border:1px solid #494949;border-radius:9px"></label>
<label>Comments<input id="old-comments" type="number" min="0" value="0" style="width:100%;padding:10px;background:#101010;color:#f3f3ef;border:1px solid #494949;border-radius:9px"></label>
<label>Shares<input id="old-shares" type="number" min="0" value="0" style="width:100%;padding:10px;background:#101010;color:#f3f3ef;border:1px solid #494949;border-radius:9px"></label>
<label>Favorites / saves<input id="old-saves" type="number" min="0" value="0" style="width:100%;padding:10px;background:#101010;color:#f3f3ef;border:1px solid #494949;border-radius:9px"></label>
</div>
<button id="add-old" type="button" style="width:100%;padding:13px;background:#ff9a52;color:#1a1009;border:0;border-radius:10px;font-weight:700">Add to publication history</button>
<p id="add-message" class="muted" aria-live="polite"></p></section>
<section class="panel"><h2>Browse records</h2><div class="controls">
<select id="sort"><option value="newest">Newest first</option><option value="views">Most views</option><option value="likes">Most likes</option></select>
<select id="status"><option value="all">All statuses</option><option value="published">Published</option><option value="created">Created</option><option value="checked">Quality checked</option><option value="planned">Planned</option></select>
</div><div id="records"></div></section>
<p class="muted">Data is read from the same browser storage as Daily Content Studio. It stays on this device and browser; clearing site data or switching devices can remove or hide it. Export CSV from the studio regularly as a backup.</p>
</main><nav class="bottom-nav"><a href="https://krash9.github.io/meta-ai-video-factory/index.html?v=navfix2"><b>⌂</b>Overview</a><a href="https://krash9.github.io/meta-ai-video-factory/calendar.html?v=navfix2"><b>▦</b>Calendar</a><a href="https://krash9.github.io/meta-ai-video-factory/content.html?v=navfix2"><b>▤</b>Content</a><a href="https://krash9.github.io/meta-ai-video-factory/analytics.html?v=navfix2"><b>▥</b>Analytics</a><a class="active" href="https://krash9.github.io/meta-ai-video-factory/history.html?v=navfix2"><b>↗</b>History</a></nav><script>
const key='quiet-place-publication-tracker-v1';let data={};
try{data=JSON.parse(localStorage.getItem(key)||'{}')||{};}catch(e){data={};}
if(!data['archive-20261108-coastal-sunset']){data['archive-20261108-coastal-sunset']={date:'2026-11-08',time:'01:57',video:'Archive',title:'Coastal sunset',url:'https://vm.tiktok.com/ZN85xQcuy/',views:788,likes:43,comments:3,shares:1,saves:2,status:'published',updatedAt:'Imported from user-provided TikTok Studio screenshot'};localStorage.setItem(key,JSON.stringify(data));}
const fmt=n=>Number(n||0).toLocaleString();
document.getElementById('old-date').value=new Date().toISOString().slice(0,10);
document.getElementById('add-old').addEventListener('click',()=>{
 const date=document.getElementById('old-date').value;
 const url=document.getElementById('old-url').value.trim();
 if(!date||!url){document.getElementById('add-message').textContent='Please enter the publication date and TikTok URL.';return;}
 try{new URL(url);}catch(e){document.getElementById('add-message').textContent='Please enter a valid URL.';return;}
 const id='archive-'+Date.now();
 data[id]={date,video:'Archive',title:document.getElementById('old-title').value.trim()||'Older TikTok publication',url,
 views:document.getElementById('old-views').value||0,likes:document.getElementById('old-likes').value||0,
 comments:document.getElementById('old-comments').value||0,shares:document.getElementById('old-shares').value||0,saves:document.getElementById('old-saves').value||0,
 status:'published',updatedAt:new Date().toLocaleString()};
 try{localStorage.setItem(key,JSON.stringify(data));document.getElementById('add-message').textContent='Publication added to history.';location.reload();}
 catch(e){document.getElementById('add-message').textContent='Could not save. Browser storage may be full or unavailable.';}
});
function getRecords(){return Object.entries(data).map(([id,r])=>({...r,_id:id})).sort((a,b)=>(b.date||'').localeCompare(a.date||'')||String(b.video||'').localeCompare(String(a.video||'')));}
const sum=k=>getRecords().reduce((s,r)=>s+Number(r[k]||0),0);
function refreshSummary(){const rs=getRecords();document.getElementById('count').textContent=rs.length;document.getElementById('views').textContent=fmt(sum('views'));document.getElementById('likes').textContent=fmt(sum('likes'));document.getElementById('engagement').textContent=fmt(sum('likes')+sum('comments')+sum('shares'));}
const esc=v=>String(v??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
function render(){
 const sort=document.getElementById('sort').value,status=document.getElementById('status').value;
 let list=getRecords().filter(r=>status==='all'||(r.status||'planned')===status);
 if(sort==='views')list.sort((a,b)=>Number(b.views||0)-Number(a.views||0));
 if(sort==='likes')list.sort((a,b)=>Number(b.likes||0)-Number(a.likes||0));
 const root=document.getElementById('records');
 if(!list.length){root.innerHTML='<div class="empty">No saved publication records yet. Save a video in Daily Content Studio and it will appear here.</div>';return;}
 root.innerHTML=list.map(r=>{
 const statusLabel=(r.status||'planned').replace('checked','quality checked');
 const link=r.url?'<p class="url"><a href="'+esc(r.url)+'" target="_blank" rel="noopener">Open TikTok publication ↗</a></p>':'<p class="meta">No TikTok URL saved</p>';
 return '<article class="entry" data-record-id="'+esc(r._id)+'"><div class="meta">'+esc(r.date||'Date not set')+(r.time?' · '+esc(r.time):'')+' · Video '+esc(r.video||'?')+'</div><h3>'+esc(r.title||'Quiet Place publication')+'</h3><span class="pill">'+esc(statusLabel)+'</span>'+link+
 '<div class="stats"><div><b>'+fmt(r.views)+'</b>Views</div><div><b>'+fmt(r.likes)+'</b>Likes</div><div><b>'+fmt(r.comments)+'</b>Comments</div><div><b>'+fmt(r.shares)+'</b>Shares</div><div><b>'+fmt(r.saves)+'</b>Favorites</div></div><div class="meta">Last saved: '+esc(r.updatedAt||'—')+'</div>'+
 '<div class="record-actions"><button type="button" class="edit-record">Edit</button><button type="button" class="delete-record">Delete</button></div>'+
 '<form class="edit-form"><label>Publication date<input name="date" type="date" value="'+esc(r.date||'')+'" required></label><label>Title / scene<input name="title" type="text" value="'+esc(r.title||'Quiet Place publication')+'"></label><label>TikTok URL<input name="url" type="url" value="'+esc(r.url||'')+'"></label><label>Status<select name="status"><option value="planned" '+((r.status||'planned')==='planned'?'selected':'')+'>Planned</option><option value="created" '+(r.status==='created'?'selected':'')+'>Created</option><option value="checked" '+(r.status==='checked'?'selected':'')+'>Quality checked</option><option value="published" '+(r.status==='published'?'selected':'')+'>Published</option></select></label><div class="grid"><label>Views<input name="views" type="number" min="0" value="'+esc(r.views||0)+'"></label><label>Likes<input name="likes" type="number" min="0" value="'+esc(r.likes||0)+'"></label><label>Comments<input name="comments" type="number" min="0" value="'+esc(r.comments||0)+'"></label><label>Shares<input name="shares" type="number" min="0" value="'+esc(r.shares||0)+'"></label><label>Favorites / saves<input name="saves" type="number" min="0" value="'+esc(r.saves||0)+'"></label></div><div class="edit-actions"><button type="submit">Save changes</button><button type="button" class="cancel-edit">Cancel</button></div></form></article>';
 }).join('');
 root.querySelectorAll('.entry').forEach(card=>{
  const id=card.dataset.recordId,form=card.querySelector('.edit-form');
  card.querySelector('.edit-record').addEventListener('click',()=>form.classList.toggle('open'));
  card.querySelector('.cancel-edit').addEventListener('click',()=>form.classList.remove('open'));
  form.addEventListener('submit',e=>{
   e.preventDefault();const fd=new FormData(form),old=data[id]||{};
   const updated={...old,date:fd.get('date'),title:fd.get('title').trim(),url:fd.get('url').trim(),status:fd.get('status'),views:fd.get('views')||0,likes:fd.get('likes')||0,comments:fd.get('comments')||0,shares:fd.get('shares')||0,saves:fd.get('saves')||0,updatedAt:new Date().toLocaleString()};
   if(updated.url){try{new URL(updated.url);}catch(err){alert('Enter a valid publication URL or leave it empty.');return;}}
   data[id]=updated;
   try{localStorage.setItem(key,JSON.stringify(data));refreshSummary();render();}
   catch(err){alert('Could not save changes. Browser storage may be unavailable.');}
  });
  card.querySelector('.delete-record').addEventListener('click',()=>{
   if(!confirm('Delete this publication record permanently from this browser?'))return;
   delete data[id];
   try{localStorage.setItem(key,JSON.stringify(data));refreshSummary();render();}
   catch(err){alert('Could not delete the record. Browser storage may be unavailable.');}
  });
 });
}
document.getElementById('sort').addEventListener('change',render);
document.getElementById('status').addEventListener('change',render);
refreshSummary();render();
</script></body></html>"""
HISTORY_FILE.write_text(history_page, encoding="utf-8")
calendar_page = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Quiet Place Calendar</title><style>:root{color-scheme:dark}body{margin:0;background:#090909;color:#f5f5f5;font:15px system-ui;padding:20px 16px 90px}main{max-width:700px;margin:auto}.panel{background:#191919;border:1px solid #333;border-radius:16px;padding:16px}.head{display:flex;justify-content:space-between;align-items:center}.head button{background:#333;color:white;padding:10px;border:0;border-radius:8px}.grid{display:grid;grid-template-columns:repeat(7,1fr);gap:5px;text-align:center}.day{padding:9px 1px;background:#101010;color:white;border:1px solid #333;border-radius:8px}.day.has{border-color:#ff7a24;color:#ff9a52}.day.sel{background:#ff7a24;color:#111}.bottom-nav{position:fixed;bottom:0;left:0;right:0;background:#151515;display:grid;grid-template-columns:repeat(5,1fr);padding:10px 4px}.bottom-nav a{text-align:center;color:#999;text-decoration:none;font-size:11px}.bottom-nav b{display:block;font-size:18px}.bottom-nav .active{color:#ff7a24}</style></head><body><main><h1>Publication Calendar</h1><section class="panel"><div class="head"><button id="prev">‹</button><h2 id="month"></h2><button id="next">›</button></div><div class="grid" id="grid"></div><h3 id="date"></h3><div id="items"></div></section></main><nav class="bottom-nav"><a href="https://krash9.github.io/meta-ai-video-factory/index.html?v=navfix2"><b>⌂</b>Overview</a><a class="active" href="https://krash9.github.io/meta-ai-video-factory/calendar.html?v=navfix2"><b>▦</b>Calendar</a><a href="https://krash9.github.io/meta-ai-video-factory/content.html?v=navfix2"><b>▤</b>Content</a><a href="https://krash9.github.io/meta-ai-video-factory/analytics.html?v=navfix2"><b>▥</b>Analytics</a><a href="https://krash9.github.io/meta-ai-video-factory/history.html?v=navfix2"><b>↗</b>History</a></nav><script>let d={};try{d=JSON.parse(localStorage.getItem('quiet-place-publication-tracker-v1')||'{}')}catch(e){}if(!d['archive-20261108-coastal-sunset']){d['archive-20261108-coastal-sunset']={date:'2026-11-08',time:'01:57',video:'Archive',title:'Coastal sunset',url:'https://vm.tiktok.com/ZN85xQcuy/',views:788,likes:43,comments:3,shares:1,saves:2,status:'published',updatedAt:'Imported from user-provided TikTok Studio screenshot'};localStorage.setItem('quiet-place-publication-tracker-v1',JSON.stringify(d));}let rs=Object.values(d),m=new Date();m.setDate(1);let sel=new Date().toISOString().slice(0,10);function draw(){let y=m.getFullYear(),mo=m.getMonth(),g=document.getElementById('grid');document.getElementById('month').textContent=m.toLocaleDateString('en',{month:'long',year:'numeric'});g.innerHTML=['M','T','W','T','F','S','S'].map(x=>'<span>'+x+'</span>').join('');for(let i=0;i<(new Date(y,mo,1).getDay()+6)%7;i++)g.innerHTML+='<i></i>';for(let n=1;n<=new Date(y,mo+1,0).getDate();n++){let dt=y+'-'+String(mo+1).padStart(2,'0')+'-'+String(n).padStart(2,'0'),b=document.createElement('button');b.textContent=n;b.className='day'+(rs.some(r=>r.date===dt)?' has':'')+(dt===sel?' sel':'');b.onclick=()=>{sel=dt;draw()};g.append(b)}document.getElementById('date').textContent=sel;let a=rs.filter(r=>r.date===sel);document.getElementById('items').innerHTML=a.length?a.map(r=>'<p>'+(r.time?r.time+' · ':'')+(r.title||('Video '+r.video))+' — '+Number(r.views||0).toLocaleString()+' views</p>').join(''):'<p>No publications saved for this date.</p>'}document.getElementById('prev').onclick=()=>{m.setMonth(m.getMonth()-1);draw()};document.getElementById('next').onclick=()=>{m.setMonth(m.getMonth()+1);draw()};draw();</script></body></html>"""
CALENDAR_FILE.write_text(calendar_page, encoding="utf-8")
analytics_page = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Quiet Place Analytics</title><style>:root{color-scheme:dark}body{margin:0;background:#090909;color:#f5f5f5;font:15px system-ui;padding:20px 16px 90px}main{max-width:700px;margin:auto}.panel{background:#191919;border:1px solid #333;border-radius:16px;padding:16px;margin:14px 0}.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:8px}.metric{background:#101010;padding:14px;border-radius:10px}.metric b{display:block;font-size:23px}.bottom-nav{position:fixed;bottom:0;left:0;right:0;background:#151515;display:grid;grid-template-columns:repeat(5,1fr);padding:10px 4px}.bottom-nav a{text-align:center;color:#999;text-decoration:none;font-size:11px}.bottom-nav b{display:block;font-size:18px}.bottom-nav .active{color:#ff7a24}</style></head><body><main><h1>Analytics</h1><section class="panel"><div class="grid"><div class="metric"><b id="views">0</b>Views</div><div class="metric"><b id="likes">0</b>Likes</div><div class="metric"><b id="comments">0</b>Comments</div><div class="metric"><b id="shares">0</b>Shares</div></div></section><section class="panel"><h2>Top publications</h2><div id="top"></div></section></main><nav class="bottom-nav"><a href="https://krash9.github.io/meta-ai-video-factory/index.html?v=navfix2"><b>⌂</b>Overview</a><a href="https://krash9.github.io/meta-ai-video-factory/calendar.html?v=navfix2"><b>▦</b>Calendar</a><a href="https://krash9.github.io/meta-ai-video-factory/content.html?v=navfix2"><b>▤</b>Content</a><a class="active" href="https://krash9.github.io/meta-ai-video-factory/analytics.html?v=navfix2"><b>▥</b>Analytics</a><a href="https://krash9.github.io/meta-ai-video-factory/history.html?v=navfix2"><b>↗</b>History</a></nav><script>let d={};try{d=JSON.parse(localStorage.getItem('quiet-place-publication-tracker-v1')||'{}')}catch(e){}let rs=Object.values(d),f=n=>Number(n||0).toLocaleString();['views','likes','comments','shares'].forEach(k=>document.getElementById(k).textContent=f(rs.reduce((s,r)=>s+Number(r[k]||0),0)));document.getElementById('top').innerHTML=rs.sort((a,b)=>b.views-a.views).slice(0,10).map(r=>'<p>'+(r.title||('Video '+r.video))+' — '+f(r.views)+' views</p>').join('')||'No saved publications yet.';</script></body></html>"""
ANALYTICS_FILE.write_text(analytics_page, encoding="utf-8")



print(f"Quiet Place package created: {OUTPUT_DIR}")
print(f"Date: {today.isoformat()}")
print("Videos planned: 3")
for index, (category, scene) in enumerate(selected, start=1):
    print(f"{index}. {category}: {scene}")
