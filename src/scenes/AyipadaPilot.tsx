import React from "react";
import { 
  AbsoluteFill, 
  useCurrentFrame, 
  useVideoConfig, 
  spring,
  interpolate,
  Img
} from "remotion";

export const AyipadaPilot: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const totalFrames = 600; // 20 seconds at 30fps

  // Scene timing - using actual image files
  const scenes = [
    { start: 0, end: 90, image: "/assets/02_emerging.png" },
    { start: 90, end: 180, image: "/assets/01_standing_front.png" },
    { start: 180, end: 270, image: "/assets/03_lurking.png" },
    { start: 270, end: 360, image: "/assets/05_collection.png" },
    { start: 360, end: 450, image: "/assets/06_reaching.png" },
    { start: 450, end: 540, image: "/assets/10_staring.png" },
    { start: 540, end: 600, image: "/assets/02_emerging.png" },
  ];

  // Find current scene
  const currentScene = scenes.find(s => frame >= s.start && frame < s.end);
  const sceneIndex = scenes.indexOf(currentScene);
  const sceneProgress = currentScene 
    ? (frame - currentScene.start) / (currentScene.end - currentScene.start) 
    : 0;

  // Fade between scenes
  const fadeIn = interpolate(Math.max(0, sceneProgress - 0.8) * 5, [0, 1], [0, 1]);
  const fadeOut = interpolate(Math.min(0.2, sceneProgress) * 5, [0, 1], [1, 0]);
  const opacity = Math.min(fadeIn, fadeOut);

  // Breathing animation
  const breathe = Math.sin(frame * 0.08) * 0.02 + 1;
  
  // Subtle sway
  const sway = Math.sin(frame * 0.05) * 1;

  // Scale based on scene
  const scale = interpolate(sceneProgress, [0, 0.5, 1], [0.95, 1.05, 0.95]);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#000000",
      }}
    >
      {/* Dark vignette effect */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: "radial-gradient(ellipse at center, transparent 0%, rgba(0,0,0,0.8) 100%)",
          zIndex: 10,
          pointerEvents: "none",
        }}
      />

      {/* Character */}
      <div
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: `translate(-50%, -50%) scale(${breathe * scale}) rotate(${sway}deg)`,
          opacity: opacity,
          width: "70%",
          maxWidth: 800,
        }}
      >
        {currentScene && (
          <img
            src={currentScene.image}
            alt="Àyípadà"
            style={{
              width: "100%",
              height: "auto",
              objectFit: "contain",
            }}
          />
        )}
      </div>

      {/* Subtle particle effect */}
      {[...Array(20)].map((_, i) => (
        <div
          key={i}
          style={{
            position: "absolute",
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            width: 2,
            height: 2,
            borderRadius: "50%",
            backgroundColor: "rgba(255, 255, 255, 0.1)",
            opacity: Math.sin(frame * 0.1 + i) * 0.5 + 0.5,
            transform: `translateY(${frame * 0.5 % 100}px)`,
          }}
        />
      ))}

      {/* Scene indicator (subtle) */}
      <div
        style={{
          position: "absolute",
          bottom: 30,
          left: 30,
          color: "rgba(255, 255, 255, 0.1)",
          fontSize: 12,
          fontFamily: "monospace",
        }}
      >
        {sceneIndex + 1} / {scenes.length}
      </div>
    </AbsoluteFill>
  );
};
