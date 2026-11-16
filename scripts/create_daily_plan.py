from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import random
import sys
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
if "--scheduled" in sys.argv and generated_at.hour < 5:
    print(f"Scheduled run started early at {generated_at:%H:%M}; refusing to generate before 05:00 Warsaw time.")
    raise SystemExit(1)
if "--scheduled" in sys.argv and generated_at.hour > 5:
    print(f"GitHub scheduled job started late at {generated_at:%H:%M}; generating now rather than silently skipping the day.")
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
    """Write a short, image-rich micro-story grounded in the actual scene."""
    text = scene.lower()
    seed = sum(ord(char) for char in scene)
    
    if "stone footbridge" in text and "river" in text:
        return (
            "The old stone bridge has watched every summer turn into autumn. "
            "But the river remembers nothing; it simply carries the fallen leaves onward, "
            "slowly, without hurry. Perhaps that is its quiet wisdom: knowing when to let things go. 🍂"
        )
    if any(word in text for word in ("lake", "shoreline", "reed-lined", "pebble beach", "tide", "driftwood", "wooden pier")):
        stories = [
            "The water keeps the colour of the November sky, while the shore gathers the leaves the wind has left behind. "
            "A small wave arrives, then slips away as if it has nowhere urgent to be. "
            "For a moment, the whole world seems content to move at this pace. 🌊",
            "There is a kind of quiet that only exists beside water. The breeze changes its surface, "
            "the reeds lean closer, and the distant shore slowly disappears into the grey. "
            "Nothing asks to be hurried here. 🍃",
            "The shoreline has no need to look perfect. A little driftwood, a restless tide and the soft November light are enough. "
            "The water comes and goes, leaving the day a little quieter than it found it. 🌫️"
        ]
        return stories[seed % len(stories)]
    if any(word in text for word in ("waterfall", "rock ledge", "water flowing", "river")):
        stories = [
            "The water has travelled farther than we can imagine, yet it never seems in a hurry. "
            "It slips over the old stones and disappears among the trees, carrying the forest's quiet with it. "
            "Some journeys are beautiful simply because they keep going. 💧",
            "Between the bare branches, the water finds its own gentle rhythm. "
            "It tumbles over the rocks, catches a little light, and carries on without looking back. "
            "The forest lets the moment pass in silence. 🍂"
        ]
        return stories[seed % len(stories)]
    if any(word in text for word in ("rain", "drops", "shower", "wet")) and any(word in text for word in ("leaf", "path", "pond", "window", "bench")):
        stories = [
            "The rain finds every leaf, every stone and every quiet corner of the path. "
            "Tiny drops gather, fall, and disappear into the earth as the afternoon slowly fades. "
            "Even an ordinary rainy day can hold a little wonder. 🌧️",
            "The last leaves are letting go, one raindrop at a time. "
            "The path darkens beneath them, while the forest listens to the soft rhythm overhead. "
            "There is nowhere else this moment needs to be. 🍂"
        ]
        return stories[seed % len(stories)]
    if any(word in text for word in ("forest", "woodland", "birch", "pine", "tree", "trees", "trail", "path")):
        stories = [
            "The trees have shed most of their colours, but the forest is far from empty. "
            "A branch moves in the breeze, a leaf crosses the path, and the quiet keeps unfolding. "
            "Autumn has its own way of making room for stillness. 🍁",
            "Every step along this path leaves the noise a little farther behind. "
            "Bare branches sway above the damp earth, while the last golden leaves hold on for another moment. "
            "The forest never asks us to hurry. 🌲",
            "The wind moves gently through the trees, stirring the few leaves still holding on. "
            "The path disappears around the bend, inviting no particular destination. "
            "Sometimes the loveliest part of a walk is simply being there. 🍃"
        ]
        return stories[seed % len(stories)]
    if any(word in text for word in ("cottage", "veranda", "cabin", "shelter", "outdoor table", "courtyard")):
        stories = [
            "Beyond the window, the autumn rain turns the garden into a soft blur of colour. "
            "Inside, the world feels distant and the afternoon seems to have nowhere else to go. "
            "Some places make doing nothing feel like enough. 🤍",
            "The little shelter stands quietly while the weather passes through. "
            "Rain touches the old stones, leaves gather by the doorway, and the day carries on at its own pace. "
            "It feels good to have nowhere to rush. 🍂"
        ]
        return stories[seed % len(stories)]
    if any(word in text for word in ("street", "village", "lane", "cobblestone", "bench", "park")):
        stories = [
            "The street is almost empty, its wet stones holding the last light of the day. "
            "A few leaves travel along the pavement, following a route no one planned. "
            "Even familiar places can feel like somewhere new when the world grows quiet. 🍁",
            "The old lane settles beneath the November sky. Bare branches frame the rooftops, "
            "and the rain leaves small reflections where footsteps have passed. "
            "For once, there is no reason to take the shortest way home. 🏡"
        ]
        return stories[seed % len(stories)]
    
    clean = scene.strip().rstrip(".")
    opening = clean[0].upper() + clean[1:] if clean else "The quiet moment"
    return (
        f"{opening}. The smallest details seem to move a little slower here, "
        "as if the day has made room for one more breath. "
        "Nothing needs to happen for this moment to matter. 🤍"
    )

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
    scene_options = []
    # Build a large pool of fresh, season-aware combinations for the per-card refresh control.
    framing_by_category = {
        "Nature & Water": [
            "seen from close to the water's edge", "framed through softly blurred foreground reeds",
            "with a broad natural view and layered depth", "from beside a weathered shoreline",
            "with the main water feature slightly off-centre"
        ],
        "Forest & Weather": [
            "seen from a quiet path-level viewpoint", "framed between natural tree trunks",
            "with a clear foreground of damp leaves", "looking gently into the woodland depth",
            "from beside a mossy tree and the forest floor"
        ],
        "Cozy Quiet Places": [
            "seen from a sheltered, human-height viewpoint", "framed by a simple doorway or window",
            "with a quiet foreground detail and soft depth", "from the edge of a peaceful garden",
            "with the architecture naturally balanced in the frame"
        ],
    }
    detail_by_category = {
        "Nature & Water": [
            "subtle reflections moving across the surface", "small leaves gathering near the edge",
            "gentle ripples catching the available light", "weathered stones and natural textures",
            "soft movement in nearby grasses"
        ],
        "Forest & Weather": [
            "tiny droplets clinging to branches", "fallen leaves scattered across the ground",
            "soft movement in thin branches", "moss and bark textures in the foreground",
            "a few leaves drifting naturally in the breeze"
        ],
        "Cozy Quiet Places": [
            "wet stone textures and a few fallen leaves", "soft reflections in a nearby window",
            "a small natural detail moving gently in the breeze", "warm wood grain and quiet garden textures",
            "subtle rain marks and natural imperfections"
        ],
    }
    variant_rng = random.Random(f"{date_seed}:{item['category']}:{item['index']}:refresh-pool")
    seen = {item["scene"]}
    for base in categories[item["category"]]:
        for framing in framing_by_category[item["category"]]:
            for detail in detail_by_category[item["category"]]:
                candidate = f"{base}, {framing}, with {detail}"
                if candidate in seen:
                    continue
                seen.add(candidate)
                scene_options.append({
                    "scene": candidate,
                    "prompt": build_prompt(candidate, camera_approaches[item["index"] - 1]),
                    "caption": build_caption(item["category"], candidate),
                    "hashtags": build_hashtags(item["category"], candidate),
                })
    variant_rng.shuffle(scene_options)
    scene_options = scene_options[:160]
    prompt_options_json = json.dumps(scene_options, ensure_ascii=False).replace("</", "<\\/")
    prompt_json = json.dumps(item["prompt"], ensure_ascii=False).replace("</", "<\\/")
    post_json = json.dumps(item["caption"] + "\n\n" + item["hashtags"], ensure_ascii=False)
    cards.append(
        f"""
        <article class="card" style="position:relative">
          <span class="prompt-options" hidden data-prompt-options='{escape(prompt_options_json, quote=True)}'></span>
          <div class="card-head"><div><div class="eyebrow">VIDEO {item["index"]} · {escape(item["category"])}</div><h2>{escape(item["scene"])}</h2></div></div>
          <div class="prompt-meta"><span class="prompt-time">Prompt updated: {escape(generated_at_label)} Warsaw time</span></div>
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
          <button class="prompt-refresh" type="button" style="display:block!important;visibility:visible!important;opacity:1!important;width:100%!important;min-height:48px!important;margin:16px 0 0!important;padding:14px!important;background:#ff9a52!important;color:#1a1009!important;border:0!important;border-radius:11px!important;font-size:15px!important;font-weight:900!important;letter-spacing:.08em!important;cursor:pointer!important">UPDATE</button>
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
.card-refresh-confirm{display:block;opacity:0;transform:translateY(-8px);background:#21170f;border:1px solid #70451f;border-radius:12px;padding:13px;margin:12px 0 4px;transition:opacity .24s ease,transform .24s ease}.card-refresh-confirm.visible{display:block;animation:refreshIn .24s ease forwards}.card-refresh-confirm.closing{opacity:0;transform:translateY(-8px)}.card-refresh-confirm.success{border-color:#b56a32}.card-refresh-confirm p{font-size:12px;color:#c7b9ad;margin:6px 0 10px}.card-refresh-actions{display:grid;grid-template-columns:1fr;gap:7px}.card-refresh-actions button{background:#333;color:#fff;padding:10px}.card-refresh-actions button[data-choice=yes]{display:block!important;width:100%!important;min-height:48px!important;background:#ff9a52!important;color:#1a1009!important;opacity:1!important;visibility:visible!important;pointer-events:auto!important;cursor:pointer!important}.card-refresh-actions button[data-choice=cancel]{grid-column:1/-1;background:transparent;border:1px solid #555;color:#bbb}@keyframes refreshIn{to{opacity:1;transform:translateY(0)}}@media(prefers-reduced-motion:reduce){.card-refresh-confirm{animation:none!important;transition:none!important}}.card{position:relative}.card-head{display:block;padding-right:0;min-height:34px}.card-head h2{margin:5px 0 0}.force-refresh{position:absolute!important;top:14px!important;right:14px!important;z-index:3!important;flex:0 0 34px;width:34px;height:34px;padding:0!important;margin:0!important;background:transparent!important;color:#ffad72;border:0!important;border-radius:0!important;box-shadow:none!important;font-size:25px;line-height:1;opacity:.9}.prompt-meta{display:flex;gap:7px;align-items:center;margin:10px 0 2px;color:#aaa;font-size:11px}.refresh-star.active:before{content:'🌟'}.confirm-backdrop{display:none;position:fixed;inset:0;z-index:100;background:#000b;align-items:center;justify-content:center;padding:20px}.confirm-backdrop.open{display:flex}.confirm-box{width:min(100%,420px);background:#202020;border:1px solid #5a3b25;border-radius:16px;padding:20px}.confirm-box p{color:#bbb;font-size:13px}.confirm-actions{display:grid;grid-template-columns:1fr 1fr;gap:8px}.confirm-actions button{background:#333;color:#fff}.confirm-actions [data-action=yes]{background:#ff9a52;color:#1a1009}.confirm-actions [data-action=cancel]{grid-column:1/-1;background:transparent;border:1px solid #555;color:#bbb}</style></head><body><main>
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

""" + """
<p class="note">Generate and save videos in Meta AI, then upload them manually in TikTok. Check TikTok's AI disclosure setting for realistic generated scenes.</p>
</section>
<section id="calendar" class="view"><h1>Publication Calendar</h1><p class="muted">Choose a date to see videos published or tracked on that day.</p>
<div class="panel"><div class="section-head"><button id="month-prev" class="action action-secondary" type="button">‹</button><h2 id="month-label">Month</h2><button id="month-next" class="action action-secondary" type="button">›</button></div>
<div class="calendar-grid" id="calendar-grid"></div><div class="section-head"><h2 id="selected-date-label">Selected date</h2><small id="selected-count">0 publications</small></div><div id="calendar-list"></div></div></section>
<section id="analytics" class="view"><h1>Analytics</h1><p class="muted">Compare saved performance across all publications.</p><div class="panel"><div class="kpis"><div class="metric"><strong id="a-views">0</strong><span>Total views</span></div><div class="metric"><strong id="a-likes">0</strong><span>Total likes</span></div><div class="metric"><strong id="a-comments">0</strong><span>Comments</span></div><div class="metric"><strong id="a-shares">0</strong><span>Shares</span></div><div class="metric"><strong id="a-saves">0</strong><span>Favorites</span></div></div><div class="section-head"><h2>Top publications</h2><small>By views</small></div><div id="top-posts"></div><button id="export-csv" class="action action-primary" type="button" style="width:100%;margin-top:16px">Export tracking CSV</button></div><a class="history-link" href="https://krash9.github.io/meta-ai-video-factory/history.html?v=navfix2">OPEN FULL HISTORY ↗</a></section>
</main>
<nav class="nav"><div class="nav-inner"><a class="active" href="https://krash9.github.io/meta-ai-video-factory/index.html?v=navfix2"><span class="nav-icon">⌂</span>Overview</a><a href="https://krash9.github.io/meta-ai-video-factory/calendar.html?v=navfix2"><span class="nav-icon">▦</span>Calendar</a><a href="https://krash9.github.io/meta-ai-video-factory/content.html?v=navfix2"><span class="nav-icon">▤</span>Content</a><a href="https://krash9.github.io/meta-ai-video-factory/analytics.html?v=navfix2"><span class="nav-icon">▥</span>Analytics</a><a href="https://krash9.github.io/meta-ai-video-factory/history.html?v=navfix2"><span class="nav-icon">↗</span>History</a></div></nav>
<script>
function setupPromptRefresh(){
 const stateKey='quiet-place-prompt-refresh-v9';
 const legacyKeys=['quiet-place-prompt-refresh-v1','quiet-place-prompt-refresh-v2','quiet-place-prompt-refresh-v3','quiet-place-prompt-refresh-v4','quiet-place-prompt-refresh-v5','quiet-place-prompt-refresh-v6','quiet-place-prompt-refresh-v7','quiet-place-prompt-refresh-v8'];
 let states={};
 const readStore=key=>{try{return JSON.parse(localStorage.getItem(key)||'{}')||{};}catch(e){return {};}};
 states=readStore(stateKey);
 for(const legacyKey of legacyKeys){
  const legacy=readStore(legacyKey);
  for(const [id,value] of Object.entries(legacy)){
   if(states[id])continue;
   const current=value&&value.current?value.current:value;
   if(current&&current.prompt){
    states[id]={current,usedScenes:Array.isArray(value.usedScenes)?value.usedScenes:(current.scene?[current.scene]:[])};
   }
  }
 }
 try{localStorage.setItem(stateKey,JSON.stringify(states));}catch(e){}
 document.querySelectorAll('.prompt-refresh').forEach(button=>{
  const card=button.closest('.card');
  const source=card&&card.querySelector('.prompt-options');
  const copy=card&&card.querySelector('.copy');
  const tracker=card&&card.querySelector('.tracker');
  const meta=card&&card.querySelector('.prompt-meta');
  const time=meta&&meta.querySelector('.prompt-time');
  const title=card&&card.querySelector('h2');
  const caption=card&&card.querySelector('.caption');
  const tags=card&&card.querySelector('.tags');
  const post=card&&card.querySelector('.copy-post');
  if(!card||!source||!copy||!tracker||!meta||!time||!title||!caption||!tags||!post){
   button.disabled=true;
   button.textContent='UNAVAILABLE';
   return;
  }
  const key=tracker.dataset.date+'-video-'+tracker.dataset.video;
  let options=[];
  try{options=JSON.parse(source.getAttribute('data-prompt-options')||'[]');}catch(e){options=[];}
  const panel=document.createElement('section');
  panel.className='prompt-refresh-confirm';
  panel.style.cssText='display:none;margin:12px 0 0;padding:14px;background:#21170f;border:1px solid #70451f;border-radius:12px';
  panel.innerHTML='<strong>Update this prompt?</strong><p style="margin:6px 0 12px;color:#c7b9ad;font-size:13px">The current scene, Meta AI prompt, caption and hashtags will be replaced. This cannot be undone from this card.</p><div style="display:grid;grid-template-columns:1fr 1fr;gap:8px"><button type="button" data-confirm-update style="margin:0;background:#ff9a52;color:#1a1009">CONFIRM UPDATE</button><button type="button" data-cancel-update style="margin:0;background:#333;color:#fff">CANCEL</button></div>';
  button.insertAdjacentElement('afterend',panel);
  const status=document.createElement('p');
  status.setAttribute('aria-live','polite');
  status.style.cssText='margin:10px 0 0;font-size:12px;color:#aaa;min-height:18px';
  panel.appendChild(status);
  const apply=(item,stamp)=>{
   copy.dataset.prompt=JSON.stringify(item.prompt);
   title.textContent=item.scene;
   caption.textContent=item.caption;
   const hashtags=item.hashtags||item.tags||'';
   tags.textContent=hashtags;
   post.dataset.post=JSON.stringify(item.caption+String.fromCharCode(10,10)+hashtags);
   time.textContent='Prompt updated: '+stamp+' Warsaw time';
  };
  const saved=states[key];
  if(saved&&saved.current&&saved.current.prompt)apply(saved.current,saved.current.updatedAt||'Previously updated');
  button.type='button';
  button.setAttribute('aria-expanded','false');
  button.addEventListener('click',()=>{
   if(button.disabled)return;
   panel.style.display=panel.style.display==='none'?'block':'none';
   button.setAttribute('aria-expanded',panel.style.display==='block'?'true':'false');
   if(panel.style.display==='block')status.textContent='Confirm only if you want to replace this card.';
  });
  panel.querySelector('[data-cancel-update]').addEventListener('click',()=>{
   panel.style.display='none';
   button.setAttribute('aria-expanded','false');
   status.textContent='Update cancelled. The current prompt is unchanged.';
  });
  panel.querySelector('[data-confirm-update]').addEventListener('click',()=>{
   const old=states[key]||{};
   const used=new Set(Array.isArray(old.usedScenes)?old.usedScenes:[]);
   used.add(title.textContent.trim());
   const available=options.filter(item=>item&&item.scene&&item.prompt&&!used.has(item.scene));
   if(!available.length){
    status.textContent='No unused scenes remain in this category.';
    return;
   }
   const next=available[Math.floor(Math.random()*available.length)];
   const stamp=new Date().toLocaleString('en-GB',{timeZone:'Europe/Warsaw'});
   const updated={...next,updatedAt:stamp};
   used.add(next.scene);
   const nextStates={...states,[key]:{current:updated,usedScenes:[...used]}};
   try{localStorage.setItem(stateKey,JSON.stringify(nextStates));}
   catch(error){
    status.textContent='Could not save. The current prompt has not been changed.';
    return;
   }
   states=nextStates;
   apply(updated,stamp);
   status.textContent='🌟 Prompt updated. New scene, Meta AI prompt and TikTok caption are ready.';
   panel.style.display='none';
   button.setAttribute('aria-expanded','false');
  });
 });
}
setupPromptRefresh();
const trackerKey='quiet-place-publication-tracker-v1';let trackerData={};
try{trackerData=JSON.parse(localStorage.getItem(trackerKey)||'{}')||{};}catch(e){trackerData={};}
if(!trackerData['archive-20261108-coastal-sunset']){trackerData['archive-20261108-coastal-sunset']={date:'2026-11-08',time:'01:57',video:'Archive',title:'Coastal sunset',url:'https://vm.tiktok.com/ZN85xQcuy/',views:788,likes:43,comments:3,shares:1,saves:2,status:'published',updatedAt:'Imported from user-provided TikTok Studio screenshot'};localStorage.setItem(trackerKey,JSON.stringify(trackerData));}
if(!trackerData['archive-20261108-waterfall-0215']){trackerData['archive-20261108-waterfall-0215']={date:'2026-11-08',time:'02:15',video:'Archive',title:'Forest waterfall',url:'https://vm.tiktok.com/ZN85xqVAV/',views:761,likes:32,comments:3,shares:1,saves:1,watchTime:'00:36:35',averageWatchTime:'2.8 s',fullWatchPercent:'5.16%',newFollowers:2,status:'published',updatedAt:'Imported from user-provided TikTok Studio screenshot'};localStorage.setItem(trackerKey,JSON.stringify(trackerData));}
if(!trackerData['archive-20261110-green-hills-1718']){trackerData['archive-20261110-green-hills-1718']={date:'2026-11-10',time:'17:18',video:'Archive',title:'Green hills',url:'https://vm.tiktok.com/ZN85xHMxN/',views:773,likes:52,comments:3,shares:1,saves:2,watchTime:'00:34:41',averageWatchTime:'2.6 s',fullWatchPercent:'4.2%',newFollowers:1,status:'published',updatedAt:'Imported from user-provided TikTok Studio screenshot'};localStorage.setItem(trackerKey,JSON.stringify(trackerData));}
if(!trackerData['archive-20261115-autumn-birch-1748']){trackerData['archive-20261115-autumn-birch-1748']={date:'2026-11-15',time:'17:48',video:'Archive',title:'Autumn birch forest',image:'data:image/jpeg;base64,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',url:'https://vm.tiktok.com/ZN85G9mPq/',views:683,likes:8,comments:0,shares:0,saves:0,watchTime:'00:23:36',averageWatchTime:'2.0 s',fullWatchPercent:'2.02%',newFollowers:0,duration:'10.01 s',status:'published',updatedAt:'Imported from user-provided TikTok Studio screenshot'};localStorage.setItem(trackerKey,JSON.stringify(trackerData));}
if(!trackerData['archive-20261115-autumn-birch-1851']){trackerData['archive-20261115-autumn-birch-1851']={date:'2026-11-15',time:'18:51',video:'Archive',title:'Dark Autumn Birch Forest',image:'data:image/jpeg;base64,B64_REPLACE',url:'https://vm.tiktok.com/ZN85GxxAM/',views:652,likes:17,comments:0,shares:0,saves:1,watchTime:'00:19:00',averageWatchTime:'1.7 s',fullWatchPercent:'2.25%',newFollowers:2,duration:'10.01 s',status:'published',updatedAt:'Imported from user-provided TikTok Studio screenshot'};localStorage.setItem(trackerKey,JSON.stringify(trackerData));}
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
setupPromptRefresh();
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
 const blob=new Blob([rows.join('\\n')],{type:'text/csv;charset=utf-8;'}),url=URL.createObjectURL(blob),a=document.createElement('a');
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

""" + """
</main><nav class="bottom-nav"><a href="https://krash9.github.io/meta-ai-video-factory/index.html?v=navfix2"><b>⌂</b>Overview</a><a href="https://krash9.github.io/meta-ai-video-factory/calendar.html?v=navfix2"><b>▦</b>Calendar</a><a class="active" href="https://krash9.github.io/meta-ai-video-factory/content.html?v=navfix2"><b>▤</b>Content</a><a href="https://krash9.github.io/meta-ai-video-factory/analytics.html?v=navfix2"><b>▥</b>Analytics</a><a href="https://krash9.github.io/meta-ai-video-factory/history.html?v=navfix2"><b>↗</b>History</a></nav><script>
function setupPromptRefresh(){
 const stateKey='quiet-place-prompt-refresh-v9';
 const legacyKeys=['quiet-place-prompt-refresh-v1','quiet-place-prompt-refresh-v2','quiet-place-prompt-refresh-v3','quiet-place-prompt-refresh-v4','quiet-place-prompt-refresh-v5','quiet-place-prompt-refresh-v6','quiet-place-prompt-refresh-v7','quiet-place-prompt-refresh-v8'];
 let states={};
 const readStore=key=>{try{return JSON.parse(localStorage.getItem(key)||'{}')||{};}catch(e){return {};}};
 states=readStore(stateKey);
 for(const legacyKey of legacyKeys){
  const legacy=readStore(legacyKey);
  for(const [id,value] of Object.entries(legacy)){
   if(states[id])continue;
   const current=value&&value.current?value.current:value;
   if(current&&current.prompt){
    states[id]={current,usedScenes:Array.isArray(value.usedScenes)?value.usedScenes:(current.scene?[current.scene]:[])};
   }
  }
 }
 try{localStorage.setItem(stateKey,JSON.stringify(states));}catch(e){}
 document.querySelectorAll('.prompt-refresh').forEach(button=>{
  const card=button.closest('.card');
  const source=card&&card.querySelector('.prompt-options');
  const copy=card&&card.querySelector('.copy');
  const tracker=card&&card.querySelector('.tracker');
  const meta=card&&card.querySelector('.prompt-meta');
  const time=meta&&meta.querySelector('.prompt-time');
  const title=card&&card.querySelector('h2');
  const caption=card&&card.querySelector('.caption');
  const tags=card&&card.querySelector('.tags');
  const post=card&&card.querySelector('.copy-post');
  if(!card||!source||!copy||!tracker||!meta||!time||!title||!caption||!tags||!post){
   button.disabled=true;
   button.textContent='UNAVAILABLE';
   return;
  }
  const key=tracker.dataset.date+'-video-'+tracker.dataset.video;
  let options=[];
  try{options=JSON.parse(source.getAttribute('data-prompt-options')||'[]');}catch(e){options=[];}
  const panel=document.createElement('section');
  panel.className='prompt-refresh-confirm';
  panel.style.cssText='display:none;margin:12px 0 0;padding:14px;background:#21170f;border:1px solid #70451f;border-radius:12px';
  panel.innerHTML='<strong>Update this prompt?</strong><p style="margin:6px 0 12px;color:#c7b9ad;font-size:13px">The current scene, Meta AI prompt, caption and hashtags will be replaced. This cannot be undone from this card.</p><div style="display:grid;grid-template-columns:1fr 1fr;gap:8px"><button type="button" data-confirm-update style="margin:0;background:#ff9a52;color:#1a1009">CONFIRM UPDATE</button><button type="button" data-cancel-update style="margin:0;background:#333;color:#fff">CANCEL</button></div>';
  button.insertAdjacentElement('afterend',panel);
  const status=document.createElement('p');
  status.setAttribute('aria-live','polite');
  status.style.cssText='margin:10px 0 0;font-size:12px;color:#aaa;min-height:18px';
  panel.appendChild(status);
  const apply=(item,stamp)=>{
   copy.dataset.prompt=JSON.stringify(item.prompt);
   title.textContent=item.scene;
   caption.textContent=item.caption;
   const hashtags=item.hashtags||item.tags||'';
   tags.textContent=hashtags;
   post.dataset.post=JSON.stringify(item.caption+String.fromCharCode(10,10)+hashtags);
   time.textContent='Prompt updated: '+stamp+' Warsaw time';
  };
  const saved=states[key];
  if(saved&&saved.current&&saved.current.prompt)apply(saved.current,saved.current.updatedAt||'Previously updated');
  button.type='button';
  button.setAttribute('aria-expanded','false');
  button.addEventListener('click',()=>{
   if(button.disabled)return;
   panel.style.display=panel.style.display==='none'?'block':'none';
   button.setAttribute('aria-expanded',panel.style.display==='block'?'true':'false');
   if(panel.style.display==='block')status.textContent='Confirm only if you want to replace this card.';
  });
  panel.querySelector('[data-cancel-update]').addEventListener('click',()=>{
   panel.style.display='none';
   button.setAttribute('aria-expanded','false');
   status.textContent='Update cancelled. The current prompt is unchanged.';
  });
  panel.querySelector('[data-confirm-update]').addEventListener('click',()=>{
   const old=states[key]||{};
   const used=new Set(Array.isArray(old.usedScenes)?old.usedScenes:[]);
   used.add(title.textContent.trim());
   const available=options.filter(item=>item&&item.scene&&item.prompt&&!used.has(item.scene));
   if(!available.length){
    status.textContent='No unused scenes remain in this category.';
    return;
   }
   const next=available[Math.floor(Math.random()*available.length)];
   const stamp=new Date().toLocaleString('en-GB',{timeZone:'Europe/Warsaw'});
   const updated={...next,updatedAt:stamp};
   used.add(next.scene);
   const nextStates={...states,[key]:{current:updated,usedScenes:[...used]}};
   try{localStorage.setItem(stateKey,JSON.stringify(nextStates));}
   catch(error){
    status.textContent='Could not save. The current prompt has not been changed.';
    return;
   }
   states=nextStates;
   apply(updated,stamp);
   status.textContent='🌟 Prompt updated. New scene, Meta AI prompt and TikTok caption are ready.';
   panel.style.display='none';
   button.setAttribute('aria-expanded','false');
  });
 });
}
setupPromptRefresh();
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
.entry h3{font-size:16px;margin:5px 0 8px}.publication-thumb{width:92px;height:120px;object-fit:cover;border-radius:9px;border:1px solid #383838;display:block;margin:10px 0}.thumb-row{display:flex;align-items:flex-start;gap:12px}.thumb-row .publication-thumb{flex:0 0 92px}.meta{font-size:12px;color:#a8aaa4}.stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px;margin:12px 0}.stats div{background:#101010;padding:8px;border-radius:8px;font-size:12px}.stats b{display:block;font-size:16px}
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
<label style="grid-column:1/-1">Publication screenshot (optional)<input id="old-image" type="file" accept="image/*" style="width:100%;padding:10px;background:#101010;color:#f3f3ef;border:1px solid #494949;border-radius:9px"><span class="meta">A small thumbnail will be saved with this publication.</span></label><label style="grid-column:1/-1">TikTok video URL<input id="old-url" type="url" placeholder="https://www.tiktok.com/..." style="width:100%;padding:10px;background:#101010;color:#f3f3ef;border:1px solid #494949;border-radius:9px"></label>
<label>Views<input id="old-views" type="number" min="0" value="0" style="width:100%;padding:10px;background:#101010;color:#f3f3ef;border:1px solid #494949;border-radius:9px"></label>
<label>Likes<input id="old-likes" type="number" min="0" value="0" style="width:100%;padding:10px;background:#101010;color:#f3f3ef;border:1px solid #494949;border-radius:9px"></label>
<label>Comments<input id="old-comments" type="number" min="0" value="0" style="width:100%;padding:10px;background:#101010;color:#f3f3ef;border:1px solid #494949;border-radius:9px"></label>
<label>Shares<input id="old-shares" type="number" min="0" value="0" style="width:100%;padding:10px;background:#101010;color:#f3f3ef;border:1px solid #494949;border-radius:9px"></label>
<label>Favorites / saves<input id="old-saves" type="number" min="0" value="0" style="width:100%;padding:10px;background:#101010;color:#f3f3ef;border:1px solid #494949;border-radius:9px"></label>
</div>
<button id="add-old" type="button" style="width:100%;padding:13px;background:#ff9a52;color:#1a1009;border:0;border-radius:10px;font-weight:700">Add to publication history</button>
<p id="add-message" class="muted" aria-live="polite"></p></section>
<section class="panel"><h2>Browse records</h2><div class="controls">
<select id="sort"><option value="newest">Newest first</option><option value="oldest">Oldest first</option><option value="views">Most views</option><option value="likes">Most likes</option></select>
<select id="status"><option value="all">All statuses</option><option value="published">Published</option><option value="created">Created</option><option value="checked">Quality checked</option><option value="planned">Planned</option></select>
</div><div id="records"></div></section>
<p class="muted">Data is read from the same browser storage as Daily Content Studio. It stays on this device and browser; clearing site data or switching devices can remove or hide it. Export CSV from the studio regularly as a backup.</p>
</main><nav class="bottom-nav"><a href="https://krash9.github.io/meta-ai-video-factory/index.html?v=navfix2"><b>⌂</b>Overview</a><a href="https://krash9.github.io/meta-ai-video-factory/calendar.html?v=navfix2"><b>▦</b>Calendar</a><a href="https://krash9.github.io/meta-ai-video-factory/content.html?v=navfix2"><b>▤</b>Content</a><a href="https://krash9.github.io/meta-ai-video-factory/analytics.html?v=navfix2"><b>▥</b>Analytics</a><a class="active" href="https://krash9.github.io/meta-ai-video-factory/history.html?v=navfix2"><b>↗</b>History</a></nav><script>
const key='quiet-place-publication-tracker-v1';let data={};
try{data=JSON.parse(localStorage.getItem(key)||'{}')||{};}catch(e){data={};}
if(!data['archive-20261108-coastal-sunset']){data['archive-20261108-coastal-sunset']={date:'2026-11-08',time:'01:57',video:'Archive',title:'Coastal sunset',url:'https://vm.tiktok.com/ZN85xQcuy/',views:788,likes:43,comments:3,shares:1,saves:2,status:'published',updatedAt:'Imported from user-provided TikTok Studio screenshot'};localStorage.setItem(key,JSON.stringify(data));}
if(!data['archive-20261115-autumn-birch-1748']){data['archive-20261115-autumn-birch-1748']={date:'2026-11-15',time:'17:48',video:'Archive',title:'Autumn birch forest',image:'data:image/jpeg;base64,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',url:'https://vm.tiktok.com/ZN85G9mPq/',views:683,likes:8,comments:0,shares:0,saves:0,watchTime:'00:23:36',averageWatchTime:'2.0 s',fullWatchPercent:'2.02%',newFollowers:0,duration:'10.01 s',status:'published',updatedAt:'Imported from user-provided TikTok Studio screenshot'};localStorage.setItem(key,JSON.stringify(data));}
if(!data['archive-20261115-autumn-birch-1851']){data['archive-20261115-autumn-birch-1851']={date:'2026-11-15',time:'18:51',video:'Archive',title:'Dark Autumn Birch Forest',image:'data:image/jpeg;base64,B64_REPLACE',url:'https://vm.tiktok.com/ZN85GxxAM/',views:652,likes:17,comments:0,shares:0,saves:1,watchTime:'00:19:00',averageWatchTime:'1.7 s',fullWatchPercent:'2.25%',newFollowers:2,duration:'10.01 s',status:'published',updatedAt:'Imported from user-provided TikTok Studio screenshot'};localStorage.setItem(key,JSON.stringify(data));}
const fmt=n=>Number(n||0).toLocaleString();
document.getElementById('old-date').value=new Date().toISOString().slice(0,10);
async function imageToThumb(file){if(!file)return '';if(!file.type.startsWith('image/'))throw new Error('Please choose an image file.');const source=await createImageBitmap(file);const scale=Math.min(1,420/Math.max(source.width,source.height));const canvas=document.createElement('canvas');canvas.width=Math.max(1,Math.round(source.width*scale));canvas.height=Math.max(1,Math.round(source.height*scale));canvas.getContext('2d').drawImage(source,0,0,canvas.width,canvas.height);source.close();return canvas.toDataURL('image/jpeg',0.72);}\ndocument.getElementById('add-old').addEventListener('click',async()=>{
 const date=document.getElementById('old-date').value;
 const url=document.getElementById('old-url').value.trim();
 if(!date||!url){document.getElementById('add-message').textContent='Please enter the publication date and TikTok URL.';return;}
 try{new URL(url);}catch(e){document.getElementById('add-message').textContent='Please enter a valid URL.';return;}
 const id='archive-'+Date.now();let image='';try{image=await imageToThumb(document.getElementById('old-image').files[0]);}catch(e){document.getElementById('add-message').textContent=e.message||'Could not process image.';return;}
 data[id]={date,video:'Archive',image,title:document.getElementById('old-title').value.trim()||'Older TikTok publication',url,
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
 const publicationOrder=(a,b)=>{
  const aStamp=String(a.date||'')+' '+String(a.time||'00:00');
  const bStamp=String(b.date||'')+' '+String(b.time||'00:00');
  return aStamp.localeCompare(bStamp)||String(a.video||'').localeCompare(String(b.video||''));
 };
 if(sort==='newest')list.sort((a,b)=>publicationOrder(b,a));
 if(sort==='oldest')list.sort(publicationOrder);
 if(sort==='views')list.sort((a,b)=>Number(b.views||0)-Number(a.views||0));
 if(sort==='likes')list.sort((a,b)=>Number(b.likes||0)-Number(a.likes||0));
 const root=document.getElementById('records');
 if(!list.length){root.innerHTML='<div class="empty">No saved publication records yet. Save a video in Daily Content Studio and it will appear here.</div>';return;}
 root.innerHTML=list.map(r=>{
 const statusLabel=(r.status||'planned').replace('checked','quality checked');
 const link=r.url?'<p class="url"><a href="'+esc(r.url)+'" target="_blank" rel="noopener">Open TikTok publication ↗</a></p>':'<p class="meta">No TikTok URL saved</p>';
 return '<article class="entry" data-record-id="'+esc(r._id)+'"><div class="meta">'+esc(r.date||'Date not set')+(r.time?' · '+esc(r.time):'')+' · Video '+esc(r.video||'?')+'</div><div class="thumb-row">'+(r.image?'<img class="publication-thumb" src="'+r.image+'" alt="Publication thumbnail">':'')+'<div><h3>'+esc(r.title||'Quiet Place publication')+'</h3><span class="pill">'+esc(statusLabel)+'</span>'+link+'</div></div>'+
 '<div class="stats"><div><b>'+fmt(r.views)+'</b>Views</div><div><b>'+fmt(r.likes)+'</b>Likes</div><div><b>'+fmt(r.comments)+'</b>Comments</div><div><b>'+fmt(r.shares)+'</b>Shares</div><div><b>'+fmt(r.saves)+'</b>Favorites</div></div><label class="meta">Change status <select class="quick-status"><option value="planned" '+((r.status||'planned')==='planned'?'selected':'')+'>Planned</option><option value="created" '+(r.status==='created'?'selected':'')+'>Created</option><option value="checked" '+(r.status==='checked'?'selected':'')+'>Quality checked</option><option value="published" '+(r.status==='published'?'selected':'')+'>Published</option></select></label><div class="meta">Last saved: '+esc(r.updatedAt||'—')+'</div>'+
 '<div class="record-actions"><button type="button" class="edit-record">Edit</button><button type="button" class="delete-record">Delete</button></div>'+
 '<form class="edit-form"><label>Replace screenshot (optional)<input name="image" type="file" accept="image/*"></label><label>Publication date<input name="date" type="date" value="'+esc(r.date||'')+'" required></label><label>Title / scene<input name="title" type="text" value="'+esc(r.title||'Quiet Place publication')+'"></label><label>TikTok URL<input name="url" type="url" value="'+esc(r.url||'')+'"></label><label>Status<select name="status"><option value="planned" '+((r.status||'planned')==='planned'?'selected':'')+'>Planned</option><option value="created" '+(r.status==='created'?'selected':'')+'>Created</option><option value="checked" '+(r.status==='checked'?'selected':'')+'>Quality checked</option><option value="published" '+(r.status==='published'?'selected':'')+'>Published</option></select></label><div class="grid"><label>Views<input name="views" type="number" min="0" value="'+esc(r.views||0)+'"></label><label>Likes<input name="likes" type="number" min="0" value="'+esc(r.likes||0)+'"></label><label>Comments<input name="comments" type="number" min="0" value="'+esc(r.comments||0)+'"></label><label>Shares<input name="shares" type="number" min="0" value="'+esc(r.shares||0)+'"></label><label>Favorites / saves<input name="saves" type="number" min="0" value="'+esc(r.saves||0)+'"></label></div><div class="edit-actions"><button type="submit">Save changes</button><button type="button" class="cancel-edit">Cancel</button></div></form></article>';
 }).join('');
 root.querySelectorAll('.entry').forEach(card=>{
  const id=card.dataset.recordId,form=card.querySelector('.edit-form');
  card.querySelector('.quick-status').addEventListener('change',e=>{data[id]={...data[id],status:e.target.value,updatedAt:new Date().toLocaleString()};try{localStorage.setItem(key,JSON.stringify(data));refreshSummary();render();}catch(err){alert('Could not save status. Browser storage may be unavailable.');}});
  card.querySelector('.edit-record').addEventListener('click',()=>form.classList.toggle('open'));
  card.querySelector('.cancel-edit').addEventListener('click',()=>form.classList.remove('open'));
  form.addEventListener('submit',async e=>{
   e.preventDefault();const fd=new FormData(form),old=data[id]||{};let image=old.image||'';try{const selected=form.querySelector('input[name="image"]').files[0];if(selected)image=await imageToThumb(selected);}catch(err){alert(err.message||'Could not process screenshot.');return;}
   const updated={...old,image,date:fd.get('date'),title:fd.get('title').trim(),url:fd.get('url').trim(),status:fd.get('status'),views:fd.get('views')||0,likes:fd.get('likes')||0,comments:fd.get('comments')||0,shares:fd.get('shares')||0,saves:fd.get('saves')||0,updatedAt:new Date().toLocaleString()};
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
calendar_page = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Quiet Place Calendar</title><style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#090909;color:#f5f5f5;font:15px/1.5 system-ui;padding:20px 16px 95px}main{max-width:700px;margin:auto}.panel{background:#191919;border:1px solid #333;border-radius:16px;padding:16px;margin:14px 0}.head,.row{display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap}.head button,.btn{background:#303030;color:white;padding:10px;border:1px solid #494949;border-radius:9px}.grid{display:grid;grid-template-columns:repeat(7,1fr);gap:5px;text-align:center}.day{padding:9px 1px;background:#101010;color:white;border:1px solid #333;border-radius:8px;min-height:42px}.day.has{border-color:#ff7a24;color:#ff9a52}.day.sel{background:#ff7a24;color:#111}.muted,.meta{color:#a8aaa4;font-size:12px}.fields{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.field{display:grid;gap:5px;margin:8px 0;color:#bbb;font-size:12px}.field input,.field select{width:100%;padding:10px;background:#101010;color:white;border:1px solid #494949;border-radius:9px;font:inherit}.item{border-top:1px solid #333;padding:12px 0}.status{background:#101010;color:white;border:1px solid #494949;border-radius:8px;padding:7px}.primary{background:#ff9a52;color:#1a1009;border:0;font-weight:700}.danger{color:#ffb5a8}.bottom-nav{position:fixed;bottom:0;left:0;right:0;background:#151515;display:grid;grid-template-columns:repeat(5,1fr);padding:10px 4px}.bottom-nav a{text-align:center;color:#999;text-decoration:none;font-size:11px}.bottom-nav b{display:block;font-size:18px}.bottom-nav .active{color:#ff7a24}
</style></head><body><main><h1>Publication Calendar</h1><p class="muted">Plan posts, edit details and change publication status. Calendar and History use the same saved data.</p><section class="panel"><div class="head"><button id="prev">‹</button><h2 id="month"></h2><button id="next">›</button></div><div class="grid" id="grid"></div><h3 id="date"></h3><div id="items"></div></section>
<section class="panel"><div class="head"><h2>Add a schedule item</h2><button class="btn" id="scheduleToday" type="button">Schedule today's 3 videos</button></div><form id="form"><div class="fields"><label class="field">Date<input id="dateInput" type="date" required></label><label class="field">Time<input id="timeInput" type="time"></label><label class="field">Video title / scene<input id="titleInput" placeholder="Quiet forest waterfall" required></label><label class="field">Video slot<select id="videoInput"><option value="1">Video 1</option><option value="2">Video 2</option><option value="3">Video 3</option><option value="Archive">Other / archive</option></select></label></div><button class="btn primary" type="submit">＋ Add to calendar</button><p class="muted" id="message"></p></form></section></main>
<nav class="bottom-nav"><a href="https://krash9.github.io/meta-ai-video-factory/index.html?v=navfix2"><b>⌂</b>Overview</a><a class="active" href="https://krash9.github.io/meta-ai-video-factory/calendar.html?v=navfix2"><b>▦</b>Calendar</a><a href="https://krash9.github.io/meta-ai-video-factory/content.html?v=navfix2"><b>▤</b>Content</a><a href="https://krash9.github.io/meta-ai-video-factory/analytics.html?v=navfix2"><b>▥</b>Analytics</a><a href="https://krash9.github.io/meta-ai-video-factory/history.html?v=navfix2"><b>↗</b>History</a></nav>
<script>
const key='quiet-place-publication-tracker-v1';let data={};try{data=JSON.parse(localStorage.getItem(key)||'{}')||{}}catch(e){}
const esc=v=>String(v??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
const today=()=>{let d=new Date();return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')};
let month=new Date();month.setDate(1);let selected=today();
const records=()=>Object.entries(data).map(([id,r])=>({...r,_id:id})).filter(r=>r.date);
function save(){localStorage.setItem(key,JSON.stringify(data));draw()}
function draw(){let y=month.getFullYear(),m=month.getMonth(),first=new Date(y,m,1),offset=(first.getDay()+6)%7,days=new Date(y,m+1,0).getDate();document.getElementById('month').textContent=first.toLocaleDateString('en-US',{month:'long',year:'numeric'});let g=document.getElementById('grid');g.innerHTML=['M','T','W','T','F','S','S'].map(x=>'<span class="muted">'+x+'</span>').join('');for(let i=0;i<offset;i++)g.insertAdjacentHTML('beforeend','<i></i>');for(let n=1;n<=days;n++){let dt=y+'-'+String(m+1).padStart(2,'0')+'-'+String(n).padStart(2,'0'),b=document.createElement('button');b.className='day'+(records().some(r=>r.date===dt)?' has':'')+(dt===selected?' sel':'');b.textContent=n;b.onclick=()=>{selected=dt;draw()};g.append(b)}document.getElementById('date').textContent=new Date(selected+'T12:00:00').toLocaleDateString('en-US',{weekday:'long',month:'long',day:'numeric'});document.getElementById('dateInput').value=selected;let list=records().filter(r=>r.date===selected).sort((a,b)=>(a.time||'').localeCompare(b.time||''));document.getElementById('items').innerHTML=list.length?list.map(r=>'<article class="item" data-id="'+esc(r._id)+'"><div class="row"><b>'+esc(r.title||('Video '+r.video))+'</b><span class="meta">'+esc(r.time||'')+'</span></div><div class="row"><label class="meta">Status <select class="status"><option value="planned" '+((r.status||'planned')==='planned'?'selected':'')+'>Planned</option><option value="created" '+(r.status==='created'?'selected':'')+'>Created</option><option value="checked" '+(r.status==='checked'?'selected':'')+'>Quality checked</option><option value="published" '+(r.status==='published'?'selected':'')+'>Published</option></select></label><div><button class="btn edit" type="button">Edit</button> <button class="btn remove danger" type="button">Remove</button></div></div><form class="edit" hidden><div class="fields"><label class="field">Title<input name="title" value="'+esc(r.title||'')+'" required></label><label class="field">Date<input name="date" type="date" value="'+esc(r.date)+'" required></label><label class="field">Time<input name="time" type="time" value="'+esc(r.time||'')+'"></label><label class="field">TikTok URL<input name="url" type="url" value="'+esc(r.url||'')+'"></label></div><button class="btn primary" type="submit">Save changes</button></form></article>').join(''):'<p class="muted">No publications saved for this date.</p>';document.querySelectorAll('.item').forEach(c=>{let id=c.dataset.id,form=c.querySelector('form.edit');c.querySelector('.status').onchange=e=>{data[id].status=e.target.value;data[id].updatedAt=new Date().toLocaleString();save()};c.querySelector('.edit').onclick=()=>form.hidden=!form.hidden;c.querySelector('.remove').onclick=()=>{if(confirm('Remove this item?')){delete data[id];save()}};form.onsubmit=e=>{e.preventDefault();let fd=new FormData(form);data[id]={...data[id],title:fd.get('title').trim(),date:fd.get('date'),time:fd.get('time'),url:fd.get('url').trim(),updatedAt:new Date().toLocaleString()};save()}})}
document.getElementById('prev').onclick=()=>{month.setMonth(month.getMonth()-1);draw()};document.getElementById('next').onclick=()=>{month.setMonth(month.getMonth()+1);draw()};
document.getElementById('form').onsubmit=e=>{e.preventDefault();let id='schedule-'+Date.now();data[id]={date:dateInput.value,time:timeInput.value,video:videoInput.value,title:titleInput.value.trim(),url:'',views:0,likes:0,comments:0,shares:0,saves:0,status:'planned',kind:'schedule',updatedAt:new Date().toLocaleString()};selected=data[id].date;titleInput.value='';message.textContent='Schedule item added.';save()};
document.getElementById('scheduleToday').onclick=()=>{let date=selected;[1,2,3].forEach(n=>{let id='schedule-'+date+'-'+n;if(!data[id])data[id]={date,video:String(n),title:'Quiet Place video '+n,time:'',url:'',views:0,likes:0,comments:0,shares:0,saves:0,status:'planned',kind:'schedule',updatedAt:new Date().toLocaleString()}});message.textContent='Three video slots added for this date.';save()};
draw();
</script></body></html>"""

CALENDAR_FILE.write_text(calendar_page, encoding="utf-8")
analytics_page = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Quiet Place Analytics</title><style>:root{color-scheme:dark}body{margin:0;background:#090909;color:#f5f5f5;font:15px system-ui;padding:20px 16px 90px}main{max-width:700px;margin:auto}.panel{background:#191919;border:1px solid #333;border-radius:16px;padding:16px;margin:14px 0}.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:8px}.metric{background:#101010;padding:14px;border-radius:10px}.metric b{display:block;font-size:23px}.bottom-nav{position:fixed;bottom:0;left:0;right:0;background:#151515;display:grid;grid-template-columns:repeat(5,1fr);padding:10px 4px}.bottom-nav a{text-align:center;color:#999;text-decoration:none;font-size:11px}.bottom-nav b{display:block;font-size:18px}.bottom-nav .active{color:#ff7a24}</style></head><body><main><h1>Analytics</h1><section class="panel"><div class="grid"><div class="metric"><b id="views">0</b>Views</div><div class="metric"><b id="likes">0</b>Likes</div><div class="metric"><b id="comments">0</b>Comments</div><div class="metric"><b id="shares">0</b>Shares</div></div></section><section class="panel"><h2>Top publications</h2><div id="top"></div></section></main><nav class="bottom-nav"><a href="https://krash9.github.io/meta-ai-video-factory/index.html?v=navfix2"><b>⌂</b>Overview</a><a href="https://krash9.github.io/meta-ai-video-factory/calendar.html?v=navfix2"><b>▦</b>Calendar</a><a href="https://krash9.github.io/meta-ai-video-factory/content.html?v=navfix2"><b>▤</b>Content</a><a class="active" href="https://krash9.github.io/meta-ai-video-factory/analytics.html?v=navfix2"><b>▥</b>Analytics</a><a href="https://krash9.github.io/meta-ai-video-factory/history.html?v=navfix2"><b>↗</b>History</a></nav><script>let d={};try{d=JSON.parse(localStorage.getItem('quiet-place-publication-tracker-v1')||'{}')}catch(e){}let rs=Object.values(d),f=n=>Number(n||0).toLocaleString();['views','likes','comments','shares'].forEach(k=>document.getElementById(k).textContent=f(rs.reduce((s,r)=>s+Number(r[k]||0),0)));document.getElementById('top').innerHTML=rs.sort((a,b)=>b.views-a.views).slice(0,10).map(r=>'<p>'+(r.title||('Video '+r.video))+' — '+f(r.views)+' views</p>').join('')||'No saved publications yet.';</script></body></html>"""
ANALYTICS_FILE.write_text(analytics_page, encoding="utf-8")



print(f"Quiet Place package created: {OUTPUT_DIR}")
print(f"Date: {today.isoformat()}")
print("Videos planned: 3")
for index, (category, scene) in enumerate(selected, start=1):
    print(f"{index}. {category}: {scene}")
