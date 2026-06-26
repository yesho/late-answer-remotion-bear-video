import argparse
import asyncio
import json
from pathlib import Path
import re

import edge_tts


def safe_audio_filename(raw_name: str) -> str:
    filename = str(raw_name or "").strip()
    if not filename:
        raise ValueError("audio filename cannot be empty")
    if not filename.lower().endswith(".mp3"):
        filename = f"{filename}.mp3"

    unsafe_reason = next(
        (
            reason
            for condition, reason in [
                (Path(filename).is_absolute(), "absolute paths are not allowed"),
                (re.match(r"^[a-zA-Z]:", filename) is not None, "drive-qualified paths are not allowed"),
                ("/" in filename or "\\" in filename, "path separators are not allowed"),
                (".." in filename, "parent-directory segments are not allowed"),
                (re.search(r'[<>:"|?*\x00-\x1F]', filename) is not None, "reserved characters are not allowed"),
            ]
            if condition
        ),
        None,
    )
    if unsafe_reason:
        raise ValueError(
            f'Unsafe audio filename "{raw_name}": {unsafe_reason}. '
            'Use a plain filename such as "setup.mp3".'
        )
    return filename


def output_path_inside_directory(output_dir: Path, filename: str) -> Path:
    directory = output_dir.resolve()
    target = (directory / filename).resolve()
    if target.parent != directory:
        raise ValueError(f"Refusing to write outside output directory: {target}")
    return target


def narration_for(scene: dict) -> str:
    if "narrationSegments" in scene:
        return "".join(segment["text"] for segment in scene["narrationSegments"])
    return scene.get("narration", "")


async def render_scene(
    scene: dict,
    output_dir: Path,
    voice: str,
    rate: str,
    pitch: str,
) -> None:
    text = narration_for(scene)
    if not text:
        return
    filename = safe_audio_filename(scene.get("audio", f"{scene['id']}.mp3"))
    output_path = output_path_inside_directory(output_dir, filename)
    communicator = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate,
        pitch=pitch,
        volume="+0%",
        boundary="SentenceBoundary",
    )
    await communicator.save(str(output_path))
    print(output_path)


async def run(args: argparse.Namespace) -> None:
    if not args.confirmed_external_tts:
        raise SystemExit(
            "Refusing external TTS export without --confirmed-external-tts."
        )
    manifest = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    for scene in manifest["scenes"]:
        await render_scene(
            scene,
            output_dir,
            manifest.get("voice", "zh-CN-XiaoxiaoNeural"),
            manifest.get("rate", "-2%"),
            manifest.get("pitch", "-2Hz"),
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--confirmed-external-tts", action="store_true")
    asyncio.run(run(parser.parse_args()))


if __name__ == "__main__":
    main()
