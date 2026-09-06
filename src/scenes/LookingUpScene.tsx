import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring } from "remotion";
import { Character } from "../components/Character";

export const LookingUpScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const lookUp = spring({
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
        pose="looking-up"
        style={{
          transform: `translateY(${lookUp * 30}px)`,
        }}
      />
    </AbsoluteFill>
  );
};
