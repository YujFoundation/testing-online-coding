from __future__ import annotations

import asyncio
import json
import os
import subprocess
from pathlib import Path

import edge_tts
from pydub import AudioSegment
from pydub.silence import detect_nonsilent

TOTAL_MS = int(os.environ.get("TOTAL_MS", "805000"))
VOICE = os.environ.get("VOICE", "hi-IN-SwaraNeural")
TARGET_DBFS = float(os.environ.get("TARGET_DBFS", "-18.0"))
OUT = Path("vb_video2_audio")
CUE_DIR = OUT / "voice_cues"
TMP = Path("tmp_vb_video2_audio")
OUT.mkdir(exist_ok=True)
CUE_DIR.mkdir(exist_ok=True)
TMP.mkdir(exist_ok=True)

CUES = json.loads(Path("cues_video2.json").read_text(encoding="utf-8"))

async def synth(text: str, out_mp3: Path) -> None:
    speaker = edge_tts.Communicate(text, VOICE, rate="-5%", pitch="+0Hz", volume="+0%")
    await speaker.save(str(out_mp3))

def trim(seg: AudioSegment) -> AudioSegment:
    if seg.dBFS == float("-inf"):
        return seg
    ranges = detect_nonsilent(seg, min_silence_len=70, silence_thresh=max(-47, seg.dBFS - 28), seek_step=5)
    if not ranges:
        return seg
    a = max(0, ranges[0][0] - 80)
    b = min(len(seg), ranges[-1][1] + 130)
    return seg[a:b]

def atempo_chain(factor: float) -> str:
    parts = []
    while factor > 2.0:
        parts.append(2.0)
        factor /= 2.0
    while factor < 0.5:
        parts.append(0.5)
        factor /= 0.5
    parts.append(factor)
    return ",".join(f"atempo={x:.6f}" for x in parts)

def fit(seg: AudioSegment, max_ms: int, idx: int) -> AudioSegment:
    if len(seg) <= max_ms:
        return seg
    factor = len(seg) / max_ms
    src = TMP / f"fit_{idx:03d}_src.wav"
    dst = TMP / f"fit_{idx:03d}_dst.wav"
    seg.export(src, format="wav")
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(src), "-filter:a", atempo_chain(factor),
        "-ar", "48000", "-ac", "1", str(dst)
    ], check=True)
    return AudioSegment.from_wav(dst)

def srt_time(sec: float) -> str:
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1_000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

async def main() -> None:
    master = AudioSegment.silent(duration=TOTAL_MS, frame_rate=48000).set_channels(1)
    meta = []
    srt = []
    script = []
    for i, cue in enumerate(CUES, 1):
        start = float(cue["start"])
        text = str(cue["text"])
        mp3 = TMP / f"{i:03d}.mp3"
        await synth(text, mp3)
        seg = trim(AudioSegment.from_file(mp3)).set_frame_rate(48000).set_channels(1)
        if seg.dBFS != float("-inf"):
            seg = seg.apply_gain(TARGET_DBFS - seg.dBFS)
        next_start = float(CUES[i]["start"]) if i < len(CUES) else TOTAL_MS / 1000
        seg = fit(seg, max(900, int((next_start - start) * 1000) - 280), i)
        wav = CUE_DIR / f"cue_{i:03d}.wav"
        seg.export(wav, format="wav")
        master = master.overlay(seg, position=int(start * 1000))
        end = min(TOTAL_MS / 1000, start + len(seg) / 1000)
        meta.append({"start": start, "end": end, "text": text, "audio": wav.name})
        srt.extend([str(i), f"{srt_time(start)} --> {srt_time(end)}", text, ""])
        script.append(text)

    wav_master = OUT / "Vishranti_Bindu_Video2_Hindi_Narration.wav"
    m4a_master = OUT / "Vishranti_Bindu_Video2_Hindi_Narration.m4a"
    master.export(wav_master, format="wav")
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(wav_master), "-af", "highpass=f=70,lowpass=f=12000,alimiter=limit=0.94",
        "-t", str(TOTAL_MS / 1000), "-c:a", "aac", "-b:a", "192k",
        "-ar", "48000", "-ac", "2", str(m4a_master)
    ], check=True)
    (OUT / "cues.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "Vishranti_Bindu_Video2_Hindi_Subtitles.srt").write_text("\n".join(srt), encoding="utf-8")
    (OUT / "Vishranti_Bindu_Video2_Hindi_Voiceover_Script.txt").write_text("\n\n".join(script), encoding="utf-8")

asyncio.run(main())
