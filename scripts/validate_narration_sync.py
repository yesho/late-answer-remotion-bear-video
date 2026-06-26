import argparse
import json
from pathlib import Path


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def spoken_text(scene: dict) -> str:
    if "narrationSegments" in scene:
        return "".join(segment["text"] for segment in scene["narrationSegments"])
    return scene.get("narration", "")


def validate(manifest: dict, audio_dir: Path | None) -> list[str]:
    errors: list[str] = []
    ids: set[str] = set()

    for index, scene in enumerate(manifest.get("scenes", [])):
        scene_id = scene.get("id", f"index-{index}")
        if scene_id in ids:
            fail(errors, f"{scene_id}: duplicate scene id")
        ids.add(scene_id)

        narration = spoken_text(scene)
        if "subtitle" in scene and scene["subtitle"] != narration:
            fail(errors, f"{scene_id}: subtitle does not exactly equal narration")

        duration = scene.get("sceneDurationMs")
        offset = scene.get("narrationOffsetMs", 0)
        audio_duration = scene.get("audioDurationMs", 0)
        if narration and duration is None:
            fail(errors, f"{scene_id}: missing sceneDurationMs")
        if narration and audio_duration <= 0:
            fail(errors, f"{scene_id}: missing positive audioDurationMs")
        if duration is not None and offset + audio_duration > duration:
            fail(errors, f"{scene_id}: narration audio exceeds scene duration")

        if "narrationSegments" in scene:
            previous_end = -1
            for segment_index, segment in enumerate(scene["narrationSegments"]):
                start = segment["startOffsetMs"]
                end = segment["endOffsetMs"]
                if not segment.get("text"):
                    fail(errors, f"{scene_id}: empty segment {segment_index}")
                if start < previous_end or end <= start:
                    fail(errors, f"{scene_id}: invalid segment timing {segment_index}")
                if duration is not None and end > duration:
                    fail(errors, f"{scene_id}: segment {segment_index} exceeds scene")
                previous_end = end

        if narration and audio_dir is not None:
            audio = audio_dir / scene.get("audio", f"{scene_id}.mp3")
            if not audio.is_file():
                fail(errors, f"{scene_id}: missing audio file {audio}")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--audio-dir", type=Path)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
    errors = validate(manifest, args.audio_dir)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print("narration/subtitle validation ok")


if __name__ == "__main__":
    main()
