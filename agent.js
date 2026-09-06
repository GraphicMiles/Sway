/**
 * SWAY AI Agent Client
 * 
 * Use this script to control SWAY from any AI agent.
 * 
 * Usage:
 *   node agent.js <command> [args]
 * 
 * Commands:
 *   node agent.js status                    - Check system status
 *   node agent.js scenes                   - List scenes
 *   node agent.js create <name> <image>   - Create new scene
 *   node agent.js render <composition>     - Render video
 *   node agent.js upload <file>            - Upload asset
 */

const http = require("http");
const fs = require("fs");
const path = require("path");

const BASE_URL = process.env.SWAY_URL || "http://localhost:3000";

// ============ HTTP HELPERS ============

function request(method, endpoint, data = null) {
  return new Promise((resolve, reject) => {
    const url = new URL(endpoint, BASE_URL);
    
    const options = {
      hostname: url.hostname,
      port: url.port || 80,
      path: url.pathname,
      method,
      headers: {
        "Content-Type": "application/json"
      }
    };
    
    const req = http.request(options, (res) => {
      let body = "";
      res.on("data", chunk => body += chunk);
      res.on("end", () => {
        try {
          resolve(JSON.parse(body));
        } catch {
          resolve(body);
        }
      });
    });
    
    req.on("error", reject);
    
    if (data) {
      req.write(JSON.stringify(data));
    }
    
    req.end();
  });
}

// ============ COMMANDS ============

async function status() {
  console.log("🔍 Checking SWAY status...\n");
  const result = await request("GET", "/status");
  console.log(JSON.stringify(result, null, 2));
}

async function listScenes() {
  console.log("📁 Listing scenes...\n");
  const result = await request("GET", "/api/scenes");
  console.log(JSON.stringify(result, null, 2));
}

async function createScene(name, image) {
  console.log(`🎬 Creating scene: ${name}\n`);
  
  const result = await request("POST", "/api/scenes", {
    name,
    component: name,
    props: { image: image || "/assets/placeholder.png" }
  });
  
  console.log(JSON.stringify(result, null, 2));
}

async function renderVideo(composition, output) {
  console.log(`🎬 Rendering: ${composition}\n`);
  
  const result = await request("POST", "/api/render", {
    composition: composition || "Main",
    output: output || `out/${composition || "video"}.mp4`
  });
  
  console.log(JSON.stringify(result, null, 2));
}

async function uploadAsset(filePath) {
  console.log(`📤 Uploading: ${filePath}\n`);
  
  if (!fs.existsSync(filePath)) {
    console.error("❌ File not found:", filePath);
    return;
  }
  
  const data = fs.readFileSync(filePath);
  const base64 = data.toString("base64");
  const ext = path.extname(filePath).slice(1);
  const mimeType = {
    png: "image/png",
    jpg: "image/jpeg",
    jpeg: "image/jpeg",
    gif: "image/gif",
    webp: "image/webp"
  }[ext] || "image/png";
  
  const result = await request("POST", "/api/assets", {
    name: path.basename(filePath),
    data: `data:${mimeType};base64,${base64}`,
    type: mimeType
  });
  
  console.log(JSON.stringify(result, null, 2));
}

async function listAssets() {
  console.log("🖼️ Listing assets...\n");
  const result = await request("GET", "/api/assets");
  console.log(JSON.stringify(result, null, 2));
}

// ============ CLI ============

const [,, command, arg1, arg2] = process.argv;

const commands = {
  status,
  scenes: listScenes,
  create: () => createScene(arg1, arg2),
  render: () => renderVideo(arg1, arg2),
  upload: () => uploadAsset(arg1),
  assets: listAssets,
  help: () => {
    console.log(`
SWAY AI Agent Client

Usage: node agent.js <command> [args]

Commands:
  status              - Check system status
  scenes              - List all scenes
  create <name>       - Create new scene
  render <comp>       - Render video
  upload <file>       - Upload asset file
  assets              - List all assets
  help                - Show this help

Examples:
  node agent.js status
  node agent.js create MyScene /assets/scene.png
  node agent.js render Main
  node agent.js upload my-image.png

Environment:
  SWAY_URL - Base URL of SWAY server (default: http://localhost:3000)
    `);
  }
};

const cmd = commands[command] || commands.help;
cmd();
