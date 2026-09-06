import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring } from "remotion";
import { Character } from "../components/Character";

export const ReachingScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const reach = spring({
    frame,
    fps,
    config: { damping: 80, mass: 0.5 },
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
        pose="reaching"
        style={{
          transform: `scale(${0.9 + reach * 0.1})`,
        }}
      />
    </AbsoluteFill>
  );
};
