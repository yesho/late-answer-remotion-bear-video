# late-answer-remotion-bear-video

一个用于生成「迟到的答案」系列竖版讲解视频的 Codex Skill。

它的目标是把一篇中文概念寓言、知识故事或 Markdown 文章，变成一条适合小红书/短视频平台发布的 3:4 竖版 Remotion 视频。它强调完整故事、自然中文旁白、字幕逐字同步、稳定栏目视觉，以及渲染前后的质量检查。

## 适合做什么

- 把一篇概念寓言改造成 60-80 秒竖版讲解视频
- 延续「迟到的答案」暖纸小熊图文风格
- 用 Remotion 代码化管理画面、音频、字幕和时间线
- 生成自然中文 TTS 旁白
- 在没有图文卡片上游产物时，自行规划并生成视频所需的小熊/场景图片资源
- 从同一份 manifest 生成旁白、字幕和 Caption JSON
- 在最终导出前检查关键帧、字幕同步、音频时长和 MP4 编码

默认视频规格：

- 尺寸：`1080 x 1440`
- 帧率：`30fps`
- 比例：`3:4`
- 建议时长：`60-80s`

## 工作流

```text
文章 / 故事
  -> 故事结构
  -> 视频视觉资产计划
  -> 小熊/场景图片资源
  -> narration-manifest.json
  -> 神经 TTS 旁白
  -> captions.json
  -> Remotion 合成
  -> 关键帧 QA
  -> MP4 成片
```

默认结构：

1. Opening Cover：独立开场封面，静音，无字幕框
2. Setup：角色、任务、规则
3. Signals：事件与证据
4. Wrong Answer：错误直觉
5. Investigation：重新解释证据
6. Answer：答案与因果链
7. Principle：故事层面的原则
8. Concept Reveal：正式概念揭示
9. Final Insight：最终洞察
10. End Card：独立品牌结尾页

## 图片资源由谁负责生成

这个 Skill 可以单独使用，不要求先执行 `late-answer-html-bear-cards`。

如果用户已经提供了当前文章批准过的小熊/场景素材，或者 HTML 卡片 Skill 已经产出了可复用的当前文章素材，那么 Remotion 视频可以复用这些素材。

如果没有任何上游素材，则由 `late-answer-remotion-bear-video` 自己负责：

1. 根据故事结构创建视频视觉资产计划
2. 为 Opening Cover、主要故事场景、Concept Reveal、Final Insight、End Card 规划各自需要的插图
3. 使用图像生成工具生成当前文章专属的小熊/场景图片
4. 将中文标题、字幕、概念名、结尾文案保留在 Remotion 图层中，不写进生成图片
5. 把最终资产保存到视频项目中，例如：

```text
public/images/
  opening-cover-bear.png
  setup-bear.png
  signals-bear.png
  wrong-answer-bear.png
  investigation-bear.png
  answer-bear.png
  principle-bear.png
  concept-reveal-bear.png
  final-insight-bear.png
  end-card-bear.png
```

如果有可用的小熊参考图，应只把它作为角色身份参考；不要复用其他文章的最终成品插图。如果没有参考图，可以先生成一张当前项目的小熊参考图，再保持后续素材的一致性。

## 目录结构

```text
late-answer-remotion-bear-video/
  SKILL.md
  README.md
  LICENSE
  ASSETS_LICENSE.md
  agents/
    openai.yaml
  references/
    remotion-video-workflow.md
  scripts/
    build_captions.py
    generate_edge_voiceover.py
    validate_narration_sync.py
```

关键文件说明：

- `SKILL.md`：Codex Skill 主说明
- `references/remotion-video-workflow.md`：视频结构、manifest、TTS、时长和 QA 细则
- `scripts/generate_edge_voiceover.py`：根据 manifest 调用 Edge TTS 生成逐场景 MP3
- `scripts/build_captions.py`：从同一份 manifest 生成 `captions.json`
- `scripts/validate_narration_sync.py`：验证旁白、字幕、音频时长和音频文件是否匹配

## Manifest 规则

旁白是唯一事实源。

每个有声音的场景应包含 `narration`：

```json
{
  "id": "setup",
  "narration": "鹿王眼睛不好，便挂起铜铃。",
  "audio": "setup.mp3",
  "sceneStartMs": 3600,
  "sceneDurationMs": 6000,
  "narrationOffsetMs": 200,
  "audioDurationMs": 5200
}
```

如果显式写 `subtitle`，它必须和 `narration` 完全一致。不要为了“更短、更顺”另写一份字幕。

如果需要把一段旁白拆成多个字幕块，用 `narrationSegments`：

```json
{
  "id": "setup",
  "audio": "setup.mp3",
  "sceneStartMs": 3600,
  "sceneDurationMs": 6000,
  "audioDurationMs": 5200,
  "narrationSegments": [
    {"text": "第一句。", "startOffsetMs": 200, "endOffsetMs": 1800},
    {"text": "第二句。", "startOffsetMs": 1800, "endOffsetMs": 3400}
  ]
}
```

所有 `text` 拼接后的结果，就是 TTS 输入和屏幕字幕的来源。

## 生成旁白

这个脚本会把旁白文本发送给 Microsoft Edge TTS 服务。使用前应明确告知用户，并取得外部 TTS 调用许可。

```bash
python <skill-dir>/scripts/generate_edge_voiceover.py narration-manifest.json \
  --output-dir public/voiceover \
  --confirmed-external-tts
```

安全说明：`scene.audio` 只能是普通 MP3 文件名，例如 `setup.mp3`。脚本会拒绝绝对路径、盘符路径、`../`、路径分隔符和保留字符，避免把音频写到输出目录之外。

## 生成字幕

```bash
python <skill-dir>/scripts/build_captions.py narration-manifest.json \
  --output public/captions.json
```

`captions.json` 来自同一份 manifest，不应该单独手写或改写。

## 校验旁白和字幕

```bash
python <skill-dir>/scripts/validate_narration_sync.py narration-manifest.json \
  --audio-dir public/voiceover
```

通过时输出：

```text
narration/subtitle validation ok
```

校验内容包括：

- 场景 ID 是否重复
- `subtitle` 是否逐字等于 `narration`
- `audioDurationMs` 是否为正数
- 音频是否超出场景时长
- 分段字幕时间是否递增
- 音频文件是否存在

## Remotion 实现要求

- 使用 `Sequence`
- 使用 `premountFor`
- 使用 `<Img>`，不要直接用原生 `<img>`
- 使用 `staticFile()` 引用 public 资源
- 使用 `<Audio>` 播放 scene-local 音频
- 动效由 `useCurrentFrame()`、`interpolate()` 和 `Easing` 驱动
- 不使用 CSS transitions、CSS keyframes 或 Tailwind animation
- 背景音乐建议保持在 `0.10-0.16` 音量，避免压过旁白

## 输出建议

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
```

最终 MP4 应确认：

- `1080 x 1440`
- `30fps`
- H.264 视频流
- AAC 音频流
- 无旁白截断
- 字幕和旁白逐字同步

## 开源说明

- 代码、脚本和文字文档使用 MIT License，见 `LICENSE`
- 当前 skill 不内置图片、音频、字体或视频素材，素材说明见 `ASSETS_LICENSE.md`
- 使用 TTS、图片生成、字体、音乐或其他第三方资源时，请根据对应服务和素材来源确认授权与署名要求

## 注意事项

- 不要在未经用户明确同意时调用外部 TTS 服务
- 不要把多个故事碎片压缩进一条视频；优先讲完整单个故事
- 不要把 Final Insight 和 End Card 混成同一页
- 不要让字幕成为“概括版”，字幕必须和听到的旁白一致
- 不要复用其他文章的最终小熊插图；只能复用当前文章批准的素材
