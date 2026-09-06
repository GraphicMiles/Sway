import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring } from "remotion";
import { Character } from "../components/Character";

export const CollectionFloatingScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const float = spring({
    frame,
    fps,
    config: { damping: 50, mass: 1 },
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
        pose="floating-masks"
        style={{
          transform: `translateY(${Math.sin(frame * 0.1) * 20}px)`,
        }}
      />
    </AbsoluteFill>
  );
};
