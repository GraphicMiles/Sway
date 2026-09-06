import React from "react";
import { 
  AbsoluteFill, 
  useCurrentFrame, 
  useVideoConfig, 
  spring,
  interpolate 
} from "remotion";

interface MainProps {
  backgroundColor?: string;
  image?: string;
}

export const Main: React.FC<MainProps> = ({ 
  backgroundColor = "#000000",
  image 
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance animation
  const entrance = spring({
    frame,
    fps,
    config: { damping: 100, mass: 0.5 }
  });

  // Subtle breathing animation
  const breathe = Math.sin(frame * 0.05) * 0.02 + 1;
  
  // Gentle sway
  const sway = Math.sin(frame * 0.03) * 2;

  return (
    <AbsoluteFill
      style={{
        backgroundColor,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <div
        style={{
          transform: `scale(${breathe}) rotate(${sway}deg)`,
          opacity: entrance,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        {image ? (
          <img
            src={image}
            alt="scene"
            style={{
              maxWidth: "80%",
              maxHeight: "80%",
              objectFit: "contain",
            }}
          />
        ) : (
          <div
            style={{
              width: 400,
              height: 400,
              backgroundColor: "#1a1a1a",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#666",
              fontSize: 24,
              fontFamily: "monospace",
            }}
          >
            Add image
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
};
