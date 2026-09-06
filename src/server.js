const express = require("express");
const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");
const app = express();

app.use(express.json());

// Serve static files from public directory
app.use(express.static("public"));

// Health check
app.get("/health", (req, res) => {
  res.json({ status: "ok", timestamp: new Date().toISOString() });
});

// Get available compositions
app.get("/api/compositions", async (req, res) => {
  try {
    const output = execSync(
      "npx remotion compositions src/index.ts --props '{}'",
      { encoding: "utf-8", cwd: __dirname }
    );
    res.json({ success: true, data: output });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Render a specific composition
app.post("/api/render", async (req, res) => {
  const { composition = "FullPilot", output = "out/pilot.mp4" } = req.body;

  try {
    console.log(`Starting render for: ${composition}`);

    // Create output directory
    fs.mkdirSync("out", { recursive: true });

    // Render the video
    execSync(
      `npx remotion render ${composition} ${output} --props '{}'`,
      { stdio: "inherit", cwd: __dirname }
    );

    const filePath = path.join(__dirname, output);
    const fileSize = fs.existsSync(filePath)
      ? fs.statSync(filePath).size
      : 0;

    res.json({
      success: true,
      message: "Render complete",
      file: output,
      size: fileSize,
      downloadUrl: `https://${process.env.RENDER_EXTERNAL_URL || "localhost:3000"}/${output}`,
    });
  } catch (error) {
    console.error("Render error:", error);
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

// Download rendered video
app.get("/download/:filename", (req, res) => {
  const filename = req.params.filename;
  const filePath = path.join(__dirname, "out", filename);

  if (fs.existsSync(filePath)) {
    res.download(filePath);
  } else {
    res.status(404).json({ error: "File not found" });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, "0.0.0.0", () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`Remotion Studio: http://localhost:${PORT}`);
});
