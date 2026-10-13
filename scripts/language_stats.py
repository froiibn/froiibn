"""Publish language totals only; never publish private repository names or code."""
import json
import os
import urllib.request
from collections import Counter
from html import escape
from pathlib import Path

API = "https://api.github.com"

def get(path, token):
    request = urllib.request.Request(API + path, headers={
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "profile-language-stats",
    })
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)

def collect(token, owner):
    totals = Counter()
    page = 1
    while True:
        repos = get(f"/user/repos?affiliation=owner&per_page=100&page={page}", token)
        for repo in repos:
            if repo["owner"]["login"].lower() != owner.lower():
                continue
            if repo["fork"] or repo["name"].lower() == owner.lower():
                continue
            totals.update(get("/repos/" + repo["full_name"] + "/languages", token))
        if len(repos) < 100:
            return totals
        page += 1

def render(totals):
    import math
    total = sum(totals.values())
    if not total:
        raise ValueError("No language data available; existing card preserved.")
    entries = sorted(
        ((name, value) for name, value in totals.items() if name != "Other"),
        key=lambda item: (-item[1], item[0]),
    )
    rows = entries[:8]
    other = totals.get("Other", 0) + sum(value for _, value in entries[8:])
    if other:
        rows.append(("Other", other))
    colors = {
        "C#": "#99ffb1", "JavaScript": "#76e49a", "TypeScript": "#5fd582",
        "Rust": "#b0e8a7", "Python": "#48bd74", "ASP.NET": "#86cb93",
        "CSS": "#63a977", "Kotlin": "#a8d2a0", "Other": "#537e61",
    }
    palette = ["#99ffb1", "#76e49a", "#5fd582", "#b0e8a7", "#48bd74"]
    height = max(340, 105 + len(rows) * 25)
    cx, cy, outer, inner = 176, 190, 106, 74
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="700" height="{height}" viewBox="0 0 700 {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Language map — code language proportions</title>',
        '<desc id="desc">Donut chart of language proportions by code bytes in accessible owned repositories. Forks and the profile repository are excluded.</desc>',
        '<style>.p{fill:#a0ffb7}.s{fill:#72a481}.border{fill:#050b07;stroke:#326b41}</style>',
        f'<rect x="1" y="1" width="698" height="{height-2}" rx="3" class="border"/>',
        '<rect x="24" y="22" width="3" height="16" fill="#64e58d"/>',
        '<text x="37" y="35" class="p" font-family="monospace" font-size="16" font-weight="700">LANGUAGE MAP</text>',
        '<text x="24" y="56" class="s" font-family="monospace" font-size="11">Accessible owned repositories / code bytes / forks excluded</text>',
        f'<circle cx="{cx}" cy="{cy}" r="{(outer+inner)/2}" fill="none" stroke="#142d1c" stroke-width="{outer-inner}"/>',
    ]
    start = -math.pi / 2
    def point(radius, angle):
        return (cx + radius * math.cos(angle), cy + radius * math.sin(angle))
    for index, (language, size) in enumerate(rows):
        percentage = size / total * 100
        sweep = size / total * 2 * math.pi
        gap = min(math.radians(0.8), sweep * 0.12)
        a, b = start + gap / 2, start + sweep - gap / 2
        color = colors.get(language, palette[index % len(palette)])
        if len(rows) == 1:
            parts.append(f'<circle cx="{cx}" cy="{cy}" r="{(outer+inner)/2}" fill="none" stroke="{color}" stroke-width="{outer-inner}"/>')
        else:
            p1, p2, p3, p4 = point(outer, a), point(outer, b), point(inner, b), point(inner, a)
            large = int(b - a > math.pi)
            path = (
                f"M {p1[0]:.3f} {p1[1]:.3f} "
                f"A {outer} {outer} 0 {large} 1 {p2[0]:.3f} {p2[1]:.3f} "
                f"L {p3[0]:.3f} {p3[1]:.3f} "
                f"A {inner} {inner} 0 {large} 0 {p4[0]:.3f} {p4[1]:.3f} Z"
            )
            parts.append(f'<path d="{path}" fill="{color}"><title>{escape(language)}: {percentage:.1f}%</title></path>')
        y = 90 + index * 25
        parts.extend([
            f'<rect x="335" y="{y-9}" width="8" height="8" fill="{color}"/>',
            f'<text x="355" y="{y}" class="p" font-family="monospace" font-size="13">{escape(language)}</text>',
            f'<text x="674" y="{y}" text-anchor="end" class="s" font-family="monospace" font-size="13">{percentage:.1f}%</text>',
        ])
        start += sweep
    parts.extend([
        f'<text x="{cx}" y="{cy-2}" text-anchor="middle" class="p" font-family="monospace" font-size="20">CODE</text>',
        f'<text x="{cx}" y="{cy+20}" text-anchor="middle" class="s" font-family="monospace" font-size="12">BYTES</text>',
        '</svg>',
    ])
    return "\n".join(parts)

if __name__ == "__main__":
    token = os.environ["PROFILE_STATS_TOKEN"]
    owner = os.environ["PROFILE_OWNER"]
    svg = render(collect(token, owner))
    Path("assets").mkdir(exist_ok=True)
    Path("assets/language-donut.svg").write_text(svg, encoding="utf-8")
    print("Language card updated.")


