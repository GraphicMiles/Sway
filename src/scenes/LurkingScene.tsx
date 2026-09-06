import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring } from "remotion";
import { Character } from "../components/Character";

export const LurkingScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const creepX = spring({
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
        justifyContent: "flex-start",
        paddingLeft: 200,
      }}
    >
      <Character
        pose="lurking"
        style={{
          transform: `translateX(${creepX * 100}px)`,
          opacity: 0.7,
        }}
      />
    </AbsoluteFill>
  );
};
