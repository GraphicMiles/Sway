import React from "react";
import {
 AbsoluteFill,
  Sequence,
  useCurrentFrame,
  useVideoConfig,
  spring,
  useAnimatedStyle,
  interpolate,
} from "remotion";
import { Character } from "../components/Character";

export const OpeningScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const opacity = spring({
    frame,
    fps,
    config: { damping: 200, mass: 0.5 },
  });

  const scale = spring({
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
      <Sequence from={0} name="CharacterEmerging">
        <Character
          pose="emerging"
          style={{
            opacity,
            transform: `scale(${scale})`,
          }}
        />
      </Sequence>
    </AbsoluteFill>
  );
};
