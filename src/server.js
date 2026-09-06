/**
 * SWAY - Agentic Video Maker
 * 
 * Express server that provides API for AI agents to generate videos
 * using Remotion framework.
 */

const express = require("express");
const cors = require("cors");
const fs = require("fs");
const path = require("path");
const { execSync, spawn } = require("child_process");

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static("public"));

const PORT = process.env.PORT || 3000;
const OUT_DIR = path.join(__dirname, "..", "out");

// Ensure output directory exists
if (!fs.existsSync(OUT_DIR)) {
  fs.mkdirSync(OUT_DIR, { recursive: true });
}

// ============ HEALTH & STATUS ============

app.get("/health", (req, res) => {
  res.json({
    status: "ok",
    service: "sway",
    timestamp: new Date().toISOString(),
    version: "0.1.0"
  });
});

app.get("/status", (req, res) => {
  const scenes = fs.readdirSync(path.join(__dirname, "scenes")).filter(f => f.endsWith(".tsx"));
  const compositions = getCompositions();
  
  res.json({
    scenes: scenes.length,
    compositions,
    assets: fs.existsSync("assets") ? fs.readdirSync("assets").length : 0,
    outputDir: OUT_DIR
  });
});

// ============ SCENES API ============

app.get("/api/scenes", (req, res) => {
  try {
    const scenesDir = path.join(__dirname, "scenes");
    const files = fs.readdirSync(scenesDir).filter(f => f.endsWith(".tsx"));
    
    const scenes = files.map(file => ({
      name: file.replace(".tsx", ""),
      component: file.replace(".tsx", ""),
      path: `/src/scenes/${file}`
    }));
    
    res.json({ success: true, scenes });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.post("/api/scenes", async (req, res) => {
  const { name, component, props = {} } = req.body;
  
  if (!name || !component) {
    return res.status(400).json({ 
      success: false, 
      error: "Missing required fields: name, component" 
    });
  }
  
  try {
    const scenesDir = path.join(__dirname, "scenes");
    const fileName = `${name}.tsx`;
    const filePath = path.join(scenesDir, fileName);
    
    const template = generateSceneTemplate(component, props);
    fs.writeFileSync(filePath, template);
    
    // Update Root.tsx
    updateRootWithScene(name, component);
    
    res.json({ 
      success: true, 
      message: `Scene ${name} created`,
      path: filePath,
      endpoint: `/api/render`
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.delete("/api/scenes/:name", (req, res) => {
  const { name } = req.params;
  const filePath = path.join(__dirname, "scenes", `${name}.tsx`);
  
  if (fs.existsSync(filePath)) {
    fs.unlinkSync(filePath);
    res.json({ success: true, message: `Scene ${name} deleted` });
  } else {
    res.status(404).json({ success: false, error: "Scene not found" });
  }
});

// ============ COMPOSITIONS API ============

app.get("/api/compositions", (req, res) => {
  const compositions = getCompositions();
  res.json({ success: true, compositions });
});

function getCompositions() {
  const scenesDir = path.join(__dirname, "scenes");
  if (!fs.existsSync(scenesDir)) return [];
  
  return fs.readdirSync(scenesDir)
    .filter(f => f.endsWith(".tsx"))
    .map(f => f.replace(".tsx", ""));
}

// ============ RENDER API ============

app.post("/api/render", async (req, res) => {
  const { 
    composition = "Main", 
    duration,
    fps = 30,
    width = 1920,
    height = 1080,
    output,
    props = {}
  } = req.body;
  
  const outputFile = output || `out/${composition.toLowerCase()}.mp4`;
  const outputPath = path.join(__dirname, "..", outputFile);
  
  try {
    console.log(`🎬 Rendering: ${composition}`);
    console.log(`📁 Output: ${outputPath}`);
    
    // Ensure output directory exists
    const outDir = path.dirname(outputPath);
    if (!fs.existsSync(outDir)) {
      fs.mkdirSync(outDir, { recursive: true });
    }
    
    // Render using Remotion CLI
    const renderCmd = `npx remotion render ${composition} ${outputFile} --props '${JSON.stringify(props)}'`;
    
    execSync(renderCmd, {
      cwd: path.join(__dirname, ".."),
      stdio: "inherit"
    });
    
    const downloadUrl = `${getBaseUrl()}/${outputFile}`;
    
    res.json({
      success: true,
      message: "Render complete",
      composition,
      output: outputFile,
      downloadUrl,
      message: `Video ready at ${downloadUrl}`
    });
    
  } catch (error) {
    console.error("Render error:", error.message);
    res.status(500).json({ 
      success: false, 
      error: error.message,
      hint: "Make sure the composition exists and assets are in place"
    });
  }
});

app.post("/api/render/stills", async (req, res) => {
  const { composition, props = {} } = req.body;
  
  if (!composition) {
    return res.status(400).json({ success: false, error: "composition required" });
  }
  
  try {
    const outputDir = path.join(__dirname, "..", "out", "stills");
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    const cmd = `npx remotion still ${composition} ${outputDir}/${composition}.png --props '${JSON.stringify(props)}'`;
    
    execSync(cmd, {
      cwd: path.join(__dirname, ".."),
      stdio: "inherit"
    });
    
    res.json({
      success: true,
      output: `${outputDir}/${composition}.png`
    });
    
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// ============ ASSETS API ============

app.get("/api/assets", (req, res) => {
  const assetsDir = path.join(__dirname, "assets");
  
  if (!fs.existsSync(assetsDir)) {
    return res.json({ success: true, assets: [] });
  }
  
  const assets = fs.readdirSync(assetsDir).map(file => ({
    name: file,
    url: `/assets/${file}`,
    type: getFileType(file)
  }));
  
  res.json({ success: true, assets });
});

app.post("/api/assets", (req, res) => {
  // Handle file upload via base64
  const { name, data, type = "image/png" } = req.body;
  
  if (!name || !data) {
    return res.status(400).json({ success: false, error: "name and data required" });
  }
  
  try {
    const assetsDir = path.join(__dirname, "assets");
    if (!fs.existsSync(assetsDir)) {
      fs.mkdirSync(assetsDir, { recursive: true });
    }
    
    // Remove data URL prefix if present
    const base64Data = data.replace(/^data:[^;]+;base64,/, "");
    const buffer = Buffer.from(base64Data, "base64");
    
    const filePath = path.join(assetsDir, name);
    fs.writeFileSync(filePath, buffer);
    
    res.json({
      success: true,
      name,
      url: `/assets/${name}`,
      path: filePath
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// ============ DOWNLOAD ============

app.get("/out/*", (req, res) => {
  const file = req.params[0];
  const filePath = path.join(__dirname, "..", "out", file);
  
  if (fs.existsSync(filePath)) {
    res.download(filePath);
  } else {
    res.status(404).json({ error: "File not found" });
  }
});

// ============ HELPERS ============

function generateSceneTemplate(component, props) {
  return `import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";

export const ${component}: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entrance = spring({
    frame,
    fps,
    config: { damping: 100, mass: 0.5 }
  });

  const breathe = Math.sin(frame * 0.05) * 0.02 + 1;
  const sway = Math.sin(frame * 0.03) * 2;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#000000",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <div
        style={{
          transform: \`scale(\${breathe}) rotate(\${sway}deg)\`,
          opacity: entrance,
        }}
      >
        {/* Add your content here */}
        <img
          src={\`/assets/\${props.image || 'placeholder.png'}\`}
          style={{ maxWidth: "100%", maxHeight: "100%" }}
          alt="scene"
        />
      </div>
    </AbsoluteFill>
  );
};
`;
}

function updateRootWithScene(name, component) {
  const rootPath = path.join(__dirname, "Root.tsx");
  
  if (!fs.existsSync(rootPath)) {
    // Create default Root.tsx
    const defaultRoot = `import React from "react";
import { Composition } from "remotion";
import { ${component} } from "./scenes/${name}";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="${component}"
        component={${component}}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
`;
    fs.writeFileSync(rootPath, defaultRoot);
  }
}

function getFileType(filename) {
  const ext = filename.split(".").pop().toLowerCase();
  const types = {
    png: "image",
    jpg: "image",
    jpeg: "image",
    gif: "image",
    webp: "image",
    mp4: "video",
    webm: "video",
    mp3: "audio",
    wav: "audio"
  };
  return types[ext] || "unknown";
}

function getBaseUrl() {
  return process.env.RENDER_EXTERNAL_URL 
    ? \`https://\${process.env.RENDER_EXTERNAL_URL}\`
    : \`http://localhost:\${PORT}\`;
}

// ============ START ============

app.listen(PORT, "0.0.0.0", () => {
  console.log(`
╔═══════════════════════════════════════════════════╗
║                                                   ║
║     ██████╗ ███████╗██╗   ██╗                  ║
║     ██╔══██╗██╔════╝██║   ██║                  ║
║     ██║  ██║█████╗  ██║   ██║                  ║
║     ██║  ██║██╔══╝  ╚██╗ ██╔╝                  ║
║     ██████╔╝███████╗ ╚████╔╝                   ║
║     ╚═════╝ ╚══════╝  ╚═══╝                    ║
║                                                   ║
║     Agentic Video Maker                          ║
║     Version 0.1.0                                ║
║                                                   ║
╠═══════════════════════════════════════════════════╣
║  Server:      http://localhost:\${PORT}             ║
║  API Docs:    http://localhost:\${PORT}/api.html   ║
║                                                   ║
║  Endpoints:                                     ║
║  - POST /api/scenes  - Create scene            ║
║  - GET  /api/scenes  - List scenes             ║
║  - POST /api/render  - Render video            ║
║  - GET  /api/assets  - List assets             ║
║                                                   ║
╚═══════════════════════════════════════════════════╝
  `);
});
