import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring } from "remotion";
import { Character } from "../components/Character";

export const LeaningBackScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const lean = spring({
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
        pose="leaning-back"
        style={{
          transform: `rotate(${(1 - lean) * 15}deg)`,
        }}
      />
    </AbsoluteFill>
  );
};
