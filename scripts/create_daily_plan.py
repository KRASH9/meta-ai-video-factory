from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import random

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "topics.json"
OUTPUT = ROOT / "output" / "daily-plan.md"

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

# Different simple phone-camera approaches keep the three videos from
# feeling like copies while preserving the everyday, non-cinematic look.
camera_approaches = [
    (
        "Hold the phone at a natural standing height from the edge of the "
        "scene. Keep the view mostly steady, with only subtle hand movement."
    ),
    (
        "Film from a nearby natural viewpoint, including a little foreground "
        "detail. Make no deliberate camera move; let the scene provide the motion."
    ),
    (
        "Use an ordinary wider phone view from a nearby path or open spot. "
        "Keep the framing casual and slightly imperfect, as in a real visit."
    )
]

captions = {
    "Nature & Water": "Take a moment. Let nature slow you down. 🌿",
    "Forest & Weather": "A quiet moment away from the noise. 🍃",
    "Cozy Quiet Places": "Some places make you breathe a little easier. 🤍"
}

lines = [
    "# QUIET PLACE — Daily Content Plan",
    "",
    f"Date: {today.isoformat()}",
    "Brand: Quiet Place",
    "Mission: Leave the noise behind.",
    "",
    "Create three peaceful, original videos using Meta AI.",
    "The goal is a believable quiet moment, not a cinematic travel scene.",
    ""
]

for index, (category, scene) in enumerate(selected, start=1):
    camera_note = camera_approaches[index - 1]
    prompt = (
        f"Create a realistic casual smartphone video in vertical 9:16 format, "
        f"showing {scene}. "
        "It should feel like a visitor quietly filmed a real place on a good "
        "phone, not like a movie, advert or staged travel production. "
        f"{camera_note} "
        "Use natural available daylight, realistic exposure, believable "
        "everyday colors and ordinary smartphone detail. Preserve small "
        "imperfections in framing; do not make the scene look artificially "
        "perfect. Show only movement that naturally belongs there, such as "
        "flowing water, leaves moving or rain falling. "
        "Use authentic environmental sound only. "
        "No cinematic lighting, color grading, dramatic sun rays, exaggerated "
        "fog or mist, artificial bokeh, slow motion, drone view, sweeping "
        "camera movement, visual effects, music, people, crowds, text, logos "
        "or transitions. Avoid the polished synthetic look of AI-generated footage."
    )

    lines.extend([
        f"## Video {index} — {category}",
        "",
        f"**Scene:** {scene}",
        "",
        "**Camera approach:**",
        "",
        camera_note,
        "",
        "**Meta AI prompt:**",
        "",
        prompt,
        "",
        "**TikTok caption:**",
        "",
        captions[category],
        "",
        "**Hashtags:**",
        "",
        "#QuietPlace #PeacefulMoments #NatureSounds #SlowLiving #RelaxingNature",
        "",
        "**Production checklist:**",
        "",
        "- [ ] Generate in Meta AI",
        "- [ ] Save the video",
        "- [ ] Check that the place and movement look natural",
        "- [ ] Check ambient sound and vertical format",
        "- [ ] Prepare for TikTok",
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
    "- This planner selects scenes for the current day; it does not yet keep "
    "a persistent history of previously published scenes.",
    "- Never publish a defective or unsuitable video.",
    ""
])

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("\n".join(lines), encoding="utf-8")

print(f"Quiet Place plan created: {OUTPUT}")
print(f"Date: {today.isoformat()}")
print("Videos planned: 3")
for index, (category, scene) in enumerate(selected, start=1):
    print(f"{index}. {category}: {scene}")
