import React from "react";
import { Composition } from "remotion";
import { Main } from "./scenes/Main";
import { AyipadaPilot } from "./scenes/AyipadaPilot";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="Main"
        component={Main}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="AyipadaPilot"
        component={AyipadaPilot}
        durationInFrames={600}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
