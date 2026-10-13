"""Generate aggregate profile cards without exposing repository names or code."""
import json
import math
import os
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path

API = "https://api.github.com"
KST = timezone(timedelta(hours=9))


def get(path, token):
    request = urllib.request.Request(API + path, headers={
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "profile-statistics",
    })
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def collect(token, owner):
    now = datetime.now(timezone.utc)
    since = now - timedelta(days=365)
    since_query = since.isoformat().replace("+00:00", "Z")
    repos = []
    page = 1
    while True:
        batch = get(f"/user/repos?affiliation=owner&per_page=100&page={page}", token)
        repos.extend(r for r in batch if r["owner"]["login"].lower() == owner.lower()
                     and not r["fork"] and r["name"].lower() != owner.lower())
        if len(batch) < 100:
            break
        page += 1
    by_repo, by_commit, hours = Counter(), Counter(), Counter()
    days = set()
    seen = set()
    active_repos = 0
    for repo in repos:
        language = repo.get("language") or "Unclassified"
        by_repo[language] += 1
        if not repo.get("size"):
            continue
        page = 1
        active = False
        while True:
            path = ("/repos/" + repo["full_name"] + "/commits?per_page=100"
                    + f"&page={page}&author={owner}&since={since_query}")
            batch = get(path, token)
            for commit in batch:
                date = datetime.fromisoformat(commit["commit"]["author"]["date"].replace("Z", "+00:00"))
                if date < since or date > now:
                    continue
                active = True
                if commit["sha"] in seen:
                    continue
                seen.add(commit["sha"])
                by_commit[language] += 1
                local = date.astimezone(KST)
                hours[local.hour] += 1
                days.add(local.date().isoformat())
            if len(batch) < 100:
                break
            page += 1
        active_repos += int(active)
    return {
        "repositories": len(repos),
        "stars": sum(r["stargazers_count"] for r in repos),
        "commits": len(seen), "active_repos": active_repos, "active_days": len(days),
        "by_repo": dict(by_repo), "by_commit": dict(by_commit), "hours": dict(hours),
        "since": since.date().isoformat(), "updated": now.astimezone(KST).date().isoformat(),
    }


COLORS = {
    "C#": "#AF96EE", "JavaScript": "#E9C965", "TypeScript": "#79ACE8",
    "Rust": "#EAA07F", "Python": "#6EC6B7", "ASP.NET": "#9EA4E5",
    "CSS": "#CD96D3", "Kotlin": "#E69BBB", "Other": "#AEBACD",
    "Unclassified": "#BEC5CF",
}
PALETTE = ["#79ACE8", "#AF96EE", "#6EC6B7", "#EAA07F", "#E9C965", "#E69BBB"]


def render(data=None):
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="730" viewBox="0 0 1200 730" role="img" aria-labelledby="title desc">',
             '<title id="title">Profile statistics dashboard</title>',
             '<desc id="desc">Owned non-fork repositories excluding the profile repository. Commit activity covers the past 365 days on repository default branches, uses author dates, and deduplicates commit hashes. Commit languages use repository primary languages. Hours use Korean time.</desc>',
             '<style>text{font-family:Arial,Helvetica,sans-serif}.title{fill:#38445E;font-size:25px;font-weight:600}.sub{fill:#8792A6;font-size:12px}.label{fill:#657289;font-size:17px}.value{fill:#35415B;font-size:20px;font-weight:600}</style>']

    def text(x, y, value, cls="label", extra=""):
        parts.append(f'<text x="{x}" y="{y}" class="{cls}" {extra}>{escape(str(value))}</text>')

    def card(x, y, title, subtitle):
        parts.append(f'<rect x="{x}" y="{y}" width="576" height="334" rx="18" fill="#FCFBFF" stroke="#E8E6F0"/>')
        text(x+25, y+43, title, "title")
        text(x+25, y+66, subtitle, "sub")

    def donut(x, y, totals):
        entries = sorted(totals.items(), key=lambda item: (-item[1], item[0]))
        rows = entries[:6]
        if len(entries) > 6:
            rows.append(("Other", sum(n for _, n in entries[6:])))
        total = sum(totals.values())
        cx, cy, radius, thickness = x+422, y+197, 84, 31
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="#EEEAF5" stroke-width="{thickness}"/>')
        if not total:
            text(cx, cy+5, "No data", "sub", 'text-anchor="middle"')
            return
        circumference = 2 * math.pi * radius
        offset = 0
        for index, (language, count) in enumerate(rows):
            color = COLORS.get(language, PALETTE[index % len(PALETTE)])
            length = count / total * circumference
            gap = min(2.5, length * .15) if len(rows) > 1 else 0
            parts.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="{color}" stroke-width="{thickness}" stroke-dasharray="{length-gap:.4f} {circumference-length+gap:.4f}" stroke-dashoffset="{-offset:.4f}" transform="rotate(-90 {cx} {cy})"><title>{escape(language)}: {count/total*100:.1f}%</title></circle>')
            offset += length
            row_y = y+111+index*27
            parts.append(f'<rect x="{x+26}" y="{row_y-12}" width="11" height="11" rx="3" fill="{color}"/>')
            text(x+46, row_y, language)
            text(x+277, row_y, f"{count/total*100:.1f}%", "sub", 'text-anchor="end"')
        text(cx, cy+5, str(total), "value", 'text-anchor="middle"')

    card(16, 16, "Stats", "Owned repositories / activity in the past 365 days")
    labels = [("Repository stars", "stars"), ("Repositories", "repositories"),
              ("Commits", "commits"), ("Active repositories", "active_repos"), ("Active days", "active_days")]
    for index, (label, key) in enumerate(labels):
        yy = 126+index*37
        parts.append(f'<circle cx="48" cy="{yy-6}" r="4" fill="{PALETTE[index]}"/>')
        text(65, yy, label)
        text(315, yy, f'{data[key]:,}' if data else "—", "value", 'text-anchor="end"')
    parts.append('<circle cx="449" cy="202" r="70" fill="#EEE9FB"/><g fill="none" stroke="#AD98DB" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"><path d="M430 183L409 202L430 221M468 183L489 202L468 221M458 170L440 234"/></g>')
    card(608, 16, "Languages by Repository", "One primary language per owned repository")
    card(16, 366, "Commits by Repo Language", "Past 365 days / language of the containing repository")
    card(608, 366, "Commit Hours · UTC+09:00", "Past 365 days / author timestamp / Korean time")
    if data:
        donut(608, 16, data["by_repo"])
        donut(16, 366, data["by_commit"])
        chart_x, chart_y, chart_w, chart_h = 654, 639, 495, 156
        values = [data["hours"].get(i, data["hours"].get(str(i), 0)) for i in range(24)]
        peak = max(values) or 1
        ceiling = 10 ** math.floor(math.log10(peak))
        ceiling = math.ceil(peak / ceiling) * ceiling
        for index in range(5):
            yy = chart_y - chart_h * index / 4
            parts.append(f'<path d="M{chart_x} {yy}h{chart_w}" stroke="#E9E6F0"/>')
            text(chart_x-9, yy+4, f"{ceiling*index/4:g}", "sub", 'text-anchor="end"')
        step = chart_w / 24
        for hour, value in enumerate(values):
            hh = chart_h * value / ceiling
            parts.append(f'<rect x="{chart_x+hour*step+3:.2f}" y="{chart_y-hh:.2f}" width="{step-6:.2f}" height="{hh:.2f}" rx="3" fill="#85C7B0"><title>{hour:02d}:00: {value} commits</title></rect>')
        for hour in [0, 6, 12, 18, 23]:
            text(chart_x+(hour+.5)*step, chart_y+23, hour, "sub", 'text-anchor="middle"')
        text(chart_x+chart_w, chart_y+45, "hour of day", "sub", 'text-anchor="end"')
        text(1184, 722, f'Data: {data["since"]} — {data["updated"]} / KST', "sub", 'text-anchor="end"')
    else:
        for xx, yy in [(608,16),(16,366),(608,366)]:
            text(xx+288, yy+190, "Waiting for the first statistics update", "sub", 'text-anchor="middle"')
    parts.append('</svg>')
    return '\n'.join(parts)


if __name__ == "__main__":
    data = collect(os.environ["PROFILE_STATS_TOKEN"], os.environ["PROFILE_OWNER"])
    Path("assets").mkdir(exist_ok=True)
    Path("assets/profile-dashboard.svg").write_text(render(data), encoding="utf-8")
    print("Profile dashboard updated.")
