# SWAY - Agentic Video Maker

A programmable video generation platform controlled by AI agents.

## Quick Start

### 1. Deploy on Render

1. Go to [render.com](https://render.com)
2. Connect your GitHub repo
3. Render auto-detects `.render.yaml`
4. Click "Apply"

### 2. Use the API

```bash
# Check status
curl https://your-sway.onrender.com/status

# Create a scene
curl -X POST https://your-sway.onrender.com/api/scenes \
  -H "Content-Type: application/json" \
  -d '{"name": "Intro", "component": "Intro", "props": {}}'

# Render video
curl -X POST https://your-sway.onrender.com/api/render \
  -H "Content-Type: application/json" \
  -d '{"composition": "Main", "output": "out/intro.mp4"}'
```

### 3. AI Agent Integration

Use the `agent.js` client:

```bash
export SWAY_URL=https://your-sway.onrender.com
node agent.js status
node agent.js create Scene1 /assets/image.png
node agent.js render Main
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/status` | GET | System status |
| `/api/scenes` | GET | List scenes |
| `/api/scenes` | POST | Create scene |
| `/api/scenes/:name` | DELETE | Delete scene |
| `/api/render` | POST | Render video |
| `/api/assets` | GET | List assets |
| `/api/assets` | POST | Upload asset |

## Project Structure

```
sway/
├── src/
│   ├── server.js        # Express API server
│   ├── index.ts         # Remotion entry
│   ├── Root.tsx         # Composition root
│   └── scenes/          # Scene components
├── public/              # Static files
├── assets/             # Images & media
├── out/                # Rendered videos
└── agent.js            # AI client
```

## Examples

### Create Animation Sequence

```javascript
// 1. Upload images
await uploadAsset("scene1.png");
await uploadAsset("scene2.png");

// 2. Create scenes
await createScene("Scene1", "/assets/scene1.png");
await createScene("Scene2", "/assets/scene2.png");

// 3. Render
await renderVideo("FullSequence");
```

## License

MIT
