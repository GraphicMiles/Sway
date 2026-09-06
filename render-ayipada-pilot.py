#!/usr/bin/env python3
"""Render ÀYÍPADÀ 5-second pilot — 1920x1080 @30fps, H.264 + drone/bell sound."""
import os, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, DUR = 1920, 1080, 30, 5.0
NFRAMES = int(FPS * DUR)  # 150
UP = "/home/user/uploads"
OUTDIR = "/home/user/Sway/out"
os.makedirs(OUTDIR, exist_ok=True)

# (file, start, end, zoom_from, zoom_to, focus_from_xy, focus_to_xy)
SHOTS = [
    ("HRT9ZT0WUAIwsqs.jpg",                    0,  38, 1.00, 1.14, (0.50, 0.44), (0.50, 0.46)),
    ("IQ8pCvGxxhazRDvtwlZ8fevE-HRk9t9BpXlp4UpEyao.png", 32,  70, 1.02, 1.16, (0.50, 0.50), (0.50, 0.42)),
    ("02_the_collection.png",                  64, 104, 1.00, 1.12, (0.50, 0.55), (0.50, 0.45)),
    ("09_reaching_viewer.png",                 98, 128, 1.04, 1.24, (0.46, 0.52), (0.50, 0.46)),
    ("08_ghostly_figures.png",                122, 150, 1.00, 1.09, (0.50, 0.50), (0.50, 0.50)),
]
LORE = {
    0: "he has never owned a single face",
    1: "every mask — a life he wore",
    2: "king · warrior · child · spirit · fool",
    3: "he makes you question who you are",
}
TITLE, SUBTITLE = "ÀYÍPADÀ", "THE MANY-FACED GOD"

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f_lore = ImageFont.truetype(SERIF, 46)
f_title = ImageFont.truetype(SANS_B, 168)
f_sub = ImageFont.truetype(SANS, 44)

def cover(img):
    s = max(W / img.width, H / img.height)
    return img.resize((int(img.width * s + 0.5), int(img.height * s + 0.5)), Image.BICUBIC)

BASE = [cover(Image.open(os.path.join(UP, f)).convert("RGB")) for f, *_ in SHOTS]

# vignette mask
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
dx, dy = (xx / W - 0.5) * 2, (yy / H - 0.5) * 2
VIG = np.clip(1.0 - 0.42 * np.clip(dx**2 + dy**2 - 0.35, 0, None), 0.35, 1.0)[..., None]

def render_shot(i, frame):
    _, s, e, z0, z1, f0, f1 = SHOTS[i]
    p = (frame - s) / max(1, (e - s))
    p = min(1.0, max(0.0, p))
    z = z0 + (z1 - z0) * p
    fx = f0[0] + (f1[0] - f0[0]) * p
    fy = f0[1] + (f1[1] - f0[1]) * p
    zw, zh = int(W * z), int(H * z)
    im = BASE[i].resize((zw, zh), Image.BICUBIC)
    cx = min(max(int(zw * fx), W // 2), zw - W // 2)
    cy = min(max(int(zh * fy), H // 2), zh - H // 2)
    return im.crop((cx - W // 2, cy - H // 2, cx + W // 2, cy + H // 2))

def shot_alpha(i, frame):
    _, s, e, *_ = SHOTS[i]
    if frame < s or frame >= e:
        return 0.0
    a = 1.0
    if i > 0:
        ps = SHOTS[i - 1][2]  # prev end
        if frame < s + (ps - s):
            a = min(a, (frame - s) / max(1, (ps - s)))
    if i < len(SHOTS) - 1:
        ne = SHOTS[i + 1][1]  # next start
        if frame >= ne:
            a = min(a, (e - frame) / max(1, (e - ne)))
    return float(np.clip(a, 0, 1))

def tracked_w(draw, text, font, tr):
    return sum(draw.textlength(c, font=font) + tr for c in text) - tr

def draw_tracked(draw, cx, y, text, font, tr, fill):
    x = cx - tracked_w(draw, text, font, tr) / 2
    for c in text:
        draw.text((x, y), c, font=font, fill=fill)
        x += draw.textlength(c, font=font) + tr

BAR = 96
stills = {20: "still_mask.jpg", 55: "still_emerge.jpg", 85: "still_collection.jpg",
          115: "still_reach.jpg", 140: "still_title.jpg"}

import imageio_ffmpeg
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
tmp_vid = os.path.join(OUTDIR, "_pilot_video_only.mp4")
proc = subprocess.Popen([ffmpeg, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                         "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                         "-crf", "18", "-preset", "medium", tmp_vid],
                        stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
for n in range(NFRAMES):
    acc = np.zeros((H, W, 3), np.float32)
    tot = 0.0
    for i in range(len(SHOTS)):
        a = shot_alpha(i, n)
        if a > 0:
            acc += np.asarray(render_shot(i, n), np.float32) * a
            tot += a
    img = (acc / max(tot, 1e-6)).clip(0, 255).astype(np.uint8)
    # dim last shot for title legibility
    if n >= SHOTS[4][1]:
        k = min(1.0, (n - SHOTS[4][1]) / 10)
        img = (img.astype(np.float32) * (1 - 0.45 * k)).astype(np.uint8)
    a = img.astype(np.float32) * VIG
    g = np.random.default_rng(n).normal(0, 5.5, (H, W, 1)).astype(np.float32)
    a = np.clip(a + g, 0, 255).astype(np.uint8)
    fr = Image.fromarray(a)
    d = ImageDraw.Draw(fr, "RGBA")
    d.rectangle([0, 0, W, BAR], fill=(0, 0, 0, 255))
    d.rectangle([0, H - BAR, W, H], fill=(0, 0, 0, 255))
    # lore captions
    for i, txt in LORE.items():
        _, s, e, *_ = SHOTS[i]
        if s <= n < e:
            fo = min(1.0, (n - s) / 8, (e - n) / 8)
            if fo > 0:
                tw = d.textlength(txt, font=f_lore)
                d.text(((W - tw) / 2 + 2, H - BAR - 108 + 2), txt, font=f_lore, fill=(0, 0, 0, int(220 * fo)))
                d.text(((W - tw) / 2, H - BAR - 108), txt, font=f_lore, fill=(240, 230, 210, int(255 * fo)))
    # title card
    _, ts, te, *_ = SHOTS[4]
    if n >= ts:
        fo = min(1.0, (n - ts) / 10)
        if fo > 0:
            ty = 300
            draw_tracked(d, W / 2 + 3, ty + 3, TITLE, f_title, 26, (0, 0, 0, int(230 * fo)))
            draw_tracked(d, W / 2, ty, TITLE, f_title, 26, (176, 132, 255, int(255 * fo)))
            draw_tracked(d, W / 2, ty + 210, SUBTITLE, f_sub, 18, (235, 225, 245, int(240 * fo)))
            d.line([W/2 - 180, ty + 290, W/2 + 180, ty + 290], fill=(176, 132, 255, int(160 * fo)), width=2)
    # global fades
    if n < 8 or n >= NFRAMES - 8:
        k = min(n / 8, (NFRAMES - 1 - n) / 8)
        fr = Image.blend(Image.new("RGB", (W, H)), fr, float(np.clip(k, 0, 1)))
    proc.stdin.write(fr.tobytes())
    if n in stills:
        fr.save(os.path.join(OUTDIR, stills[n]), quality=88)
proc.stdin.close(); proc.wait()

# ---- sound: deep thump + swelling drone + bell at title ----
SR = 44100
t = np.arange(int(SR * DUR)) / SR
thump = np.sin(2 * np.pi * 58 * t) * np.exp(-t * 7) * 0.55 * (t < 1.2)
swell = (t / DUR) ** 1.6 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.4 * t))
drone = (np.sin(2 * np.pi * 55 * t) * 0.22 + np.sin(2 * np.pi * 110 * t) * 0.10
         + np.sin(2 * np.pi * 82.5 * t + 1.3) * 0.08) * swell
tb = t - (122 / FPS)
bell = sum(np.sin(2 * np.pi * f * np.clip(tb, 0, None) + p) * np.exp(-np.clip(tb, 0, None) * 2.6) * amp
           for f, p, amp in [(660, 0, .16), (990, 1.1, .10), (1320, 2.0, .08), (440, .5, .10)]) * (tb > 0)
fade_out = np.clip((DUR - t) / 0.4, 0, 1)
mix = np.clip((thump + drone + bell) * fade_out, -1, 1)
mix = (mix / max(1e-6, np.abs(mix).max()) * 0.89 * 32767).astype(np.int16)
wav_p = os.path.join(OUTDIR, "_pilot_audio.wav")
wv = wave.open(wav_p, "wb"); wv.setnchannels(1); wv.setsampwidth(2); wv.setframerate(SR)
wv.writeframes(mix.tobytes()); wv.close()

final = os.path.join(OUTDIR, "ayipada-5sec-pilot.mp4")
subprocess.run([ffmpeg, "-y", "-i", tmp_vid, "-i", wav_p, "-c:v", "copy",
                "-c:a", "aac", "-b:a", "160k", "-shortest", final],
               check=True, capture_output=True)
os.remove(tmp_vid); os.remove(wav_p)
print("OK ->", final, os.path.getsize(final), "bytes")
