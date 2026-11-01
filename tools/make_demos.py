import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PORTFOLIO = Path.home() / "portfolio"
OUT = Path(__file__).resolve().parent.parent / "assets"
SIZE = (720, 405)
BG = (15, 23, 42)
PANEL = (30, 41, 59)
INK = (226, 232, 240)
MUTED = (148, 163, 184)
BAR = (56, 189, 248)
BAR_ALT = (251, 146, 60)
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


@dataclass(frozen=True)
class Bar:
    label: str
    value: float
    shown: str
    alt: bool = False


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, size)


def bar_chart(name: str, title: str, caption: str, bars: list[Bar], maximum: float) -> None:
    image = Image.new("RGB", SIZE, BG)
    draw = ImageDraw.Draw(image)
    draw.text((32, 24), title, font=font(24), fill=INK)
    draw.text((32, 58), caption, font=font(14), fill=MUTED)
    top, row = 110, (SIZE[1] - 140) // len(bars)
    for index, bar in enumerate(bars):
        y = top + index * row
        width = int((SIZE[0] - 330) * bar.value / maximum)
        draw.text((32, y + 6), bar.label, font=font(15), fill=INK)
        draw.rounded_rectangle((230, y, 230 + max(width, 6), y + row - 18), radius=6, fill=BAR_ALT if bar.alt else BAR)
        draw.text((238 + width, y + 6), bar.shown, font=font(16), fill=INK)
    image.save(OUT / f"{name}.webp", quality=82)


def line_chart(name: str, title: str, caption: str, points: list[tuple[str, float]]) -> None:
    image = Image.new("RGB", SIZE, BG)
    draw = ImageDraw.Draw(image)
    draw.text((32, 24), title, font=font(24), fill=INK)
    draw.text((32, 58), caption, font=font(14), fill=MUTED)
    left, right, top, bottom = 70, SIZE[0] - 40, 110, SIZE[1] - 60
    draw.rectangle((left, top, right, bottom), fill=PANEL)
    peak = max(value for _, value in points) * 1.15
    step = (right - left) / (len(points) - 1)
    coords = [(left + i * step, bottom - (bottom - top) * value / peak) for i, (_, value) in enumerate(points)]
    draw.line(coords, fill=BAR, width=4)
    for (x, y), (label, value) in zip(coords, points):
        draw.ellipse((x - 6, y - 6, x + 6, y + 6), fill=BAR_ALT)
        draw.text((x - 18, y - 28), f"{value:.0f}", font=font(14), fill=INK)
        draw.text((x - 10, bottom + 10), label, font=font(14), fill=MUTED)
    image.save(OUT / f"{name}.webp", quality=82)


def detection_demo() -> None:
    from vision_agent.detector import OnnxDetector

    source = PORTFOLIO / "vision-agent-mcp/data/coco128/images/train2017/000000000009.jpg"
    image = Image.open(source).convert("RGB")
    detections = OnnxDetector(PORTFOLIO / "vision-agent-mcp/models/yolov8n.onnx").detect(source)
    draw = ImageDraw.Draw(image)
    for detection in detections:
        draw.rectangle(detection.box, outline=BAR_ALT, width=3)
        draw.text((detection.box[0] + 4, detection.box[1] + 2), f"{detection.label} {detection.confidence:.2f}", font=font(14), fill=(255, 255, 255))
    image.thumbnail(SIZE)
    canvas = Image.new("RGB", SIZE, BG)
    canvas.paste(image, ((SIZE[0] - image.width) // 2, (SIZE[1] - image.height) // 2))
    canvas.save(OUT / "vision-agent-mcp.webp", quality=82)


def mean_by_kind() -> dict[str, float]:
    seeds = json.loads((PORTFOLIO / "cv-label-audit/results/audit-results.json").read_text())["seeds"]
    kinds = ("deleted", "relabeled", "shifted", "spurious")
    return {k: sum(s["thresholds"][0]["recall_by_kind"][k] for s in seeds) / len(seeds) for k in kinds}


def main() -> None:
    OUT.mkdir(exist_ok=True)
    detection_demo()
    recall = mean_by_kind()
    bar_chart("cv-label-audit", "Label errors found, by kind", "Injected errors on COCO128, 5-seed mean, min score 0.25",
              [Bar(k, v, f"{v:.2f}") for k, v in recall.items()], 1.0)
    lab = json.loads((PORTFOLIO / "cv-training-lab/results/lab-results.json").read_text())["comparison"]
    bar_chart("cv-training-lab", "Test accuracy, CIFAR-10", "Same data, same budget, three models",
              [Bar(row["config"]["architecture"], row["test_accuracy"], f"{row['test_accuracy']:.3f}") for row in lab], 1.0)
    bar_chart("lidar-camera-fusion", "Median distance error (m)", "KITTI drive, near-face ground truth, lower is better",
              [Bar("camera only", 2.45, "2.45 m", True), Bar("camera + LiDAR", 0.35, "0.35 m")], 2.8)
    cpu = json.loads((PORTFOLIO / "edge-inference-bench/results/cpu-matrix.json").read_text())
    points = [(row["label"].removeprefix("threads_"), row["decode_tokens_per_second"]) for row in cpu if row["label"].startswith("threads_")]
    line_chart("edge-inference-bench", "CPU decode speed vs threads", "Tokens per second, 0.5B model, Q8_0", points)
    serving = json.loads((PORTFOLIO / "ml-feature-serving/results/serving-results.json").read_text())["leakage"]
    bar_chart("ml-feature-serving", "AUC: honest vs leaky features", "Point-in-time features against future data leaking in",
              [Bar("point-in-time", serving["auc_point_in_time"], f"{serving['auc_point_in_time']:.3f}"),
               Bar("future leaked", serving["auc_with_future_data"], f"{serving['auc_with_future_data']:.3f}", True)], 1.0)
    modes = json.loads((PORTFOLIO / "agent-retrieval-service/results/retrieval-results.json").read_text())["modes"]
    bar_chart("agent-retrieval-service", "Retrieval quality, nDCG@10", "SciFact, 300 queries",
              [Bar(k, v["ndcg_at_10"], f"{v['ndcg_at_10']:.3f}", k == "hybrid") for k, v in modes.items()], 1.0)


if __name__ == "__main__":
    main()
