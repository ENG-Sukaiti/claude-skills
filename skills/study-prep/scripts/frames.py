# /// script
# requires-python = ">=3.11"
# dependencies = ["av>=12", "pillow>=10"]
# ///
"""Grab frames from a video, to see what was written or shown on screen.
Same on macOS and Linux (no ffmpeg install needed).

    sh scripts/run frames.py <video> --to <dir> --at 12:40 [--at 1:05:10 ...]
        one PNG per timestamp (m:ss, h:mm:ss or seconds)
    sh scripts/run frames.py <video> --to <dir> --every 240 [--sheet]
        a frame every N seconds; --sheet also tiles them, 4 across, into
        sheet-NN.png with timestamps, to find the right moment quickly
"""

import argparse
from pathlib import Path

import av
from PIL import Image, ImageDraw


def seconds(t):
    s = 0.0
    for part in t.split(":"):
        s = s * 60 + float(part)
    return s


def stamp(s):
    s = int(s)
    return f"{s // 3600}:{s // 60 % 60:02d}:{s % 60:02d}" if s >= 3600 else f"{s // 60}:{s % 60:02d}"


def grab(path, t):
    with av.open(path) as c:
        v = c.streams.video[0]
        c.seek(int(t / v.time_base), stream=v, backward=True, any_frame=False)
        for f in c.decode(v):
            if f.time is not None and f.time >= t - 0.05:
                return f.to_image()
    return None


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("video")
    p.add_argument("--to", required=True)
    p.add_argument("--at", action="append", default=[])
    p.add_argument("--every", type=float)
    p.add_argument("--sheet", action="store_true")
    a = p.parse_args()
    out = Path(a.to)
    out.mkdir(parents=True, exist_ok=True)

    times = [seconds(t) for t in a.at]
    if a.every:
        with av.open(a.video) as c:
            dur = float(c.duration or 0) / av.time_base
        times += [i * a.every for i in range(int(dur // a.every) + 1)]
    if not times:
        raise SystemExit("Give --at <time> or --every <seconds>.")

    shots = []
    for t in times:
        img = grab(a.video, t)
        if img is None:
            continue
        f = out / f"frame-{stamp(t).replace(':', '-')}.png"
        img.save(f)
        shots.append((t, img))
        print(f)

    if a.sheet and shots:
        w = 640
        for n in range(0, len(shots), 8):
            batch = shots[n:n + 8]
            thumbs = [(t, im.resize((w, int(im.height * w / im.width)))) for t, im in batch]
            h = thumbs[0][1].height
            sheet = Image.new("RGB", (w * 4, h * ((len(thumbs) + 3) // 4)), "black")
            draw = ImageDraw.Draw(sheet)
            for i, (t, im) in enumerate(thumbs):
                x, y = (i % 4) * w, (i // 4) * h
                sheet.paste(im, (x, y))
                draw.rectangle([x, y, x + 70, y + 20], fill="black")
                draw.text((x + 4, y + 4), stamp(t), fill="yellow")
            f = out / f"sheet-{n // 8 + 1:02d}.png"
            sheet.save(f)
            print(f)


if __name__ == "__main__":
    main()
