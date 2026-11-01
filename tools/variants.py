from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from build import EMAIL, GITHUB, LINKEDIN, ROOT, TYPE_ORDER, SITE_TITLE, Project, escape, load_projects, repo_line

CV_PATH = "../../assets/guilherme-monteiro-cv.pdf"
IMAGE_TITLES = {
    "vision-agent-mcp": "vision-agent-mcp",
    "cv-label-audit": "cv-label-audit",
    "cv-training-lab": "cv-training-lab",
    "lidar-camera-fusion": "lidar-camera-fusion",
    "edge-inference-bench": "edge-inference-bench",
    "ml-feature-serving": "ml-feature-serving",
    "agent-retrieval-service": "agent-retrieval-service",
}
PHOTO_SOURCE = Path.home() / "Downloads" / "profile-photo.jpg"
PHOTO_TARGET = ROOT / "assets" / "profile.webp"
PHOTO_MAX_SIZE = 400
ABOUT_TEXT = (
    "I am an applied ML engineer who works close to the client. At ALTAVE I was Forward Deployed Engineer for a drilling client, I manage a maritime monitoring project, and I led the architecture of a real-time GPU vision pipeline.",
    "I like to own a product end to end, from Figma and frontend to backend, AI models and hardware installation.",
    "Today I focus on agentic systems and computer vision, and I run a multi-agent engineering workflow every day.",
)
FACTS = (
    ("Location", "Santos, São Paulo, Brazil (remote)"),
    ("Languages", "Portuguese (native), English (native or bilingual)"),
    ("Education", "Bachelor's in Mechatronics Engineering, Escola Politécnica da USP, 2018-2023"),
)
HERO_STATEMENT = "I turn client problems into measured computer-vision and agentic systems."
HERO_SUPPORT = "Product design, client interface and engineering in one person. Every project below states the result and its limits."


@dataclass(frozen=True)
class Number:
    value: str
    label: str


@dataclass(frozen=True)
class Step:
    title: str
    text: str


@dataclass(frozen=True)
class Variant:
    key: str
    name: str
    body_class: str
    eyebrow: str


NUMBERS = (
    Number("0.35 m", "median distance error with LiDAR fusion, against 2.45 m for the camera alone"),
    Number("266 tok/s", "local language-model decode on a laptop GPU, against 78 on the CPU"),
    Number("90.4%", "test accuracy of a pretrained ResNet-18 on CIFAR-10"),
    Number("0.72 vs 0.94", "AUC with honest features against features that leak the future"),
)
STEPS = (
    Step("Listen", "I talk to the client and write the problem as a measurable question."),
    Step("Design", "I write the design note first and agree the contract before code."),
    Step("Build", "I build end to end: model, service, interface and deployment."),
    Step("Measure", "I report the result with its limits, including what did not work."),
)
SERVICES = (
    Step("Computer vision", "Detection, fusion and inference on GPU and edge devices."),
    Step("Agentic systems", "MCP tools, retrieval services and evaluation of agent behaviour."),
    Step("ML and data services", "Feature serving, drift monitoring and contract-first Python backends."),
    Step("Delivery", "Client interface, roadmap and on-site delivery for safety-critical work."),
)
VARIANTS = (
    Variant("a", "Product studio", "v-a", "Applied ML engineer"),
    Variant("b", "Bold editorial", "v-b", "Applied ML engineer"),
    Variant("c", "Dark technical", "v-c", "Applied ML engineer"),
)


def prepare_photo() -> bool:
    if not PHOTO_SOURCE.exists():
        return False
    image = Image.open(PHOTO_SOURCE).convert("RGB")
    image.thumbnail((PHOTO_MAX_SIZE, PHOTO_MAX_SIZE))
    image.save(PHOTO_TARGET, quality=82)
    return True


def render_photo(has_photo: bool) -> str:
    if has_photo:
        return '<img class="photo" src="../../assets/profile.webp" width="400" height="400" alt="Portrait of Guilherme Monteiro" decoding="async">'
    return '<div class="photo placeholder" role="img" aria-label="Profile photo placeholder"><span>GM</span></div>'


def render_about(has_photo: bool) -> str:
    paragraphs = "".join(f"<p>{escape(t)}</p>" for t in ABOUT_TEXT)
    facts = "".join(f"<dt>{escape(k)}</dt><dd>{escape(v)}</dd>" for k, v in FACTS)
    return (
        f'<section class="about reveal" id="about">{render_photo(has_photo)}<div><h2>About me</h2>'
        f'<p class="draft">Draft text for review</p>{paragraphs}<dl class="facts">{facts}</dl></div></section>'
    )


def render_card(project: Project, index: int) -> str:
    image = IMAGE_TITLES.get(project.title)
    media = (
        f'<img class="media" src="../../assets/{image}.webp" width="720" height="405" loading="lazy" decoding="async" alt="Output of {escape(project.title)}">'
        if image
        else '<div class="media media-text" aria-hidden="true"><span>Private company work</span></div>'
    )
    tags = "".join(f'<span class="tag">{escape(tag)}</span>' for tag in project.tags[:4])
    return (
        f'<article class="card reveal" style="--i:{index % 3}">{media}<div class="card-body">'
        f'<p class="kind">{escape(project.type)}</p><h3>{escape(project.title)}</h3>'
        f'<p class="headline">{escape(project.headline)}</p><p class="problem">{escape(project.problem)}</p>'
        f'<div class="tags">{tags}</div><details><summary>Build, result and limits</summary><dl>'
        f'<dt>Built</dt><dd>{escape(project.built)}</dd><dt>Result</dt><dd>{escape(project.result)}</dd>'
        f'<dt>Limits</dt><dd>{escape(project.limits)}</dd><dt>Link</dt><dd>{repo_line(project)}</dd></dl></details></div></article>'
    )


def ordered(projects: list[Project]) -> list[Project]:
    with_media = [p for p in projects if p.title in IMAGE_TITLES]
    without = [p for p in projects if p.title not in IMAGE_TITLES]
    return with_media + sorted(without, key=lambda p: TYPE_ORDER.index(p.type))


def render_numbers() -> str:
    items = "".join(f'<li class="reveal"><strong>{escape(n.value)}</strong><span>{escape(n.label)}</span></li>' for n in NUMBERS)
    return f'<section class="numbers" aria-label="Key measured numbers"><ul>{items}</ul></section>'


def render_steps(title: str, steps: tuple[Step, ...], css: str) -> str:
    items = "".join(
        f'<li class="reveal" style="--i:{i}"><span class="step-no">{i + 1:02d}</span><h3>{escape(s.title)}</h3><p>{escape(s.text)}</p></li>'
        for i, s in enumerate(steps)
    )
    return f'<section class="{css}"><h2>{escape(title)}</h2><ol>{items}</ol></section>'


def render_hero(variant: Variant) -> str:
    art = '<div class="hero-art" aria-hidden="true"><i></i><i></i><i></i><b></b></div>' if variant.key == "c" else ""
    return (
        f'<header class="hero" id="top">{art}<div class="hero-inner"><p class="eyebrow">{escape(variant.eyebrow)}</p>'
        f'<h1>{escape(HERO_STATEMENT)}</h1><p class="support">{escape(HERO_SUPPORT)}</p>'
        f'<p class="cta"><a class="btn primary" href="{CV_PATH}" download>Download CV</a>'
        f'<a class="btn" href="#contact">Contact</a></p></div></header>'
    )


def render_page(variant: Variant, projects: list[Project], has_photo: bool) -> str:
    cards = "".join(render_card(p, i) for i, p in enumerate(ordered(projects)))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{SITE_TITLE} - Portfolio ({escape(variant.name)})</title>
<meta name="description" content="{escape(HERO_STATEMENT)}">
<link rel="stylesheet" href="../base.css"><link rel="stylesheet" href="style.css"></head>
<body class="{variant.body_class}">
<nav class="bar"><a class="brand" href="#top">GM</a><span><a href="#projects">Projects</a><a href="#about">About</a><a href="#how">How I work</a><a href="#services">Services</a><a href="#contact">Contact</a></span></nav>
{render_hero(variant)}
{render_numbers()}
<main>{render_about(has_photo)}<section id="projects"><h2>Projects</h2><div class="grid">{cards}</div></section>
<div id="how">{render_steps("How I work", STEPS, "steps")}</div>
<div id="services">{render_steps("Services", SERVICES, "steps services")}</div></main>
<footer id="contact"><h2>Let us talk</h2><p><a class="btn primary" href="mailto:{EMAIL}">{EMAIL}</a><a class="btn" href="{LINKEDIN}">LinkedIn</a><a class="btn" href="{GITHUB}">GitHub</a></p>
<p class="small">Company work appears at the level of the public resume, as text only. No tracking, no external fonts.</p></footer>
<script src="../shared.js" defer></script></body></html>"""


def main() -> None:
    projects = load_projects()
    has_photo = prepare_photo()
    for variant in VARIANTS:
        (ROOT / "variants" / variant.key / "index.html").write_text(render_page(variant, projects, has_photo))


if __name__ == "__main__":
    main()
