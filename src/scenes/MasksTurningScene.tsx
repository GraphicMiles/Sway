import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring } from "remotion";
import { Character } from "../components/Character";

export const MasksTurningScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const turn = spring({
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
        pose="masks-turning"
        style={{
          transform: `rotateY(${turn * 30}deg)`,
        }}
      />
    </AbsoluteFill>
  );
};
