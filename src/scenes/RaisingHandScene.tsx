import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring } from "remotion";
import { Character } from "../components/Character";

export const RaisingHandScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const raiseHand = spring({
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
        pose="raising-hand"
        style={{
          transform: `translateY(${(1 - raiseHand) * 50}px)`,
        }}
      />
    </AbsoluteFill>
  );
};
