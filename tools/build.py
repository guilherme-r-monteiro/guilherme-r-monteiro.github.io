import html
import json
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE_TITLE = "Guilherme Monteiro"
EMAIL = "guilhermeromonteiro@gmail.com"
LINKEDIN = "https://www.linkedin.com/in/grmonteiro"
GITHUB = "https://github.com/guilherme-r-monteiro"
TYPE_ORDER = (
    "Agentic and MCP",
    "Computer vision and inference",
    "Data and backend",
    "Delivery and management",
)
REPO_LABELS = {
    "public": "Repository",
    "private": "Repository: public after review",
    "company": "Private company work. No public repository.",
}


@dataclass(frozen=True)
class Project:
    type: str
    title: str
    tags: list[str]
    headline: str
    problem: str
    built: str
    result: str
    limits: str
    repo: str | None
    status: str
    target: str | None


def load_projects() -> list[Project]:
    rows = json.loads((ROOT / "projects.json").read_text())
    return [Project(**{"target": None, **row}) for row in rows]


def escape(text: str) -> str:
    return html.escape(text, quote=True)


def repo_line(project: Project) -> str:
    label = REPO_LABELS[project.status]
    if project.status == "public" and project.repo:
        return f'<a href="{escape(project.repo)}">{escape(project.repo.removeprefix("https://"))}</a>'
    return escape(label)


def render_project(project: Project) -> str:
    tags = "".join(f'<span class="tag">{escape(t)}</span>' for t in project.tags)
    target = f'<p class="target">Built for: {escape(project.target)}</p>' if project.target else ""
    return (
        f'<article class="card" data-type="{escape(project.type)}">'
        f'<div class="card-head"><h3>{escape(project.title)}</h3><p class="headline">{escape(project.headline)}</p></div>'
        f'<div class="tags">{tags}</div>{target}'
        f'<p class="problem">{escape(project.problem)}</p>'
        f'<details><summary>Build, result and limits</summary><dl>'
        f'<dt>What was built</dt><dd>{escape(project.built)}</dd>'
        f'<dt>Measured result</dt><dd>{escape(project.result)}</dd>'
        f'<dt>Limits</dt><dd>{escape(project.limits)}</dd>'
        f'<dt>Link</dt><dd>{repo_line(project)}</dd></dl></details></article>'
    )


def render_chips() -> str:
    chips = ['<button class="chip" data-filter="all" aria-pressed="true">All</button>']
    chips += [f'<button class="chip" data-filter="{escape(t)}" aria-pressed="false">{escape(t)}</button>' for t in TYPE_ORDER]
    return "".join(chips)


def render_page(projects: list[Project]) -> str:
    ordered = sorted(projects, key=lambda p: TYPE_ORDER.index(p.type))
    cards = "".join(render_project(p) for p in ordered)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{SITE_TITLE} - Portfolio</title>
<meta name="description" content="Product-oriented technical leader. Agentic and computer-vision projects with problem, build, measured result and limits.">
<link rel="stylesheet" href="style.css"></head><body>
<nav class="bar"><a class="brand" href="#top">GM</a><a href="#projects">Projects</a><a href="#contact">Contact</a><button id="theme" aria-label="Toggle dark mode">Theme</button></nav>
<header id="top"><h1>{SITE_TITLE}</h1><p class="role">Product-oriented technical leader. Agentic systems and computer vision.</p>
<p class="lead">I talk to the client, design the product and build it end to end. Each project below states the problem, the measured result and the limits.</p>
<p class="links"><a href="mailto:{EMAIL}">Email</a><a href="{LINKEDIN}">LinkedIn</a><a href="{GITHUB}">GitHub</a></p></header>
<main id="projects"><h2>Projects</h2><div class="chips" role="group" aria-label="Filter by type">{render_chips()}</div>
<div class="list">{cards}</div></main>
<footer id="contact"><p>Contact: <a href="mailto:{EMAIL}">{EMAIL}</a> · <a href="{LINKEDIN}">LinkedIn</a></p>
<p class="small">Company work is described at the level of the public resume, without confidential detail. No tracking, no external fonts.</p></footer>
<script src="site.js"></script></body></html>"""


def main() -> None:
    (ROOT / "index.html").write_text(render_page(load_projects()))


if __name__ == "__main__":
    main()
