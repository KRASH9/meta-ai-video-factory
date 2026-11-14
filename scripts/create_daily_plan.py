
from pathlib import Path
from datetime import datetime, timezone
import json
import random

ROOT = Path(__file__).resolve().parents[1]

config_path = ROOT / "config" / "topics.json"
config = json.loads(config_path.read_text(encoding="utf-8"))

topics = config["topics"]
random.seed(datetime.now(timezone.utc).strftime("%Y-%m-%d"))

selected = random.sample(topics, k=3)

output = ROOT / "output" / "daily-plan.md"
output.parent.mkdir(parents=True, exist_ok=True)

lines = [
    "# Daily Meta AI Video Plan",
    "",
    f"Generated (UTC): {datetime.now(timezone.utc):%Y-%m-%d %H:%M}",
    "",
    "Generate each clip manually in Meta AI.",
    ""
]

for i, topic in enumerate(selected, start=1):
    prompt = (
        f"Create an 8-second cinematic, photorealistic video of {topic}. "
        "Use subtle natural motion, realistic lighting, "
        "a locked camera and a perfectly seamless loop. "
        "No text, no logos, no artificial-looking elements."
    )

    lines.extend([
        f"## Video {i}",
        "",
        f"**Concept:** {topic}",
        "",
        "**Prompt:**",
        "",
        prompt,
        ""
    ])

lines.extend([
    "## Checklist",
    "",
    "- [ ] Generate video in Meta AI",
    "- [ ] Save as MP4",
    "- [ ] Check video quality",
    "- [ ] Upload to TikTok drafts"
])

output.write_text("\n".join(lines), encoding="utf-8")

print(f"Created: {output}")
