/**
 * AI Agent - Video Generation Controller
 * 
 * This script allows AI agents to generate videos by:
 * 1. Writing scene components
 * 2. Committing to GitHub
 * 3. Triggering render on Render
 */

const { execSync } = require("child_process");
const fs = require("fs");
const https = require("https");

const GITHUB_REPO = "https://github.com/GraphicMiles/Sway.git";
const RENDER_URL = process.env.RENDER_URL || "https://ayipada-pilot.onrender.com";

/**
 * Add a new scene to the project
 */
function addScene(sceneName, pose) {
  const fileName = sceneName.charAt(0).toUpperCase() + sceneName.slice(1) + "Scene";
  
  const content = `import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring } from "remotion";
import { Character } from "../components/Character";

export const ${fileName}: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const animate = spring({
    frame,
    fps,
    config: { damping: 100, mass: 0.5 },
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#000000",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Character
        pose="${pose}"
        style={{
          transform: \`scale(\${0.9 + animate * 0.1})\`,
        }}
      />
    </AbsoluteFill>
  );
};
`;

  const path = `src/scenes/${fileName}.tsx`;
  fs.writeFileSync(path, content);
  console.log(`✅ Created scene: ${path}`);
  
  return path;
}

/**
 * Commit and push changes to GitHub
 */
function pushToGitHub(message) {
  try {
    execSync("git add .", { cwd: __dirname });
    execSync(`git commit -m "${message}"`, { cwd: __dirname });
    execSync("git push origin master", { cwd: __dirname });
    console.log("✅ Pushed to GitHub");
  } catch (error) {
    console.error("❌ Git error:", error.message);
  }
}

/**
 * Trigger render on Render
 */
function triggerRender(composition = "FullPilot") {
  const postData = JSON.stringify({
    composition,
    output: `out/${composition.toLowerCase()}.mp4`,
  });

  const url = new URL(RENDER_URL);
  const options = {
    hostname: url.hostname,
    port: 443,
    path: "/api/render",
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Content-Length": Buffer.byteLength(postData),
    },
  };

  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      let body = "";
      res.on("data", (chunk) => (body += chunk));
      res.on("end", () => {
        console.log("🎬 Render triggered!");
        console.log(body);
        resolve(JSON.parse(body));
      });
    });

    req.on("error", reject);
    req.write(postData);
    req.end();
  });
}

// Export for use
module.exports = { addScene, pushToGitHub, triggerRender };

// CLI usage
if (require.main === module) {
  const action = process.argv[2];
  
  if (action === "add") {
    const name = process.argv[3];
    const pose = process.argv[4] || name;
    addScene(name, pose);
  } else if (action === "render") {
    const comp = process.argv[3] || "FullPilot";
    triggerRender(comp);
  } else if (action === "push") {
    pushToGitHub(process.argv[3] || "Update scenes");
  } else {
    console.log("Usage:");
    console.log("  node generate.js add <sceneName> <pose>");
    console.log("  node generate.js render <composition>");
    console.log("  node generate.js push <message>");
  }
}
