import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring } from "remotion";
import { Character } from "../components/Character";

export const StaringScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const stare = spring({
    frame,
    fps,
    config: { damping: 200, mass: 0.5 },
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
        pose="staring"
        style={{
          transform: `scale(${0.9 + stare * 0.1})`,
          filter: `brightness(${0.7 + stare * 0.3})`,
        }}
      />
    </AbsoluteFill>
  );
};
