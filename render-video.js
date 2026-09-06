const { bundle } = require("@remotion/bundler");
const { renderMedia, selectComposition } = require("@remotion/renderer");
const path = require("path");

async function build() {
  // Bundle the Remotion project
  const bundleLocation = await bundle({
    entryPoint: path.resolve(__dirname, "src/index.ts"),
    webpackOverride: (f) => f,
  });

  // Select the composition
  const composition = await selectComposition({
    serveUrl: bundleLocation,
    id: "FullPilot",
  });

  // Render the video
  await renderMedia({
    composition,
    serveUrl: bundleLocation,
    codec: "h264",
    outputLocation: "out/Ayipada-Pilot.mp4",
  });

  console.log("Video rendered successfully!");
}

build().catch((err) => {
  console.error(err);
  process.exit(1);
});
