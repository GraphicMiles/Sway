#!/usr/bin/env python3
"""Build Ayipada_Wan2_ComfyUI_Kaggle.ipynb (valid nbformat JSON)."""
import json, os

OUT = "/home/user/Sway/kaggle/Ayipada_Wan2_ComfyUI_Kaggle.ipynb"

def md(src): return {"cell_type": "markdown", "metadata": {},
                    "source": [l + "\n" for l in src.strip("\n").split("\n")]}
def code(src): return {"cell_type": "code", "metadata": {}, "execution_count": None,
                      "outputs": [], "source": [l + "\n" for l in src.strip("\n").split("\n")]}

cells = []

cells.append(md("""
# 🟣 ÀYÍPADÀ — Real AI Motion on Free Kaggle GPUs
**Wan 2.1 I2V 14B (GGUF Q4) + ComfyUI** — turns your Àyípadà stills into true AI-animated video clips.

### Setup (2 minutes, do this first)
1. **Kaggle.com → Create → New Notebook → Upload** this `.ipynb` file
2. Right sidebar → **Accelerator: GPU T4 x2** (or T4)
3. Right sidebar → **Internet: ON** (Kaggle may ask for phone verification — models download from Hugging Face)
4. **Run All** (Cell → Run All). Total first run ≈ 25–45 min (mostly model downloads, one time only)

### Free quota reminder
- Kaggle: **~30 GPU-hours/week**, sessions up to 9–12h. Each 5-sec clip ≈ 8–20 min on T4
- 💡 After first run: **Save → Save Version** or copy `/kaggle/working/ComfyUI/models` to a private Dataset so next session skips downloads
"""))

cells.append(code("""
# ===== Cell 1: Environment check =====
import shutil, torch, urllib.request
print("PyTorch:", torch.__version__, "| CUDA available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))
    print("VRAM: %.1f GB" % (torch.cuda.get_device_properties(0).total_memory / 1e9))
print("Free disk in /kaggle/working: %.1f GB" % (shutil.disk_usage('/kaggle/working').free / 1e9))
try:
    urllib.request.urlopen("https://huggingface.co", timeout=10)
    print("Internet: OK ✅ (model downloads will work)")
except Exception as e:
    print("Internet: FAILED ❌ — turn Internet ON in the right sidebar, then re-run. Error:", e)
"""))

cells.append(code("""
# ===== Cell 2: Install ComfyUI + custom nodes (uses Kaggle's built-in torch) =====
%cd /kaggle/working
!git clone -q https://github.com/comfyanonymous/ComfyUI 2>&1 | tail -1
%cd /kaggle/working/ComfyUI
!pip install -q gguf imageio-ffmpeg "huggingface_hub[cli]" 2>&1 | tail -1
!sed -i '/^torch$/d;/^torch==/d;/^torchaudio/d;/^torchvision/d' requirements.txt
!pip install -q -r requirements.txt 2>&1 | tail -1
!git clone -q https://github.com/city96/ComfyUI-GGUF custom_nodes/ComfyUI-GGUF 2>&1 | tail -1
!git clone -q https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite custom_nodes/ComfyUI-VideoHelperSuite 2>&1 | tail -1
!pip install -q -r custom_nodes/ComfyUI-VideoHelperSuite/requirements.txt 2>&1 | tail -1
print("Install done ✅")
"""))

cells.append(code("""
# ===== Cell 3: Download models (auto-resolves exact filenames, with fallbacks) =====
# Primary: Wan 2.1 I2V 14B 720P GGUF Q4 (~9GB, single file, battle-tested on T4 16GB)
from huggingface_hub import hf_hub_download, list_repo_files
COMFY = "/kaggle/working/ComfyUI"

def pick(repo, *wants):
    files = list_repo_files(repo)
    cands = [f for f in files if all(w in f.lower() for w in wants)]
    return sorted(cands, key=len)[0] if cands else None

# --- 3a. GGUF main model ---
GGUF = (None, None)
for repo in ["Kijai/WanVideo_comfy_GGUF", "QuantStack/Wan2.1-I2V-14B-720P-GGUF"]:
    try:
        f = pick(repo, "i2v", "14b", "720p", "q4_k_m") or pick(repo, "i2v", "14b", "q4")
        if f:
            GGUF = (repo, f); break
    except Exception as e:
        print(repo, "->", type(e).__name__, e)
assert GGUF[1], "No GGUF found — check repos above. Aborting."
print("GGUF:", GGUF[0], "/", GGUF[1])
hf_hub_download(GGUF[0], GGUF[1], local_dir=f"{COMFY}/models/diffusion_models", local_dir_use_symlinks=False)

# --- 3b. Text encoder + VAE + CLIP vision (from repackaged bundle) ---
R = "Comfy-Org/Wan_2.1_ComfyUI_repackaged"
TE  = pick(R, "umt5", "fp8") or pick(R, "umt5")
VAE = pick(R, "wan_2.1_vae") or pick(R, "wan", "vae")
CV  = pick(R, "clip_vision") or pick(R, "clip", "vision")
print("TE:", TE, "\\nVAE:", VAE, "\\nCLIP-V:", CV)
assert TE and VAE and CV, "Missing helper model — inspect repo file list. Aborting."
hf_hub_download(R, TE,  local_dir=f"{COMFY}/models/clip",        local_dir_use_symlinks=False)
hf_hub_download(R, VAE, local_dir=f"{COMFY}/models/vae",         local_dir_use_symlinks=False)
hf_hub_download(R, CV,  local_dir=f"{COMFY}/models/clip_vision", local_dir_use_symlinks=False)

import os
GGUF_FILE, TE_FILE, VAE_FILE, CV_FILE = (os.path.basename(p) for p in (GGUF[1], TE, VAE, CV))
print("\\n✅ Models ready:", GGUF_FILE, "|", TE_FILE, "|", VAE_FILE, "|", CV_FILE)
"""))

cells.append(code("""
# ===== Cell 4: Download Àyípadà stills (from your own GitHub repo) =====
import os, urllib.request
RAW = "https://raw.githubusercontent.com/GraphicMiles/Sway/main/public/assets"
DST = "/kaggle/working/ComfyUI/input/ayipada"
os.makedirs(DST, exist_ok=True)
STILLS = ["pilot_emerge.png", "pilot_reach.png", "pilot_collection.png", "pilot_ancestors.png", "pilot_mask.jpg"]
for s in STILLS:
    urllib.request.urlretrieve(f"{RAW}/{s}", f"{DST}/{s}")
    print("got", s, os.path.getsize(f"{DST}/{s}") // 1024, "KB")
"""))

cells.append(code("""
# ===== Cell 5: Start ComfyUI + validate required nodes exist =====
import json, subprocess, time, urllib.request
LOG = open("/kaggle/working/comfy.log", "w")
subprocess.Popen(["python", "main.py", "--listen", "127.0.0.1", "--port", "8188",
                  "--preview-method", "none", "--lowvram"],
                 cwd="/kaggle/working/ComfyUI", stdout=LOG, stderr=subprocess.STDOUT)
for i in range(60):
    try:
        urllib.request.urlopen("http://127.0.0.1:8188/system_stats", timeout=5)
        print("ComfyUI is up ✅"); break
    except Exception:
        time.sleep(10)
else:
    raise RuntimeError("ComfyUI did not start — see /kaggle/working/comfy.log")
info = json.load(urllib.request.urlopen("http://127.0.0.1:8188/object_info", timeout=60))
need = ["UnetLoaderGGUF", "CLIPLoader", "CLIPTextEncode", "CLIPVisionLoader",
        "CLIPVisionEncode", "WanImageToVideo", "KSampler", "VAEDecode",
        "VHS_VideoCombine", "LoadImage"]
missing = [n for n in need if n not in info]
print("Nodes OK:", len(need) - len(missing), "/", len(need))
assert not missing, f"Missing nodes {missing} — check comfy.log, custom nodes may have failed."
"""))

cells.append(code("""
# ===== Cell 6: Queue helper + Wan I2V workflow builder =====
import json, random, time, urllib.request, os
SERVER = "http://127.0.0.1:8188"
CLIPS = "/kaggle/working/clips"; os.makedirs(CLIPS, exist_ok=True)

# --- quality knobs (lower for quick draft tests) ---
WIDTH, HEIGHT = 832, 480      # 16:9, multiples of 16
FRAMES = 81                   # 4k+1 only (e.g. 49, 81, 121). 81 @16fps ≈ 5 sec
STEPS, CFG = 24, 6.0
FPS_OUT = 16
NEG = ("morphing face, extra limbs, distorted hands, flicker, watermark, text, "
       "cartoon jump, static frame, no motion")

def build_wan_i2v(image_file, prompt, seed=None):
    seed = seed or random.randint(0, 2**31)
    return {
        "1":  {"class_type": "UnetLoaderGGUF", "inputs": {"unet_name": GGUF_FILE}},
        "2":  {"class_type": "CLIPLoader", "inputs": {"clip_name": TE_FILE, "type": "wan"}},
        "3":  {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["2", 0]}},
        "4":  {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["2", 0]}},
        "5":  {"class_type": "CLIPVisionLoader", "inputs": {"clip_name": CV_FILE}},
        "6":  {"class_type": "LoadImage", "inputs": {"image": f"ayipada/{image_file}"}},
        "7":  {"class_type": "CLIPVisionEncode", "inputs": {"clip_vision": ["5", 0], "image": ["6", 0]}},
        "8":  {"class_type": "VAELoader", "inputs": {"vae_name": VAE_FILE}},
        "9":  {"class_type": "WanImageToVideo", "inputs": {
            "positive": ["3", 0], "negative": ["4", 0], "vae": ["8", 0],
            "width": WIDTH, "height": HEIGHT, "length": FRAMES, "batch_size": 1,
            "clip_vision_output": ["7", 0], "start_image": ["6", 0]}},
        "10": {"class_type": "KSampler", "inputs": {
            "model": ["1", 0], "positive": ["9", 0], "negative": ["9", 1],
            "latent_image": ["9", 2], "seed": seed, "steps": STEPS, "cfg": CFG,
            "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}},
        "11": {"class_type": "VAEDecode", "inputs": {"samples": ["10", 0], "vae": ["8", 0]}},
        "12": {"class_type": "VHS_VideoCombine", "inputs": {
            "images": ["11", 0], "frame_rate": FPS_OUT, "loop_count": 0,
            "filename_prefix": "ayipada", "format": "video/h264-mp4",
            "pix_fmt": "yuv420p", "crf": 19, "save_metadata": False,
            "pingpong": False, "save_output": True}},
    }

def queue_and_wait(workflow, out_name, poll=15):
    req = urllib.request.Request(SERVER + "/prompt",
        data=json.dumps({"prompt": workflow}).encode(),
        headers={"Content-Type": "application/json"})
    pid = json.load(urllib.request.urlopen(req))["prompt_id"]
    print(f"queued {out_name} (id {pid[:8]}…) — rendering, this takes a while ⏳")
    while True:
        time.sleep(poll)
        h = json.load(urllib.request.urlopen(SERVER + f"/history/{pid}"))
        if pid in h:
            node12 = h[pid]["outputs"]["12"]["gifs"][0]
            q = f"filename={node12['filename']}&subfolder={node12['subfolder']}&type={node12['type']}"
            data = urllib.request.urlopen(SERVER + "/view?" + q).read()
            path = f"{CLIPS}/{out_name}"
            open(path, "wb").write(data)
            print(f"✅ saved {path} ({len(data)//1024} KB)")
            return path

print("helper ready ✅")
"""))

cells.append(md("""
### 🎬 Shots — run the next 3 cells one by one (each renders one clip)
Prompts are tuned for Àyípadà. Tweak wording, re-run a cell to regenerate that shot.
"""))

cells.append(code("""
# ===== Shot 1: EMERGENCE (pilot_emerge.png) =====
from IPython.display import Video
p1 = queue_and_wait(build_wan_i2v(
    "pilot_emerge.png",
    "dark wooden spirit god with glowing purple mask crouching in darkness, "
    "ember eyes flicker alive, brass bells sway gently, smoke drifts past, "
    "slow supernatural breathing motion, cinematic push in, dark fantasy"),
    "shot1_emerge.mp4")
Video(p1, width=640)
"""))

cells.append(code("""
# ===== Shot 2: THE REACH (pilot_reach.png) =====
from IPython.display import Video
p2 = queue_and_wait(build_wan_i2v(
    "pilot_reach.png",
    "purple masked tribal spirit lunges its carved wooden hand toward the camera, "
    "fingers stretch forward reaching for the viewer, mask grin widens, "
    "bells trembling, dramatic forward motion, dark fantasy horror"),
    "shot2_reach.mp4")
Video(p2, width=640)
"""))

cells.append(code("""
# ===== Shot 3: THE COLLECTION (pilot_collection.png) =====
from IPython.display import Video
p3 = queue_and_wait(build_wan_i2v(
    "pilot_collection.png",
    "towering god covered head to toe in living wooden masks, the masks blink "
    "and sway gently, purple mist rises around him, spotlight flickers, "
    "slow majestic rising motion, dark fantasy cinematic"),
    "shot3_collection.mp4")
Video(p3, width=640)
"""))

cells.append(code("""
# ===== Final: stitch the 3 clips into one pilot assembly =====
import imageio_ffmpeg
from IPython.display import Video
ff = imageio_ffmpeg.get_ffmpeg_exe()
import subprocess
open("/kaggle/working/list.txt", "w").write(
    "file '/kaggle/working/clips/shot1_emerge.mp4'\\n"
    "file '/kaggle/working/clips/shot2_reach.mp4'\\n"
    "file '/kaggle/working/clips/shot3_collection.mp4'\\n")
out = "/kaggle/working/AYIPADA_AI_pilot.mp4"
subprocess.run([ff, "-y", "-f", "concat", "-safe", "0", "-i", "/kaggle/working/list.txt",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", "-movflags", "+faststart",
                "-an", out], check=True, capture_output=True)
print("✅", out)
Video(out, width=640)
"""))

cells.append(md("""
### 💾 Reuse next session (skip re-downloads)
Kaggle wipes `/kaggle/working` between sessions. To keep the ~15GB of models:
1. In this notebook: **Save Version → Save**, then download `ComfyUI/models` folders, **or**
2. Better: **Kaggle → Datasets → New Dataset** (upload the `models` folder once), then next session **Add Input → Your Dataset** and symlink it:
```python
import os
os.system("rm -rf /kaggle/working/ComfyUI/models && ln -s /kaggle/input/YOUR-DATASET/models /kaggle/working/ComfyUI/models")
```
(run after Cell 2, skip Cell 3). Your clips in `/kaggle/working/clips` — download them from the Output panel before closing.
### ⬆️ Quality upgrades when free quota allows
- **Wan 2.2** (sharper motion): swap the GGUF cell to `Wan2.2-I2V-A14B` Q4 (needs HIGH+LOW files + chained sampler — ask and I'll add the workflow)
- More steps (30–40) / larger size (960×544) / longer clips (121 frames ≈ 7.5s)
- Stitch + subtitles + score with `render-ayipada-v2.py` from the Sway repo
"""))

nb = {"nbformat": 4, "nbformat_minor": 5, "metadata": {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
    "cells": cells}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(nb, open(OUT, "w"), indent=1)
print("wrote", OUT, "with", len(cells), "cells")
