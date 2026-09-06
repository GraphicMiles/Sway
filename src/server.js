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
const { execSync } = require("child_process");

const app = express();
app.use(cors());
app.use(express.json());
// /pilot page — registered BEFORE static so it isn't shadowed
// by the public/pilot/ asset directory (which would 301 /pilot -> /pilot/)
app.get("/pilot", (req, res) => {
  res.sendFile(path.join(__dirname, "..", "public", "pilot.html"));
});
app.use(express.static("public"));
app.use("/assets", express.static(path.join(__dirname, "..", "assets")));

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
  const scenesDir = path.join(__dirname, "scenes");
  const scenes = fs.existsSync(scenesDir) 
    ? fs.readdirSync(scenesDir).filter(f => f.endsWith(".tsx")).length 
    : 0;
  
  res.json({
    scenes,
    uptime: process.uptime(),
    version: "0.1.0"
  });
});

// ============ COMPOSITIONS API ============

app.get("/api/compositions", (req, res) => {
  const scenesDir = path.join(__dirname, "scenes");
  if (!fs.existsSync(scenesDir)) {
    return res.json({ success: true, compositions: [] });
  }
  
  const compositions = fs.readdirSync(scenesDir)
    .filter(f => f.endsWith(".tsx"))
    .map(f => f.replace(".tsx", ""));
  
  res.json({ success: true, compositions });
});

// ============ RENDER API ============

app.post("/api/render", async (req, res) => {
  const { composition = "Main", output, props = {} } = req.body;
  
  const outputFile = output || "out/video.mp4";
  
  try {
    console.log("Rendering:", composition);
    
    // Ensure output directory exists
    const outDir = path.join(__dirname, "..", "out");
    if (!fs.existsSync(outDir)) {
      fs.mkdirSync(outDir, { recursive: true });
    }
    
    // Render using Remotion CLI
    const propsString = JSON.stringify(props).replace(/'/g, "'");
    const renderCmd = `npx remotion render ${composition} ${outputFile} --props '${propsString}'`;
    
    execSync(renderCmd, {
      cwd: path.join(__dirname, ".."),
      stdio: "inherit"
    });
    
    const baseUrl = process.env.RENDER_EXTERNAL_URL 
      ? "https://" + process.env.RENDER_EXTERNAL_URL 
      : "http://localhost:" + PORT;
    
    res.json({
      success: true,
      message: "Render complete",
      composition,
      output: outputFile,
      downloadUrl: baseUrl + "/" + outputFile
    });
    
  } catch (error) {
    console.error("Render error:", error.message);
    res.status(500).json({ 
      success: false, 
      error: error.message
    });
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

function getBaseUrl() {
  if (process.env.RENDER_EXTERNAL_URL) {
    return "https://" + process.env.RENDER_EXTERNAL_URL;
  }
  return "http://localhost:" + PORT;
}

// ============ START ============

app.listen(PORT, "0.0.0.0", () => {
  console.log("SWAY v0.1.0 - Agentic Video Maker");
  console.log("Server running on port", PORT);
  console.log("Health:", "http://localhost:" + PORT + "/health");
  console.log("API:", "http://localhost:" + PORT + "/api/compositions");
});
