# Remotion Video Workflow

## 1. Story Structure

Use this default sequence:

```text
Opening Cover: 3-4s, silent, simple emphasized title
01 Setup: character, task, rule
02 Signals: event and evidence
03 Wrong Answer: incorrect intuition
04 Investigation: how evidence is re-evaluated
05 Answer: result and causal chain
06 Principle: story-level lesson
07 Concept Reveal: formal term and mapping
08 Final Insight: one memorable conclusion
End Card: 4-5s, independent brand close
```

The cover attracts attention. It does not explain the story.  
The End Card closes the brand. It does not repeat the knowledge section.

## 2. Narration Manifest

Use JSON as the single source for TTS, subtitles, and timing:

```json
{
  "voice": "zh-CN-XiaoxiaoNeural",
  "rate": "-2%",
  "pitch": "-2Hz",
  "coverDurationMs": 3600,
  "endCardDurationMs": 4800,
  "scenes": [
    {
      "id": "setup",
      "narration": "鹿王眼睛不好，便挂起铜铃。",
      "subtitle": "鹿王眼睛不好，便挂起铜铃。",
      "audio": "setup.mp3",
      "sceneStartMs": 3600,
      "sceneDurationMs": 6000,
      "narrationOffsetMs": 200,
      "audioDurationMs": 5200
    }
  ]
}
```

`subtitle` is allowed only for explicit validation and must equal `narration` byte-for-byte after JSON decoding. Prefer omitting it and deriving the UI subtitle directly from `narration`.

For multiple blocks:

```json
{
  "narrationSegments": [
    {"text": "第一句。", "startOffsetMs": 200, "endOffsetMs": 1800},
    {"text": "第二句。", "startOffsetMs": 1800, "endOffsetMs": 3400}
  ]
}
```

Do not create a paraphrased full-scene caption. The concatenated segment text is the narration source.

## 3. Exact-Match Architecture

Use one field in application code:

```ts
type Scene = {
  id: string;
  narration: string;
  durationInFrames: number;
};

const subtitle = scene.narration;
const ttsInput = scene.narration;
```

Never use this pattern:

```ts
voiceover: "Long natural spoken sentence.",
caption: "Short rewritten summary."
```

Meaning-equivalent is still a failure. The user hears and reads words simultaneously, so punctuation, terminology, and sequence must match.

## 4. Neural TTS

Recommended defaults:

```text
voice: zh-CN-XiaoxiaoNeural
rate: -2%
pitch: -2Hz
```

Use scene-local MP3 files. Keep narration conversational and let visuals carry lists and secondary details.

Before using Edge TTS, tell the user that narration text will be sent to Microsoft and obtain explicit approval.

## 5. Video Image Assets

This workflow is standalone. If no current-article bear or scene assets are supplied, generate them as part of this skill before implementing the Remotion composition.

Create an asset plan that maps each required visual to a scene:

```text
opening-cover-bear.png: silent hook image for the cover
setup-bear.png: character, task, rule
signals-bear.png: event and evidence
wrong-answer-bear.png: incorrect intuition
investigation-bear.png: re-evaluating evidence
answer-bear.png: causal chain
principle-bear.png: story-level lesson
concept-reveal-bear.png: formal concept reveal
final-insight-bear.png: memorable conclusion
end-card-bear.png: independent brand close
```

Use this prompt pattern for each image asset:

```text
Create one clean illustration asset for a Chinese vertical Remotion explainer video.

Bear identity:
cream/off-white cute study bear, round soft body, small round ears, tiny dot eyes,
small oval nose, gentle small smile, small backpack, clear black hand-drawn outline,
soft plush/sketch texture, warm paper editorial style.

Scene purpose:
{scene role and story action}

Scene object:
{one simple metaphor object or prop}

Background:
transparent PNG preferred. If not possible, use one perfectly flat #faf9f5 background
with no shadow, gradient, texture, floor plane, or paper rectangle. The asset must blend
into a warm paper Remotion panel.

Composition:
single bear scene, generous whitespace, no text, no letters, no numbers, no logo,
no watermark. Suitable for a 1080x1440 vertical video layout.

Avoid:
multiple animals, panda, black bear, human, robot, dense background, accidental text,
white square background, cast shadows that reveal the image boundary.
```

Do not put Chinese text in generated images. Render titles, subtitles, labels, concept names, and end-card text in Remotion layers.

If `late-answer-html-bear-cards` has already produced current-article assets, the Remotion video may reuse those approved source bear/scene assets. Do not depend on that skill having run.

## 6. Timing

Measure generated audio with `ffprobe`.

```text
scene duration =
  narration offset
  + audio duration
  + ending pause
```

Defaults:

```text
narration offset: 200ms
ending pause: 500-900ms
cover: at least 2s fully settled
end card: at least 1.5s fully settled
```

Do not speed up narration merely to satisfy a fixed duration.

## 7. Visual Contract

```text
paper: #f5f4ed
ivory: #faf9f5
ink: #17191c
blue: #1B365D
muted: #706d66
line: #d9d5c9
mist: #edf3f8
clay: #b86f52
```

Use Noto Serif SC for display Chinese and Noto Sans SC for subtitles. Avoid dark technology themes, purple gradients, neon colors, grids, scan lines, glass effects, and generic dashboard motion.

## 8. Quality Gate

Inspect:

- Opening Cover settled frame
- densest story scene
- wrong-answer scene
- concept reveal
- Final Insight
- End Card settled frame

Validate:

- exact narration/subtitle equality
- audio duration fits scene
- subtitle timing stays within scene
- no silent scene accidentally has a subtitle
- no missing audio
- no missing image assets
- no text overflow
- no visible image background rectangle
- MP4 has video and audio streams
