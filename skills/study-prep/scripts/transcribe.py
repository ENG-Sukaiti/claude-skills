# /// script
# requires-python = ">=3.11"
# dependencies = ["faster-whisper", "numpy"]
# ///
"""Transcribe a lecture recording locally with faster-whisper (no cloud, no API key).

Usage:
    sh scripts/run transcribe.py <video-or-audio> <out.txt> [--language ar] [--model medium] [--chunk-min 10] [--jobs 4]

Splits the audio into chunks and transcribes them in parallel worker processes,
then writes one "[mm:ss] text" line per segment, in order, to <out.txt>.
The first chunk is written to <out.txt>.part0 as soon as it finishes, because
lecturers usually talk about the exam in the first minutes.
"""
import argparse
import os
import shutil
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np

SAMPLE_RATE = 16000


def load_audio(path: str, start: float, dur: float) -> np.ndarray:
    """Mono 16 kHz float audio for one chunk. Uses the ffmpeg command if it's
    installed (some PyAV builds reject faster-whisper's own file call),
    otherwise PyAV, which faster-whisper already brings along, so nothing
    extra needs installing on macOS or Linux."""
    if shutil.which("ffmpeg"):
        raw = subprocess.run(
            ["ffmpeg", "-loglevel", "error", "-ss", str(start), "-t", str(dur), "-i", path,
             "-f", "s16le", "-ac", "1", "-ar", str(SAMPLE_RATE), "-"],
            capture_output=True, check=True,
        ).stdout
        return np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    import av

    out = []
    with av.open(path) as c:
        stream = c.streams.audio[0]
        c.seek(int(start / stream.time_base), stream=stream)
        res = av.AudioResampler(format="s16", layout="mono", rate=SAMPLE_RATE)
        for frame in c.decode(stream):
            if frame.time is not None and frame.time > start + dur:
                break
            if frame.time is not None and frame.time + frame.samples / frame.sample_rate < start:
                continue
            for f in res.resample(frame):
                out.append(f.to_ndarray().reshape(-1))
    if not out:
        return np.zeros(0, np.float32)
    return np.concatenate(out).astype(np.float32) / 32768


def duration(path: str) -> float:
    if shutil.which("ffprobe"):
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
            capture_output=True, text=True, check=True,
        ).stdout
        return float(out.strip())
    import av

    with av.open(path) as c:
        return float(c.duration) / av.time_base


def transcribe_chunk(path: str, start: float, dur: float, model: str, threads: int, language: str | None, device: str = "cpu") -> list[str]:
    from faster_whisper import WhisperModel

    m = WhisperModel(model, device=device, compute_type="int8" if device == "cpu" else "float16", cpu_threads=threads)
    segs, _ = m.transcribe(
        load_audio(path, start, dur),
        language=language,
        vad_filter=True,
        # Without this, Whisper feeds its own output back in and can lock into
        # repeating one token ("y y y ...") for the rest of the file.
        condition_on_previous_text=False,
        compression_ratio_threshold=2.0,
    )
    lines = []
    for s in segs:
        t = start + s.start
        lines.append(f"[{int(t // 60)}:{int(t % 60):02d}] {s.text.strip()}")
    return lines


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("src")
    p.add_argument("out")
    p.add_argument("--language", default=None, help="ISO code (ar, en, fr...); default: detect per chunk. Set it for mixed-language lectures")
    p.add_argument("--model", default="medium", help="medium is the smallest that handles Arabic well; small is faster for English")
    p.add_argument("--device", default="cpu", help="cpu (works everywhere) or cuda (NVIDIA; needs CUDA 12 cuBLAS + cuDNN 9 installed)")
    p.add_argument("--chunk-min", type=float, default=10)
    p.add_argument("--jobs", type=int, default=4, help="parallel workers; each loads its own model (~1.5 GB RAM for medium)")
    a = p.parse_args()

    total = duration(a.src)
    step = a.chunk_min * 60
    starts = [i * step for i in range(int(total // step) + 1) if i * step < total]
    threads = max(1, (os.cpu_count() or 4) // a.jobs)

    results: dict[int, list[str]] = {}
    with ProcessPoolExecutor(max_workers=a.jobs) as ex:
        futs = {ex.submit(transcribe_chunk, a.src, s, step, a.model, threads, a.language, a.device): i for i, s in enumerate(starts)}
        for f in as_completed(futs):
            i = futs[f]
            results[i] = f.result()
            print(f"chunk {i + 1}/{len(starts)} done", file=sys.stderr, flush=True)
            if i == 0:
                with open(a.out + ".part0", "w") as fh:
                    fh.write("\n".join(results[0]) + "\n")

    with open(a.out, "w") as fh:
        for i in range(len(starts)):
            fh.write("\n".join(results[i]) + "\n")
    print(f"wrote {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
