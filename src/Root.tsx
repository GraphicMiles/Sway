import React from "react";
import { Composition } from "remotion";
import { OpeningScene } from "./scenes/OpeningScene";
import { CollectionScene } from "./scenes/CollectionScene";
import { LurkingScene } from "./scenes/LurkingScene";
import { RaisingHandScene } from "./scenes/RaisingHandScene";
import { CollectionFloatingScene } from "./scenes/CollectionFloatingScene";
import { ReachingScene } from "./scenes/ReachingScene";
import { LeaningBackScene } from "./scenes/LeaningBackScene";
import { LookingUpScene } from "./scenes/LookingUpScene";
import { MasksTurningScene } from "./scenes/MasksTurningScene";
import { StaringScene } from "./scenes/StaringScene";
import { TransitionSeries, springTiming } from "@remotion/transitions";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="Opening"
        component={OpeningScene}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="Collection"
        component={CollectionScene}
        durationInFrames={180}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="Lurking"
        component={LurkingScene}
        durationInFrames={120}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="RaisingHand"
        component={RaisingHandScene}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="CollectionFloating"
        component={CollectionFloatingScene}
        durationInFrames={180}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="Reaching"
        component={ReachingScene}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="LeaningBack"
        component={LeaningBackScene}
        durationInFrames={120}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="LookingUp"
        component={LookingUpScene}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="MasksTurning"
        component={MasksTurningScene}
        durationInFrames={180}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="Staring"
        component={StaringScene}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="FullPilot"
        component={FullPilot}
        durationInFrames={1800}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};

const FullPilot: React.FC = () => {
  return (
    <TransitionSeries>
      <TransitionSeries.Sequence durationInFrames={150}>
        <OpeningScene />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition
        presentation={springTiming({ damping: 200, mass: 0.5 })}
        durationInFrames={30}
      />
      <TransitionSeries.Sequence durationInFrames={180}>
        <CollectionScene />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition
        presentation={springTiming({ damping: 200, mass: 0.5 })}
        durationInFrames={30}
      />
      <TransitionSeries.Sequence durationInFrames={120}>
        <LurkingScene />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition
        presentation={springTiming({ damping: 200, mass: 0.5 })}
        durationInFrames={30}
      />
      <TransitionSeries.Sequence durationInFrames={150}>
        <RaisingHandScene />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition
        presentation={springTiming({ damping: 200, mass: 0.5 })}
        durationInFrames={30}
      />
      <TransitionSeries.Sequence durationInFrames={180}>
        <CollectionFloatingScene />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition
        presentation={springTiming({ damping: 200, mass: 0.5 })}
        durationInFrames={30}
      />
      <TransitionSeries.Sequence durationInFrames={150}>
        <ReachingScene />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition
        presentation={springTiming({ damping: 200, mass: 0.5 })}
        durationInFrames={30}
      />
      <TransitionSeries.Sequence durationInFrames={120}>
        <LeaningBackScene />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition
        presentation={springTiming({ damping: 200, mass: 0.5 })}
        durationInFrames={30}
      />
      <TransitionSeries.Sequence durationInFrames={150}>
        <LookingUpScene />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition
        presentation={springTiming({ damping: 200, mass: 0.5 })}
        durationInFrames={30}
      />
      <TransitionSeries.Sequence durationInFrames={180}>
        <MasksTurningScene />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition
        presentation={springTiming({ damping: 200, mass: 0.5 })}
        durationInFrames={30}
      />
      <TransitionSeries.Sequence durationInFrames={150}>
        <StaringScene />
      </TransitionSeries.Sequence>
    </TransitionSeries>
  );
};
