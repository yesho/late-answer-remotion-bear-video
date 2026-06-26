---
name: late-answer-remotion-bear-video
description: Generate Chinese 3:4 Remotion explainer videos for the "迟到的答案" concept-fable series, matching the warm-paper Xiaohongshu bear-card visual identity. Use when Codex needs to turn a Markdown 寓言/知识故事 and its article-specific bear assets into a narrated vertical video with an independent opening cover, complete single-story arc, concept reveal, independent End Card, natural Chinese neural TTS, and subtitles that match the spoken narration exactly.
---

# Late Answer Remotion Bear Video

Build a polished vertical explainer with this pipeline:

```text
article -> story plan -> narration manifest -> article bear assets
-> neural TTS + captions from one source -> Remotion -> key-frame QA -> MP4
```

Read `references/remotion-video-workflow.md` before implementation.

## Non-Negotiable Contract

- Use `1080 x 1440`, 30fps.
- Match the card series: warm paper `#f5f4ed`, ivory `#faf9f5`, ink blue `#1B365D`.
- Reuse only the current article's approved bear assets. Never reuse final artwork from another article.
- Include an independent 3-4 second Opening Cover with no subtitle box.
- Tell one complete story before revealing the concept.
- Keep Final Insight separate from the independent 4-5 second End Card.
- Prefer natural narration over an arbitrary one-minute limit. Default to 60-80 seconds.
- Use natural Chinese neural TTS. Recommend `zh-CN-XiaoxiaoNeural`, rate `-6%` to `0%`.
- Ask for explicit approval before sending narration text to an external TTS service.

## Visual Asset Responsibility

This skill is responsible for the video's image assets when they are not already provided.

Do not assume `late-answer-html-bear-cards` has run first. That skill may be an optional upstream source for article-specific bear assets, but it is not a prerequisite.

When the user has not supplied approved current-article assets:

- Create a video visual asset plan after the story plan and before Remotion implementation.
- Generate fresh current-article assets for the Opening Cover, each major story scene, Concept Reveal, Final Insight, and End Card.
- Use image generation only for illustration assets, not for final Chinese subtitles or body text.
- Keep all Chinese text in Remotion layers so it stays editable and crisp.
- Use a consistent cream/off-white study bear identity: round soft body, small round ears, tiny dot eyes, small oval nose, gentle smile, small backpack, hand-drawn outline, warm paper texture.
- Prefer transparent PNG assets. If transparency is not available, use a flat `#faf9f5` background or remove a chroma-key background locally before composing.
- Save generated image assets under the video project, for example `public/images/` or `dist/<slug>-remotion-video/assets/`.

If a canonical bear reference image is available from the user's workspace or a prior approved article, use it only as an identity reference. If no reference is available, generate a simple article-specific bear reference sheet first and use it consistently for the rest of that video's assets.

## Exact Subtitle Rule

Treat narration as the single source of truth.

- Store one `narration` string per spoken scene.
- Send that exact string to TTS.
- Render that exact string in the lower subtitle.
- Generate Caption JSON from that same field.
- Do not author a separate shortened, polished, or paraphrased `caption`.
- Do not change punctuation, English terms, numbers, or word order between TTS and subtitle.
- If subtitles need multiple timed blocks, split the source into `narrationSegments`. Send and display the same segments in the same order. Their exact concatenation must equal the spoken text.
- Opening Cover and silent End Card may intentionally have no narration and no subtitle.

Run before every final render:

```bash
python <skill>/scripts/validate_narration_sync.py <manifest.json> --audio-dir <voiceover-dir>
```

Any mismatch is a hard failure.

## Workflow

1. Read the article and identify the hook, setting, error, investigation, answer, principle, concept mapping, and final insight.
2. Choose one complete story case. Do not compress several similar cases into fragments.
3. Create:
   - Opening Cover
   - 5 story scenes
   - principle
   - concept reveal
   - Final Insight
   - independent End Card
4. Create the video visual asset plan. If current-article assets are not supplied, generate the required bear/scene assets now.
5. Create `narration-manifest.json` using the schema in the workflow reference.
6. Generate TTS only after external-service approval:

```bash
python <skill>/scripts/generate_edge_voiceover.py <manifest.json> \
  --output-dir <project>/public/voiceover \
  --confirmed-external-tts
```

7. Generate captions from the same manifest:

```bash
python <skill>/scripts/build_captions.py <manifest.json> \
  --output <project>/public/captions.json
```

8. Set each scene duration from measured audio duration plus:
   - `200-400ms` opening buffer
   - `500-900ms` ending pause
9. Implement Remotion using `Sequence`, `premountFor`, `<Img>`, `staticFile()`, and `<Audio>`.
10. Render and inspect Opening Cover, dense story scene, concept reveal, Final Insight, and End Card.
11. Validate narration/subtitles, render MP4, then verify dimensions, duration, video codec, and audio stream with `ffprobe`.

## Remotion Rules

- Drive all motion with `useCurrentFrame()`, `interpolate()`, and `Easing`.
- Do not use CSS transitions, CSS keyframes, or Tailwind animation.
- Keep motion editorial: page turns, paper placement, subtle translations, and fades.
- Use `<Img>` instead of native `<img>`.
- Put public assets behind `staticFile()`.
- Add `premountFor` to every `Sequence`.
- Keep narration scene-local. Never cut or overlap spoken audio across scenes.
- Use background music around `0.10-0.16` under narration.

## Deliverables

```text
dist/<slug>-remotion-video/
  <slug>.mp4
  opening-cover.png
  end-card.png
  captions.json
  narration-manifest.json
  voiceover.md
  timeline.md
  video-prompt.md
  assets/
    opening-cover-bear.png
    setup-bear.png
    ...
```

Pass only when:

- The story is understandable without the source article.
- Opening Cover and End Card are visually independent.
- Every spoken scene's visible subtitle is exactly its TTS input.
- No narration is truncated.
- Bear assets blend into the panel without visible rectangles.
- Required current-article image assets exist even when no HTML-card workflow was run first.
- The MP4 is `1080 x 1440`, 30fps, with valid H.264 and AAC streams.
