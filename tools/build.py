import html
import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SITE_TITLE = "Guilherme Monteiro"
EMAIL = "guilhermeromonteiro@gmail.com"
LINKEDIN = "https://www.linkedin.com/in/grmonteiro"
GITHUB = "https://github.com/guilherme-r-monteiro"
PHOTO_SOURCE = Path.home() / "profile-foto.jpg"
PHOTO_TARGET = ROOT / "assets" / "profile.webp"
PHOTO_MAX_SIZE = 400
CV_PATH = "assets/guilherme-monteiro-cv.pdf"
HERO_STATEMENT = "I turn client problems into measured computer-vision and agentic systems."
HERO_SUPPORT = "Applied ML engineer. I lead the client conversation, design the product and build it end to end."
PROJECT_ORDER = (
    "vision-agent-mcp",
    "HelperBot",
    "agent-retrieval-service",
    "lidar-camera-fusion",
    "cv-label-audit",
    "cv-training-lab",
    "edge-inference-bench",
    "ml-feature-serving",
    "Facial-expression effort model",
)
NUMBERS = (
    ("0.35 m", "median distance error with LiDAR fusion"),
    ("266 tok/s", "local LLM decode on a laptop GPU"),
    ("90.4%", "CIFAR-10 test accuracy, pretrained ResNet-18"),
    ("92%", "of railway false alerts traced to 21 of 119 scenes"),
)
ABOUT_TEXT = (
    "I am a forward deployed engineer who owns solutions end to end, from the client problem to production.",
    "At ALTAVE I worked on site with a drilling client as Forward Deployed Engineer, I manage a maritime monitoring project, and I led the architecture of a real-time GPU vision pipeline.",
    "I design the product, build the models and services, and ship them, with the client in the loop at every step. Today I focus on computer vision and agentic systems.",
)
FACTS = (
    ("Location", "São Paulo, SP, Brazil (remote)"),
    ("Languages", "Portuguese (native), English (native or bilingual)"),
    ("Education", "Bachelor's in Mechatronics Engineering, Escola Politécnica da USP, 2018-2023"),
)
STACK = "Python, PyTorch, TensorRT, DeepStream, ONNX, YOLOv8, OpenCV, CUDA, FastAPI, gRPC, asyncio, TypeScript, Figma, Docker, AWS, MLflow"
MEDIA_PROJECTS = frozenset(
    ("vision-agent-mcp", "cv-label-audit", "cv-training-lab", "lidar-camera-fusion", "edge-inference-bench", "ml-feature-serving", "agent-retrieval-service")
)


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


@dataclass(frozen=True)
class Engagement:
    name: str
    role: str
    period: str
    points: list[str]


@dataclass(frozen=True)
class Position:
    org: str
    place: str
    title: str
    period: str
    summary: str
    engagements: list[Engagement]


def escape(text: str) -> str:
    return html.escape(text, quote=True)


def load_projects() -> list[Project]:
    rows = json.loads((ROOT / "projects.json").read_text())
    by_title = {row["title"]: Project(**{"target": None, **row}) for row in rows}
    return [by_title[title] for title in PROJECT_ORDER]


def load_positions() -> list[Position]:
    rows = json.loads((ROOT / "experience.json").read_text())
    return [Position(**{**row, "engagements": [Engagement(**e) for e in row["engagements"]]}) for row in rows]


def prepare_photo() -> bool:
    if not PHOTO_SOURCE.exists():
        return False
    image = Image.open(PHOTO_SOURCE).convert("RGB")
    image.thumbnail((PHOTO_MAX_SIZE, PHOTO_MAX_SIZE))
    image.save(PHOTO_TARGET, quality=82)
    return True


def render_photo(has_photo: bool) -> str:
    if has_photo:
        return '<img class="photo" src="assets/profile.webp" width="400" height="400" alt="Portrait of Guilherme Monteiro" decoding="async">'
    return '<div class="photo placeholder" role="img" aria-label="Profile photo placeholder"><span>GM</span></div>'


def render_hero(has_photo: bool) -> str:
    return (
        '<header class="hero" id="top"><div class="hero-art" aria-hidden="true"><i></i><i></i><i></i><b></b></div>'
        f'<div class="hero-inner"><p class="eyebrow">Applied ML engineer</p><h1>{escape(HERO_STATEMENT)}</h1>'
        f'<p class="support">{escape(HERO_SUPPORT)}</p>'
        f'<p class="cta"><a class="btn primary" href="{CV_PATH}" download>Download CV</a><a class="btn" href="#contact">Contact</a></p></div>'
        f'{render_photo(has_photo)}</header>'
    )


def render_numbers() -> str:
    items = "".join(f'<li class="reveal"><strong>{escape(v)}</strong><span>{escape(label)}</span></li>' for v, label in NUMBERS)
    return f'<section class="numbers" aria-label="Key numbers"><ul>{items}</ul></section>'


def render_about() -> str:
    paragraphs = "".join(f"<p>{escape(t)}</p>" for t in ABOUT_TEXT)
    facts = "".join(f"<dt>{escape(k)}</dt><dd>{escape(v)}</dd>" for k, v in FACTS)
    return f'<section class="about reveal" id="about"><h2>About me</h2>{paragraphs}<dl class="facts">{facts}</dl></section>'


def render_engagement(engagement: Engagement) -> str:
    meta = " · ".join(part for part in (engagement.role, engagement.period) if part)
    meta_html = f'<p class="meta">{escape(meta)}</p>' if meta else ""
    points = "".join(f"<li>{escape(point)}</li>" for point in engagement.points)
    return f'<div class="engagement"><h4>{escape(engagement.name)}</h4>{meta_html}<ul>{points}</ul></div>'


def render_position(position: Position) -> str:
    summary = f'<p class="summary">{escape(position.summary)}</p>' if position.summary else ""
    engagements = "".join(render_engagement(e) for e in position.engagements)
    return (
        f'<li class="role reveal"><span class="dot" aria-hidden="true"></span><p class="period">{escape(position.period)}</p>'
        f'<h3>{escape(position.org)} <small>{escape(position.place)}</small></h3><p class="title">{escape(position.title)}</p>'
        f'{summary}{engagements}</li>'
    )


def render_experience(positions: list[Position]) -> str:
    roles = "".join(render_position(p) for p in positions)
    return (
        f'<section id="experience"><h2>Experience</h2><ol class="timeline">{roles}</ol>'
        f'<p class="stack reveal"><strong>Stack</strong> {escape(STACK)}</p></section>'
    )


def render_links(project: Project) -> str:
    if not project.repo:
        return ""
    return f'<a class="repo" href="{escape(project.repo)}">View repository</a>'


def render_card(project: Project, index: int) -> str:
    media = (
        f'<img class="media" src="assets/{escape(project.title)}.webp" width="720" height="405" loading="lazy" decoding="async" alt="Output of {escape(project.title)}">'
        if project.title in MEDIA_PROJECTS
        else f'<div class="media media-text" aria-hidden="true"><span>{escape(project.title)}</span></div>'
    )
    tags = "".join(f'<span class="tag">{escape(t)}</span>' for t in project.tags[:4])
    return (
        f'<article class="card reveal" style="--i:{index % 3}">{media}<div class="card-body">'
        f'<h3>{escape(project.title)}</h3><p class="headline">{escape(project.headline)}</p>'
        f'<p class="problem">{escape(project.problem)}</p><div class="tags">{tags}</div>{render_links(project)}</div></article>'
    )


def render_projects(projects: list[Project]) -> str:
    cards = "".join(render_card(p, i) for i, p in enumerate(projects))
    return f'<section id="projects"><h2>Projects</h2><div class="grid">{cards}</div></section>'


def render_page(projects: list[Project], positions: list[Position], has_photo: bool) -> str:
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{SITE_TITLE} - Portfolio</title>
<meta name="description" content="{escape(HERO_STATEMENT)}">
<link rel="stylesheet" href="style.css"></head>
<body>
<nav class="bar"><a class="brand" href="#top">GM</a><span><a href="#about">About</a><a href="#experience">Experience</a><a href="#projects">Projects</a><a href="#contact">Contact</a></span></nav>
{render_hero(has_photo)}
<main>{render_numbers()}{render_about()}{render_experience(positions)}{render_projects(projects)}</main>
<footer id="contact"><h2>Let us talk</h2><p><a class="btn primary" href="mailto:{EMAIL}">{EMAIL}</a><a class="btn" href="{LINKEDIN}">LinkedIn</a><a class="btn" href="{GITHUB}">GitHub</a></p></footer>
<script src="site.js" defer></script></body></html>"""


def main() -> None:
    has_photo = prepare_photo()
    (ROOT / "index.html").write_text(render_page(load_projects(), load_positions(), has_photo))


if __name__ == "__main__":
    main()
