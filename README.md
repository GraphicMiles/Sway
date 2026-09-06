# ÀYÍPADÀ - THE MANY-FACED GOD
## 2D Animation Pilot Project

### SETUP

1. **Install dependencies:**
```bash
npm install
```

2. **Add your character images:**
   - Copy your images to `src/assets/`
   - Name them: `01_standing_front.png`, `02_emerging.png`, etc.

3. **Run preview:**
```bash
npm start
```

4. **Render video:**
```bash
npm run build
```

### DEPLOY TO RENDER (FREE)

1. Push to GitHub
2. Go to [render.com](https://render.com)
3. Click "New" → "Web Service"
4. Connect your GitHub repo
5. Set build command: `npm install`
6. Set start command: `npm start`
7. Deploy!

### SCENES

| Scene | Duration | Description |
|-------|----------|-------------|
| Opening | 5s | Character emerging from darkness |
| Collection | 6s | Full body with masks |
| Lurking | 4s | Shadow at edge |
| Raising Hand | 5s | Arm raised |
| Floating Masks | 6s | Surrounded by masks |
| Reaching | 5s | Reaching forward |
| Leaning Back | 4s | Defensive posture |
| Looking Up | 5s | Head tilted up |
| Masks Turning | 6s | All faces turning |
| Staring | 5s | Direct stare |

**Total: ~51 seconds**

### ADD VOICEOVER

Add audio file: `src/assets/narration.mp3`

### CUSTOMIZE

Edit `src/Root.tsx` to change scene order, timing, and transitions.
Edit scene files in `src/scenes/` to modify individual scenes.
