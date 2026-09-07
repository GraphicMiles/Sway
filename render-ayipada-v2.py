#!/usr/bin/env python3
"""AYIPADA v2 — real 2D motion-comic animation (24fps, 10s).
Rig: luma-keyed cutout + idle body motion (on 2s) + swinging bell parts
+ eye glow + grin shimmer + animated void (smoke/dust/rays) + camera.
Shots: cartoon idle -> reach impact -> collection title.
Usage: python3 render-ayipada-v2.py [--preview]  (preview dumps 3 stills only)
"""
import os, sys, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, DUR = 1920, 1080, 24, 10.0
NFRAMES = int(FPS * DUR)  # 240
UP = "/home/user/uploads"
OUTDIR = "/home/user/Sway/out"
PREVIEW = "--preview" in sys.argv

# ---------------- helpers ----------------
def luma_key(img, lo=9, hi=46, blur=1.2):
    g = np.asarray(img.convert("L")).astype(np.float32)
    m = np.clip((g - lo) / (hi - lo), 0, 1)
    m = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(blur))
    out = img.copy(); out.putalpha(m)
    return out

def add_glow(base, xy, radius, color, alpha):
    """Additive radial glow on RGB PIL image."""
    x, y = int(xy[0]), int(xy[1])
    r = int(radius)
    glow = Image.new("L", (r * 2, r * 2), 0)
    d = ImageDraw.Draw(glow)
    for i in range(10, 0, -1):
        d.ellipse([r - r * i / 10, r - r * i / 10, r + r * i / 10, r + r * i / 10],
                  fill=int(alpha * (11 - i) / 10))
    glow = glow.filter(ImageFilter.GaussianBlur(r / 8))
    solid = Image.new("RGB", (r * 2, r * 2), color)
    base.paste(solid, (x - r, y - r), glow)
    return base

def sparkle_sprite(size=46):
    s = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(s)
    c = size / 2
    d.line([c, 2, c, size - 2], fill=(255, 255, 255, 200), width=3)
    d.line([2, c, size - 2, c], fill=(255, 255, 255, 200), width=3)
    d.line([c, c - 8, c, c + 8], fill=(255, 255, 255, 255), width=6)
    return s.filter(ImageFilter.GaussianBlur(1))

SPARK = sparkle_sprite()

def paste_sprite(base, sprite, xy, scale=1.0, alpha=1.0, angle=0):
    sz = sprite.size
    sp = sprite.resize((max(1, int(sz[0] * scale)), max(1, int(sz[1] * scale))), Image.BICUBIC)
    if angle:
        sp = sp.rotate(angle, expand=True, resample=Image.BICUBIC)
    if alpha < 1.0:
        a = sp.getchannel("A").point(lambda v: int(v * alpha))
        sp.putalpha(a)
    base.paste(sp, (int(xy[0] - sp.width / 2), int(xy[1] - sp.height / 2)), sp)

# ---------------- shot 1 assets: cartoon rig ----------------
CARTOON = Image.open(os.path.join(UP, "02_emerging.png")).convert("RGB")  # 1367x768

# bell part boxes (x0,y0,x1,y1) + pivot (top-center) in original px
BELLS = [
    {"box": (735, 90, 810, 205), "pivot": (772, 96),  "phase": 0.0, "freq": 1.45, "amp": 9},
    {"box": (845, 95, 895, 175), "pivot": (868, 100), "phase": 1.7, "freq": 1.9,  "amp": 11},
    {"box": (1060, 95, 1112, 180), "pivot": (1085, 100), "phase": 3.1, "freq": 1.7, "amp": 10},
    {"box": (1150, 115, 1215, 225), "pivot": (1182, 120), "phase": 4.4, "freq": 1.5, "amp": 9},
]

def erase_bells(img):
    img = img.copy()
    d = ImageDraw.Draw(img)
    for b in BELLS:
        x0, y0, x1, y1 = b["box"]
        ring = np.concatenate([
            np.asarray(img.crop((x0, y0, x1, y0 + 6))).reshape(-1, 3),
            np.asarray(img.crop((x0, y1 - 6, x1, y1))).reshape(-1, 3),
            np.asarray(img.crop((x0, y0, x0 + 6, y1))).reshape(-1, 3),
            np.asarray(img.crop((x1 - 6, y0, x1, y1))).reshape(-1, 3),
        ])
        fill = tuple(int(v) for v in np.median(ring, axis=0))
        d.rectangle(b["box"], fill=fill)
    return img.filter(ImageFilter.GaussianBlur(0.6))

CHAR_NOBELLS = luma_key(erase_bells(CARTOON))
BELL_PARTS = []
for b in BELLS:
    part = luma_key(CARTOON.crop(b["box"]))
    BELL_PARTS.append(part)

# face landmarks (orig px): eye slits + grin (for glow / shimmer)
EYE_L, EYE_R = (985, 300), (1120, 305)
GRIN = (1025, 405)

# character placement: cover 1920x1080 from 1367x768 (scale ~1.405) then offset
CS = max(W / CARTOON.width, H / CARTOON.height)  # cover scale
CHAR_W, CHAR_H = int(CARTOON.width * CS), int(CARTOON.height * CS)
CHAR_BASE = CHAR_NOBELLS.resize((CHAR_W, CHAR_H), Image.BICUBIC)
BELL_BASE = [p.resize((int(p.width * CS), int(p.height * CS)), Image.BICUBIC) for p in BELL_PARTS]

def orig2char(x, y):
    return (x * CS, y * CS)

# ---------------- other shots ----------------
REACH = Image.open(os.path.join(UP, "09_reaching_viewer.png")).convert("RGB")
COLLECT = Image.open(os.path.join(UP, "02_the_collection.png")).convert("RGB")

def cover(img):
    s = max(W / img.width, H / img.height)
    return img.resize((int(img.width * s + .5), int(img.height * s + .5)), Image.BICUBIC)

REACH_C, COLLECT_C = cover(REACH), cover(COLLECT)

# ---------------- atmosphere ----------------
rng = np.random.default_rng(7)
def puff_sprite(size=300):
    im = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(im)
    for _ in range(26):
        x, y = rng.integers(0, size, 2)
        r = rng.integers(size // 10, size // 4)
        d.ellipse([x - r, y - r, x + r, y + r], fill=int(rng.integers(24, 70)))
    return im.filter(ImageFilter.GaussianBlur(size / 12))

PUFFS = [puff_sprite() for _ in range(3)]
SMOKE = [{"x": float(rng.uniform(-200, W)), "y": float(rng.uniform(0, H)),
          "s": float(rng.uniform(2.2, 4.6)), "v": float(rng.uniform(6, 20)),
          "a": float(rng.uniform(40, 90)), "p": int(rng.integers(0, 3))} for _ in range(16)]
DUST = [{"x": float(rng.uniform(0, W)), "y": float(rng.uniform(0, H)),
         "v": float(rng.uniform(8, 30)), "ph": float(rng.uniform(0, 6.28)),
         "s": float(rng.uniform(0.5, 1.6))} for _ in range(90)]
EMBERS = [{"x": float(rng.uniform(0, W)), "y": float(rng.uniform(H * 0.3, H)),
           "v": float(rng.uniform(30, 90)), "ph": float(rng.uniform(0, 6.28)),
           "s": float(rng.uniform(0.6, 1.8))} for _ in range(70)]

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
dx, dy = (xx / W - .5) * 2, (yy / H - .5) * 2
VIG = np.clip(1.0 - 0.40 * np.clip(dx**2 + dy**2 - 0.35, 0, None), 0.4, 1.0)[..., None]

# ---------------- text ----------------
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f_sub = ImageFont.truetype(SANS_B, 42)
f_title = ImageFont.truetype(SANS_B, 150)
f_sub2 = ImageFont.truetype(SANS, 40)
SUBS = [(7, 91, "He has never owned a single face."),
        (99, 163, "Every mask \u2014 a life he wore."),
        (173, 231, "\u00c0y\u00edpad\u00e0... the many-faced god.")]

def tracked_w(d, text, font, tr):
    return sum(d.textlength(c, font=font) + tr for c in text) - tr

def draw_tracked(d, cx, y, text, font, tr, fill):
    x = cx - tracked_w(d, text, font, tr) / 2
    for c in text:
        d.text((x, y), c, font=font, fill=fill)
        x += d.textlength(c, font=font) + tr

# ---------------- shot timing (frames @24fps) ----------------
# s1: 0-100 (cartoon rig), s2: 92-172 (reach), s3: 164-240 (collection+title)
def shot_alpha(s, e, n, fade=8):
    if n < s or n >= e: return 0.0
    return float(min(1.0, (n - s) / fade, (e - n) / fade))

def smooth_noise(n, seed=0, scale=0.35):
    return (np.sin(n * 0.31 * scale + seed) + 0.5 * np.sin(n * 0.83 * scale + seed * 2.1)) / 1.5

# ---------------- render shots ----------------
def render_void(n, tint=(16, 10, 28)):
    t = n / FPS
    base = Image.new("RGB", (W, H), tint)
    top = Image.new("RGB", (W, H), (38, 20, 70))
    mask = Image.new("L", (1, H))
    mp = mask.load()
    for y in range(H):
        mp[0, y] = int(150 * (1 - y / H) ** 2)
    base.paste(top, (0, 0), mask.resize((W, H)))
    # smoke (drifting up, wrap)
    for sm in SMOKE:
        y = (sm["y"] - sm["v"] * t) % (H + 700) - 350
        x = sm["x"] + 30 * np.sin(t * 0.2 + sm["y"])
        spr = PUFFS[sm["p"]].resize((int(300 * sm["s"]),) * 2)
        a = spr.point(lambda v: int(v * sm["a"] / 255))
        base.paste(Image.new("RGB", spr.size, (88, 52, 140)), (int(x - spr.width / 2), int(y - spr.height / 2)), a)
    # god rays
    ov = ImageDraw.Draw(base, "RGBA")
    flick = 0.75 + 0.25 * np.sin(t * 2.3)
    for i, bx in enumerate((W * 0.55, W * 0.72)):
        w0, spread = 90 + i * 60, 260 + i * 120
        ov.polygon([(bx - w0, -50), (bx + w0, -50),
                    (bx + spread, H), (bx - spread, H)], fill=(150, 110, 255, int(13 * flick)))
    return base

def render_dust(base, n, gold=False):
    t = n / FPS
    for p in DUST:
        y = (p["y"] - p["v"] * t) % (H + 40) - 20
        x = p["x"] + 18 * np.sin(t * 0.7 + p["ph"])
        tw = 0.35 + 0.65 * abs(np.sin(t * 1.5 + p["ph"]))
        col = (255, 210, 150) if gold else (190, 160, 255)
        paste_sprite(base, SPARK, (x, y), scale=0.10 * p["s"], alpha=0.5 * tw)
        d = ImageDraw.Draw(base, "RGBA")
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=col + (int(120 * tw),))

def render_embers(base, n):
    t = n / FPS
    d = ImageDraw.Draw(base, "RGBA")
    for p in EMBERS:
        y = (p["y"] - p["v"] * t) % (H + 60) - 30
        x = p["x"] + 26 * np.sin(t * 1.1 + p["ph"])
        tw = 0.4 + 0.6 * abs(np.sin(t * 2.2 + p["ph"]))
        r = 2.5 * p["s"]
        d.ellipse([x - r * 2.2, y - r * 2.2, x + r * 2.2, y + r * 2.2],
                  fill=(178, 102, 255, int(60 * tw)))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(235, 210, 255, int(200 * tw)))

def render_s1(n):
    """Cartoon rigged idle."""
    t = n / FPS
    fr = render_void(n)
    # animation on 2s for the body (cartoon feel)
    nc = (n // 2) * 2
    tc = nc / FPS
    breathe = 1 + 0.012 * np.sin(tc * 2 * np.pi * 0.32)
    squash = 1 - 0.010 * np.sin(tc * 2 * np.pi * 0.32)
    bob = 7 * np.sin(tc * 2 * np.pi * 0.32 - 0.6)
    sway = 0.55 * np.sin(tc * 2 * np.pi * 0.21)
    settle = min(1.0, n / 24)
    rise = (1 - settle) * 60
    cw, ch = int(CHAR_W * squash), int(CHAR_H * breathe)
    char = CHAR_BASE.resize((cw, ch), Image.BICUBIC).rotate(sway, expand=False,
                                                            resample=Image.BICUBIC, center=(cw / 2, ch * 0.62))
    # placement: char layer coords = orig*CS scaled by body scale, centered
    ox = (W - cw) / 2 + 40 + 10 * smooth_noise(n, 3)
    oy = (H - ch) / 2 + 30 + bob - rise
    fr.paste(char, (int(ox), int(oy)), char)

    def to_frame(x, y):
        return (ox + x * CS * squash, oy + y * CS * breathe)

    # eye glow pulse + blink flares
    pulse = 0.30 + 0.25 * np.sin(t * 2 * np.pi * 1.1)
    flare = max(0, 1 - abs((t % 2.4) - 0.4) / 0.25) ** 2
    for ex, ey in (EYE_L, EYE_R):
        fx, fy = to_frame(ex, ey)
        add_glow(fr, (fx, fy), 46 * CS / 1.4, (190, 130, 255), int(110 * pulse + 120 * flare))
    # grin shimmer sweep every ~3s
    sw = (t % 3.0) / 3.0
    if 0.15 < sw < 0.55:
        gx, gy = to_frame(GRIN[0], GRIN[1])
        sx = gx - 160 + (sw - 0.15) / 0.40 * 320
        band = Image.new("L", (W, H), 0)
        db = ImageDraw.Draw(band)
        db.polygon([(sx - 46, gy - 120), (sx + 10, gy - 120),
                    (sx - 30, gy + 120), (sx - 86, gy + 120)], fill=90)
        band = band.filter(ImageFilter.GaussianBlur(18))
        fr.paste(Image.new("RGB", (W, H), (220, 190, 255)), (0, 0), band)
    # swinging bells (separate rigged parts)
    for i, b in enumerate(BELLS):
        ang = b["amp"] * np.sin(t * 2 * np.pi * b["freq"] * 0.5 + b["phase"])
        px, py = to_frame(*b["pivot"])
        part = BELL_PARTS[i].copy() if False else BELL_BASE[i]
        # rotate about pivot: pivot in part coords
        x0, y0, x1, y1 = b["box"]
        pvx, pvy = (b["pivot"][0] - x0) * CS * squash, (b["pivot"][1] - y0) * CS * breathe
        pr = part.rotate(-ang, expand=True, resample=Image.BICUBIC, center=(pvx, pvy))
        # rotated pivot location inside expanded image
        ang_r = np.radians(-ang)
        cx0, cy0 = part.width / 2, part.height / 2
        dx0, dy0 = pvx - cx0, pvy - cy0
        rdx = dx0 * np.cos(ang_r) - dy0 * np.sin(ang_r)
        rdy = dx0 * np.sin(ang_r) + dy0 * np.cos(ang_r)
        ncx, ncy = pr.width / 2, pr.height / 2
        fr.paste(pr, (int(px - (ncx + rdx)), int(py - (ncy + rdy))), pr)
        # bell glint sparkles
        tw = max(0, np.sin(t * 3 + b["phase"] * 2)) ** 6
        if tw > 0.02:
            paste_sprite(fr, SPARK, (px + 12, py + 70 * CS / 1.4), scale=0.5, alpha=float(tw))
    render_dust(fr, n)
    return fr

IMPACT = 128  # frame of reach impact (~5.3s)

def render_s2(n):
    t = n / FPS
    p = (n - 92) / (172 - 92)
    z = 1.04 + 0.20 * p
    im = REACH_C.resize((int(W * z), int(H * z)), Image.BICUBIC)
    cx = im.width / 2 + 30 * p
    cy = im.height / 2 + 10 * p
    fr = im.crop((int(cx - W / 2), int(cy - H / 2), int(cx + W / 2), int(cy + H / 2))).copy()
    # impact shake + flash
    if n >= IMPACT:
        dt = (n - IMPACT) / FPS
        mag = 14 * np.exp(-dt * 5)
        fr = fr.transform((W, H), Image.AFFINE,
                          (1, 0, mag * smooth_noise(n, 9), 0, 1, mag * smooth_noise(n, 21)))
        if dt < 0.12:
            fr = Image.blend(fr, Image.new("RGB", (W, H), (200, 160, 255)), 0.35 * (1 - dt / 0.12))
    # hand glow swell
    gl = 60 + 120 * p + (150 * np.exp(-max(0, (n - IMPACT)) / FPS * 4) if n >= IMPACT else 0)
    add_glow(fr, (W * 0.42, H * 0.52), 260, (170, 110, 255), int(min(200, gl)))
    # speed lines near impact
    if IMPACT - 10 <= n <= IMPACT + 8:
        d = ImageDraw.Draw(fr, "RGBA")
        k = 1 - abs(n - IMPACT) / 12
        for i in range(26):
            a = (i / 26) * 6.283 + 0.2
            r0, r1 = 420, 420 + 260 * k
            x0, y0 = W * 0.42 + r0 * np.cos(a), H * 0.52 + r0 * np.sin(a) * 0.6
            x1, y1 = W * 0.42 + r1 * np.cos(a), H * 0.52 + r1 * np.sin(a) * 0.6
            d.line([x0, y0, x1, y1], fill=(220, 190, 255, int(150 * k)), width=4)
    render_embers(fr, n)
    return fr

def render_s3(n):
    t = n / FPS
    p = (n - 164) / (240 - 164)
    z = 1.0 + 0.08 * p
    im = COLLECT_C.resize((int(W * z), int(H * z)), Image.BICUBIC)
    cx, cy = im.width / 2, im.height / 2 - 30 * p
    fr = im.crop((int(cx - W / 2), int(cy - H / 2), int(cx + W / 2), int(cy + H / 2))).copy()
    fr = Image.blend(fr, Image.new("RGB", (W, H)), 0.42 * min(1, (n - 164) / 12))
    # shimmer sweep across masks
    sw = (t % 2.6) / 2.6
    sx = -200 + sw * (W + 400)
    band = Image.new("L", (W, H), 0)
    db = ImageDraw.Draw(band)
    db.polygon([(sx - 90, 0), (sx + 30, 0), (sx - 60, H), (sx - 180, H)], fill=54)
    fr.paste(Image.new("RGB", (W, H), (200, 160, 255)), (0, 0), band.filter(ImageFilter.GaussianBlur(24)))
    render_embers(fr, n)
    return fr

# ---------------- main ----------------
BAR = 80
stills = {30: "v2_rig.jpg", 126: "v2_impact.jpg", 210: "v2_title.jpg"}

def compose(n):
    a1, a2, a3 = shot_alpha(0, 100, n), shot_alpha(92, 172, n, 10), shot_alpha(164, 240, n, 10)
    acc = np.zeros((H, W, 3), np.float32)
    tot = 0.0
    for a, fn in ((a1, render_s1), (a2, render_s2), (a3, render_s3)):
        if a > 0:
            acc += np.asarray(fn(n), np.float32) * a
            tot += a
    img = (acc / max(tot, 1e-6)).clip(0, 255).astype(np.uint8)
    a = img.astype(np.float32) * VIG
    g = np.random.default_rng(n).normal(0, 4.5, (H, W, 1)).astype(np.float32)
    fr = Image.fromarray(np.clip(a + g, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(fr, "RGBA")
    d.rectangle([0, 0, W, BAR], fill=(0, 0, 0, 255))
    d.rectangle([0, H - BAR, W, H], fill=(0, 0, 0, 255))
    # subtitles (YouTube style)
    for s, e, txt in SUBS:
        if s <= n < e:
            fo = min(1.0, (n - s) / 6, (e - n) / 6)
            if fo > 0:
                tw = d.textlength(txt, font=f_sub)
                d.text(((W - tw) / 2, H - BAR - 96), txt, font=f_sub,
                       fill=(255, 255, 255, int(255 * fo)),
                       stroke_width=2, stroke_fill=(0, 0, 0, int(255 * fo)))
    # title card on shot 3
    if n >= 178:
        fo = min(1.0, (n - 178) / 12)
        ty = 250
        draw_tracked(d, W / 2 + 3, ty + 3, "\u00c0Y\u00cdPAD\u00c0", f_title, 24, (0, 0, 0, int(230 * fo)))
        draw_tracked(d, W / 2, ty, "\u00c0Y\u00cdPAD\u00c0", f_title, 24, (190, 150, 255, int(255 * fo)))
        draw_tracked(d, W / 2, ty + 190, "THE MANY-FACED GOD", f_sub2, 16, (235, 225, 245, int(240 * fo)))
        d.line([W / 2 - 170, ty + 268, W / 2 + 170, ty + 268], fill=(176, 132, 255, int(160 * fo)), width=2)
    if n < 10 or n >= NFRAMES - 10:
        k = min(n / 10, (NFRAMES - 1 - n) / 10)
        fr = Image.blend(Image.new("RGB", (W, H)), fr, float(np.clip(k, 0, 1)))
    return fr

if PREVIEW:
    for n, name in stills.items():
        compose(n).save(os.path.join(OUTDIR, name), quality=88)
        print("saved", name)
    sys.exit(0)

import imageio_ffmpeg
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
tmp_vid = os.path.join(OUTDIR, "_v2_video_only.mp4")
proc = subprocess.Popen([ffmpeg, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                         "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                         "-crf", "19", "-preset", "medium", tmp_vid],
                        stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
for n in range(NFRAMES):
    proc.stdin.write(compose(n).tobytes())
    if n in stills:
        pass
    if n % 48 == 0:
        print(f"frame {n}/{NFRAMES}", flush=True)
proc.stdin.close(); proc.wait()
for n, name in stills.items():
    compose(n).save(os.path.join(OUTDIR, name), quality=88)

# ---- 10s sound: drone + bell strikes + whooshes + impact ----
SR = 44100
t = np.arange(int(SR * DUR)) / SR
def bell_at(t0, base=660, amp=0.2, decay=2.8):
    tb = t - t0
    parts = [(1.0, 0, 1.0), (1.5, 1.1, 0.6), (2.0, 2.0, 0.45), (0.5, 0.5, 0.5)]
    s = sum(np.sin(2 * np.pi * base * m * np.clip(tb, 0, None) + p) * a
            for m, p, a in parts) * np.exp(-np.clip(tb, 0, None) * decay)
    return s * amp * (tb > 0)
def whoosh(t0, dur=0.5, amp=0.25):
    x = (t - t0) / dur
    m = ((0 < x) & (x < 1)).astype(float)
    nse = np.random.default_rng(3).standard_normal(t.shape)
    # crude sweep: amplitude envelope, brightness via cumulative trick
    env = np.sin(np.clip(x, 0, 1) * np.pi) ** 2 * m
    return nse * env * amp * 0.4
swell = (t / DUR) ** 1.4
drone = (np.sin(2 * np.pi * 55 * t) * 0.22 + np.sin(2 * np.pi * 110 * t) * 0.10
         + np.sin(2 * np.pi * 82.5 * t + 1.3) * 0.08) * swell
ti = IMPACT / FPS
boom = np.sin(2 * np.pi * 50 * np.clip(t - ti, 0, None)) * np.exp(-np.clip(t - ti, 0, None) * 5) * 0.6 * (t > ti)
mix = (drone + bell_at(0.8, 660, .20) + bell_at(2.6, 550, .16) + bell_at(7.4, 440, .22, 2.2)
       + whoosh(92 / FPS) + whoosh(164 / FPS) + boom)
mix *= np.clip((DUR - t) / 0.5, 0, 1)
mix = (mix / max(1e-6, np.abs(mix).max()) * 0.89 * 32767).astype(np.int16)
wav_p = os.path.join(OUTDIR, "_v2_audio.wav")
wv = wave.open(wav_p, "wb"); wv.setnchannels(1); wv.setsampwidth(2); wv.setframerate(SR)
wv.writeframes(mix.tobytes()); wv.close()
final = os.path.join(OUTDIR, "ayipada-2d-pilot.mp4")
subprocess.run([ffmpeg, "-y", "-i", tmp_vid, "-i", wav_p, "-c:v", "copy",
                "-c:a", "aac", "-b:a", "160k", "-shortest", final],
               check=True, capture_output=True)
os.remove(tmp_vid); os.remove(wav_p)
print("OK ->", final, os.path.getsize(final), "bytes")
