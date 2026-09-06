import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate } from "remotion";

// ÀYÍPADÀ — The Many-Faced God · 5 sec pilot (150 frames @30fps)
// Beat 1 (0-38):   the mask — "he has never owned a single face"
// Beat 2 (32-70):  the god emerges — "every mask, a life he wore"
// Beat 3 (64-104): the collection — "king · warrior · child · spirit · fool"
// Beat 4 (98-128): the reach — "he makes you question who you are"
// Beat 5 (122-150): title — ÀYÍPADÀ / THE MANY-FACED GOD

const SHOTS = [
  { start: 0, end: 38, image: "/assets/pilot_mask.jpg", z0: 1.0, z1: 1.14,
    caption: "he has never owned a single face" },
  { start: 32, end: 70, image: "/assets/pilot_emerge.png", z0: 1.02, z1: 1.16,
    caption: "every mask — a life he wore" },
  { start: 64, end: 104, image: "/assets/pilot_collection.png", z0: 1.0, z1: 1.12,
    caption: "king · warrior · child · spirit · fool" },
  { start: 98, end: 128, image: "/assets/pilot_reach.png", z0: 1.04, z1: 1.24,
    caption: "he makes you question who you are" },
  { start: 122, end: 150, image: "/assets/pilot_ancestors.png", z0: 1.0, z1: 1.09,
    caption: "" },
];

const captionStyle: React.CSSProperties = {
  position: "absolute",
  bottom: 150,
  width: "100%",
  textAlign: "center",
  color: "#f0e6d2",
  fontSize: 42,
  fontFamily: "Georgia, 'DejaVu Serif', serif",
  textShadow: "0 2px 12px rgba(0,0,0,0.9)",
  zIndex: 20,
};

export const Ayipada5SecPilot: React.FC = () => {
  const frame = useCurrentFrame();

  const globalFade =
    frame < 8
      ? interpolate(frame, [0, 8], [0, 1])
      : frame >= 142
        ? interpolate(frame, [142, 149], [1, 0])
        : 1;

  const titleOpacity = interpolate(frame, [122, 132], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "#000", opacity: globalFade }}>
      {SHOTS.map((s, i) => {
        if (frame < s.start || frame >= s.end) return null;
        const p = (frame - s.start) / (s.end - s.start);
        const fadeLen = 6;
        const opacity = Math.min(
          interpolate(frame, [s.start, s.start + fadeLen], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
          interpolate(frame, [s.end - fadeLen, s.end], [1, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        );
        const scale = interpolate(p, [0, 1], [s.z0, s.z1]);
        const dim = i === 4 ? interpolate(frame, [122, 132], [1, 0.55], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        }) : 1;
        const capOp = Math.min(
          interpolate(frame, [s.start, s.start + 8], [0, 1], {
            extrapolateLeft: "clamp", extrapolateRight: "clamp",
          }),
          interpolate(frame, [s.end - 8, s.end], [1, 0], {
            extrapolateLeft: "clamp", extrapolateRight: "clamp",
          }),
        );
        return (
          <AbsoluteFill key={i} style={{ opacity }}>
            <AbsoluteFill
              style={{
                transform: `scale(${scale})`,
                filter: `brightness(${dim})`,
                justifyContent: "center",
                alignItems: "center",
              }}
            >
              <img
                src={s.image}
                alt="Àyípadà"
                style={{ width: "100%", height: "100%", objectFit: "cover" }}
              />
            </AbsoluteFill>
            {/* vignette */}
            <div
              style={{
                position: "absolute", inset: 0,
                background:
                  "radial-gradient(ellipse at center, transparent 30%, rgba(0,0,0,0.55) 100%)",
              }}
            />
            {s.caption !== "" && (
              <div style={{ ...captionStyle, opacity: capOp }}>{s.caption}</div>
            )}
          </AbsoluteFill>
        );
      })}

      {/* letterbox */}
      <div style={{ position: "absolute", top: 0, width: "100%", height: 96, background: "#000", zIndex: 30 }} />
      <div style={{ position: "absolute", bottom: 0, width: "100%", height: 96, background: "#000", zIndex: 30 }} />

      {/* title card */}
      {frame >= 122 && (
        <div
          style={{
            position: "absolute", top: 300, width: "100%", textAlign: "center",
            opacity: titleOpacity, zIndex: 40,
          }}
        >
          <div
            style={{
              fontSize: 150, fontWeight: 800, color: "#b084ff",
              fontFamily: "Verdana, 'DejaVu Sans', sans-serif",
              letterSpacing: 24, textShadow: "0 4px 24px rgba(0,0,0,0.9)",
            }}
          >
            ÀYÍPADÀ
          </div>
          <div
            style={{
              fontSize: 40, color: "#ebe1f5", marginTop: 12,
              fontFamily: "Verdana, 'DejaVu Sans', sans-serif",
              letterSpacing: 16, textShadow: "0 2px 12px rgba(0,0,0,0.9)",
            }}
          >
            THE MANY-FACED GOD
          </div>
        </div>
      )}
    </AbsoluteFill>
  );
};
