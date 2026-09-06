import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import { Img } from "remotion";

// Import your character images
// Replace these paths with your actual character images from /home/user/scenes_focused/
import standingFront from "../assets/01_standing_front.png";
import emerging from "../assets/02_emerging.png";
import lurking from "../assets/03_lurking.png";
import raisingHand from "../assets/04_raising_hand.png";
import collection from "../assets/05_collection.png";
import reaching from "../assets/06_reaching.png";
import leaningBack from "../assets/07_leaning_back.png";
import lookingUp from "../assets/08_looking_up.png";
import masksTurning from "../assets/09_masks_turning.png";
import staring from "../assets/10_staring.png";

type Pose =
  | "standing-front"
  | "emerging"
  | "lurking"
  | "raising-hand"
  | "floating-masks"
  | "reaching"
  | "leaning-back"
  | "looking-up"
  | "masks-turning"
  | "staring"
  | "collection";

interface CharacterProps {
  pose: Pose;
  style?: React.CSSProperties;
}

const poseImages: Record<Pose, string> = {
  "standing-front": standingFront,
  "emerging": emerging,
  "lurking": lurking,
  "raising-hand": raisingHand,
  "floating-masks": collection,
  "reaching": reaching,
  "leaning-back": leaningBack,
  "looking-up": lookingUp,
  "masks-turning": masksTurning,
  "staring": staring,
  "collection": collection,
};

export const Character: React.FC<CharacterProps> = ({ pose, style = {} }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Breathing animation
  const breathe = Math.sin(frame * 0.05) * 0.02 + 1;

  // Sway animation
  const sway = Math.sin(frame * 0.03) * 2;

  const imageSrc = poseImages[pose];

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        width: "100%",
        height: "100%",
        transform: `scale(${breathe}) rotate(${sway}deg)`,
        ...style,
      }}
    >
      {imageSrc && (
        <Img
          src={imageSrc}
          style={{
            width: "80%",
            maxWidth: 800,
            height: "auto",
            objectFit: "contain",
          }}
        />
      )}
    </div>
  );
};
