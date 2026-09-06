import React from "react";
import { Composition } from "remotion";

// Import scenes dynamically
// Add your scenes here as they're created

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="Main"
        component={require("./scenes/Main").Main}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
