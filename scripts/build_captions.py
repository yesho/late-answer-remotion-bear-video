import argparse
import json
from pathlib import Path


def scene_text(scene: dict) -> str:
    if "narrationSegments" in scene:
        return "".join(segment["text"] for segment in scene["narrationSegments"])
    return scene.get("narration", "")


def build(manifest: dict) -> list[dict]:
    captions = []
    for scene in manifest["scenes"]:
        if "narrationSegments" in scene:
            for segment in scene["narrationSegments"]:
                captions.append(
                    {
                        "text": segment["text"],
                        "startMs": scene["sceneStartMs"]
                        + segment["startOffsetMs"],
                        "endMs": scene["sceneStartMs"] + segment["endOffsetMs"],
                        "timestampMs": None,
                        "confidence": None,
                    }
                )
            continue

        text = scene_text(scene)
        if not text:
            continue
        start = scene["sceneStartMs"] + scene.get("narrationOffsetMs", 0)
        captions.append(
            {
                "text": text,
                "startMs": start,
                "endMs": start + scene["audioDurationMs"],
                "timestampMs": None,
                "confidence": None,
            }
        )
    return captions


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(build(manifest), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(args.output)


if __name__ == "__main__":
    main()
