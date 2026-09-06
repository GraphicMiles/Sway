#!/bin/bash
# Render script for Remotion

COMPOSITION=${1:-FullPilot}
OUTPUT=${2:-out/pilot.mp4}

echo "Rendering $COMPOSITION to $OUTPUT..."
npx remotion render $COMPOSITION $OUTPUT --props '{}'
echo "Done! File saved to $OUTPUT"
