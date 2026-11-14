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
META_AI_CHAT_URL = "https://www.meta.ai/"

WARSAW = ZoneInfo("Europe/Warsaw")
today = datetime.now(WARSAW).date()
date_seed = today.strftime("%Y-%m-%d")

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
    "Hold the phone at a natural standing height from the edge of the scene. Keep the view mostly steady, with only subtle hand movement.",
    "Film from a nearby natural viewpoint, including a little foreground detail. Make no deliberate camera move; let the scene provide the motion.",
    "Use an ordinary wider phone view from a nearby path or open spot. Keep the framing casual and slightly imperfect, as in a real visit."
]

captions = {
    "Nature & Water": "Take a moment. Let nature slow you down. 🌿",
    "Forest & Weather": "A quiet moment away from the noise. 🍃",
    "Cozy Quiet Places": "Some places make you breathe a little easier. 🤍"
}

hashtags = "#QuietPlace #PeacefulMoments #NatureSounds #SlowLiving #RelaxingNature"

def build_prompt(scene, camera_note):
    return (
        f"Create a realistic casual smartphone video in vertical 9:16 format, showing {scene}. "
        "It should feel like a visitor quietly filmed a real place on a good phone, "
        "not like a movie, advert or staged travel production. "
        f"{camera_note} "
        "Use natural available daylight, realistic exposure, believable everyday colors "
        "and ordinary smartphone detail. Preserve small imperfections in framing; do not "
        "make the scene look artificially perfect. Show only movement that naturally "
        "belongs there, such as flowing water, leaves moving or rain falling. "
        "Use authentic environmental sound only. "
        "No cinematic lighting, color grading, dramatic sun rays, exaggerated fog or mist, "
        "artificial bokeh, slow motion, drone view, sweeping camera movement, visual effects, "
        "music, people, crowds, text, logos or transitions. "
        "Avoid the polished synthetic look of AI-generated footage."
    )

video_packages = []

lines = [
    "# QUIET PLACE — Daily Content Plan",
    "",
    f"Date: {today.isoformat()}",
    "Brand: Quiet Place",
    "Mission: Leave the noise behind.",
    "",
    "Three ready-to-produce videos. Individual copy-ready files are included in this package.",
    "The goal is a believable quiet moment, not a cinematic travel scene.",
    ""
]

for index, (category, scene) in enumerate(selected, start=1):
    camera_note = camera_approaches[index - 1]
    prompt = build_prompt(scene, camera_note)
    caption = captions[category]
    video_packages.append({"index": index, "category": category, "scene": scene, "prompt": prompt, "caption": caption, "hashtags": hashtags})
    video_dir = OUTPUT_DIR / f"video-{index:02d}"
    video_dir.mkdir(parents=True, exist_ok=True)

    (video_dir / "01-meta-ai-prompt.txt").write_text(prompt + "\n", encoding="utf-8")
    (video_dir / "02-tiktok-caption-and-hashtags.txt").write_text(
        f"{caption}\n\n{hashtags}\n", encoding="utf-8"
    )
    (video_dir / "03-quality-checklist.txt").write_text(
        "QUIET PLACE — VIDEO QUALITY CHECK\n\n"
        "[ ] Vertical 9:16 format\n"
        "[ ] Looks like a real place filmed casually on a good smartphone\n"
        "[ ] Natural light and believable colors\n"
        "[ ] Natural movement; no artificial camera moves\n"
        "[ ] Ambient environmental sound only; no music\n"
        "[ ] No text, logos, visual effects or transitions\n"
        "[ ] No visible generation defects or strange objects\n"
        "[ ] Suitable for the calm Quiet Place identity\n",
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
        hashtags,
        "",
        f"**Copy-ready folder:** video-{index:02d}/",
        "",
        "**Quality checklist:**",
        "",
        "- [ ] Vertical 9:16 format",
        "- [ ] Natural, believable smartphone footage",
        "- [ ] Natural movement and ambient sound",
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
    "- Keep camera movement simple; do not add dramatic effects.",
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
    cards.append(
        f"""
        <article class="card">
          <div class="eyebrow">VIDEO {item["index"]} · {escape(item["category"])}</div>
          <h2>{escape(item["scene"])}</h2>
          <button class="copy" data-prompt='{escape(prompt_json, quote=True)}'>Copy Meta AI prompt</button>
          <p class="caption">{escape(item["caption"])}</p>
          <p class="tags">{escape(item["hashtags"])}</p>
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
.copy{background:#e4e8dc;color:#172016}.primary{background:#9eb18c;color:#11190f;margin:20px 0}.caption{margin:14px 0 4px}.tags{font-size:13px;color:#b6b9b0;overflow-wrap:anywhere}
.status{min-height:24px;color:#b9c5a8;font-size:14px;margin-top:8px}.note{font-size:13px;color:#a8aaa4;margin:18px 0}
</style>
</head>
<body><main>
<div class="eyebrow">QUIET PLACE · LEAVE THE NOISE BEHIND</div>
<h1>Daily Content Studio</h1>
<p class="muted">DATE_PLACEHOLDER · Three copy-ready video prompts</p>
<a class="primary" href="META_AI_URL_PLACEHOLDER" target="_blank" rel="noopener">Open Meta AI</a>
<div id="status" class="status" aria-live="polite">Choose a video and copy its prompt. Then paste it into Meta AI.</div>
""" + "\n".join(cards) + """
<p class="note">This dashboard prepares and copies prompts only. Meta AI video generation and saving the finished video still require your action.</p>
</main>
<script>
document.querySelectorAll('.copy').forEach(button=>{
  button.addEventListener('click',async()=>{
    const prompt=JSON.parse(button.dataset.prompt);
    try{
      if(navigator.clipboard && window.isSecureContext){await navigator.clipboard.writeText(prompt);}
      else{
        const field=document.createElement('textarea');field.value=prompt;
        field.style.position='fixed';field.style.opacity='0';document.body.appendChild(field);
        field.focus();field.select();const ok=document.execCommand('copy');field.remove();
        if(!ok) throw new Error('Clipboard unavailable');
      }
      document.getElementById('status').textContent='Prompt copied. Open Meta AI and paste it into the chat.';
      button.textContent='Copied ✓';setTimeout(()=>button.textContent='Copy Meta AI prompt',1800);
    }catch(e){
      document.getElementById('status').textContent='Copy was blocked. Use the individual prompt .txt file instead.';
    }
  });
});
</script>
</body></html>"""
dashboard = dashboard.replace("DATE_PLACEHOLDER", today.isoformat()).replace("META_AI_URL_PLACEHOLDER", META_AI_CHAT_URL)
DASHBOARD_FILE.write_text(dashboard, encoding="utf-8")

print(f"Quiet Place package created: {OUTPUT_DIR}")
print(f"Date: {today.isoformat()}")
print("Videos planned: 3")
for index, (category, scene) in enumerate(selected, start=1):
    print(f"{index}. {category}: {scene}")
