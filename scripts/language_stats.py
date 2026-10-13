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
    total = sum(totals.values())
    if not total:
        raise ValueError("No language data available; existing card preserved.")
    entries = sorted(totals.items(), key=lambda item: (-item[1], item[0]))
    rows = entries[:8]
    if len(entries) > 8:
        rows.append(("Other", sum(value for _, value in entries[8:])))
    colors = {
        "C#": "#b69aff", "JavaScript": "#ecd66b", "TypeScript": "#71a8f5",
        "Rust": "#eda57e", "Python": "#6ed5ca", "ASP.NET": "#9aabf5",
        "CSS": "#9d91ee", "Kotlin": "#e294d7", "Other": "#778ba6",
    }
    palette = ["#6ed5ca", "#71a8f5", "#b69aff", "#eda57e", "#ecd66b"]
    height = 92 + len(rows) * 38
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="700" height="{height}" viewBox="0 0 700 {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Code languages</title>',
        '<desc id="desc">Language proportions by code bytes in accessible owned repositories. Forks and the profile repository are excluded.</desc>',
        '<style>.p{fill:#edf3fb}.s{fill:#9bacc3}.track{fill:#202d42}.border{fill:#101a2c;stroke:#2a3a52}</style>',
        f'<rect x="1" y="1" width="698" height="{height-2}" rx="12" class="border"/>',
        '<rect x="24" y="22" width="3" height="16" rx="1.5" fill="#4ddbc8"/>',
        '<text x="37" y="35" class="p" font-family="Arial,sans-serif" font-size="16" font-weight="700">CODE LANGUAGES</text>',
        '<text x="24" y="57" class="s" font-family="Arial,sans-serif" font-size="12">Accessible owned repositories · code bytes · forks excluded</text>',
    ]
    for index, (language, size) in enumerate(rows):
        y = 84 + index * 38
        percentage = size / total * 100
        color = colors.get(language, palette[index % len(palette)])
        parts.extend([
            f'<circle cx="29" cy="{y-4}" r="3" fill="{color}"/>',
            f'<text x="42" y="{y}" class="p" font-family="monospace" font-size="13">{escape(language)}</text>',
            f'<rect x="190" y="{y-10}" width="400" height="8" rx="4" class="track"/>',
            f'<rect x="190" y="{y-10}" width="{percentage*4:.2f}" height="8" rx="4" fill="{color}"/>',
            f'<text x="676" y="{y}" text-anchor="end" class="s" font-family="monospace" font-size="13">{percentage:.1f}%</text>',
        ])
    parts.append("</svg>")
    return "\n".join(parts)

if __name__ == "__main__":
    token = os.environ["PROFILE_STATS_TOKEN"]
    owner = os.environ["PROFILE_OWNER"]
    svg = render(collect(token, owner))
    Path("assets").mkdir(exist_ok=True)
    Path("assets/languages.svg").write_text(svg, encoding="utf-8")
    print("Language card updated.")


