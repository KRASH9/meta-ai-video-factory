
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
topics = config["topics"]

# Three content directions for Quiet Place.
categories = {
    "Nature & Water": [
        "a quiet lake surrounded by pine trees at dawn",
        "a gentle waterfall flowing through a mossy forest",
        "soft ocean waves reaching a peaceful empty beach",
        "a clear stream flowing over smooth stones",
        "a misty river reflecting the morning sky",
        "gentle rain falling on a still lake"
    ],
    "Forest & Atmosphere": [
        "a peaceful pine forest covered in soft morning mist",
        "gentle snow falling between tall evergreen trees",
        "warm sunlight passing through a quiet bamboo forest",
        "a forest path after a gentle rainfall",
        "slow clouds moving above a green mountain valley",
        "soft autumn leaves moving in a light breeze"
    ],
    "Cozy Quiet Places": [
        "a peaceful Japanese garden with a small stone lantern",
        "a quiet wooden cabin beside a calm lake",
        "a small garden with a gentle flowing fountain",
        "an empty old European street after light rain",
        "a warm campfire glowing quietly in a forest clearing",
        "a peaceful countryside cottage at sunrise"
    ]
}

rng = random.Random(date_seed)

selected = []
for category, options in categories.items():
    selected.append((category, rng.choice(options)))

lines = [
    "# QUIET PLACE — Daily Content Plan",
    "",
    f"Date: {today.isoformat()}",
    "Brand: Quiet Place",
    "Mission: Leave the noise behind.",
    "",
    "Create three peaceful, original videos using Meta AI.",
    "Prioritize calm, natural realism and a feeling of presence.",
    ""
]

for index, (category, scene) in enumerate(selected, start=1):
    prompt = (
        f"Create a realistic casual smartphone video, vertical 9:16, "
        f"showing {scene}. "
        "Make it look like a real place casually filmed by a visitor, "
        "not a movie, travel commercial or professionally staged production. "
        "Use ordinary natural daylight, believable colors and realistic "
        "smartphone camera detail. Keep natural imperfections in framing "
        "and exposure; slight handheld movement is acceptable. "
        "Show only the movement that would naturally happen in the scene. "
        "Keep the composition simple and believable. "
        "Use authentic ambient environmental sound only. "
        "No cinematic lighting, no color grading, no dramatic sun rays, "
        "no exaggerated fog or mist, no artificial bokeh, no slow motion, "
        "no drone shots, no sweeping camera moves, no visual effects, "
        "no music, no people, no crowds, no text, no logos, no transitions. "
        "Avoid the polished, synthetic look of AI-generated footage."
    )

    caption = {
        "Nature & Water": "Take a moment. Let nature slow you down. 🌿",
        "Forest & Atmosphere": "A quiet moment away from the noise. 🍃",
        "Cozy Quiet Places": "Some places make you breathe a little easier. 🤍"
    }[category]

    lines.extend([
        f"## Video {index} — {category}",
        "",
        f"**Scene:** {scene}",
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
        "#QuietPlace #PeacefulMoments #NatureSounds "
        "#SlowLiving #RelaxingNature",
        "",
        "**Production checklist:**",
        "",
        "- [ ] Generate in Meta AI",
        "- [ ] Save the video",
        "- [ ] Check visual quality and natural motion",
        "- [ ] Check sound and video format",
        "- [ ] Prepare for TikTok",
        ""
    ])

lines.extend([
    "---",
    "",
    "## Daily quality standards",
    "",
    "- Authentic everyday realism is more important than cinematic beauty.",
    "- Videos should feel like casual smartphone footage of a real place.",
    "- Use natural light, believable colors and ordinary camera framing.",
    "- Avoid cinematic grading, dramatic effects and artificial perfection.",
    "- Natural ambient sound is preferred; no background music.",
    "- Avoid repeating recently published scenes.",
    "- Never publish a defective or unsuitable video.",
    ""
])

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("\n".join(lines), encoding="utf-8")

print(f"Quiet Place plan created: {OUTPUT}")
print(f"Date: {today.isoformat()}")
print("Videos planned: 3")
