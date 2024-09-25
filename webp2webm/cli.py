from pathlib import Path
from PIL import Image

import subprocess
import click


def extract_frames(webp_file: str, frames_dir: str) -> int:
    # validate the webp file nae
    webp_path = Path(webp_file)
    if not webp_path.is_file():
        raise ValueError(f"file {webp_path} not found")
    # load the emote into memory
    im = Image.open(webp_path)
    frames = []
    # loop through the frames
    durations = []
    try:
        while True:
            frame = im.convert("RGBA")
            frames.append(frame)
            durations.append(im.info['duration'])
            im.seek(im.tell() + 1)
    # end of sequence
    except EOFError:
        pass
    # compute the approximate fps
    avg_duration = sum(durations) / len(durations)
    fps = 1000 / avg_duration
    # create folder for storing frames
    emote_name = webp_path.stem
    emote_frames_dir = Path(frames_dir) / emote_name
    emote_frames_dir.mkdir(parents=True, exist_ok=True)
    # dump the frames
    for i, frame in enumerate(frames):
        output_path = emote_frames_dir / f"frame_{i:03d}.png"
        frame.save(output_path)
    return int(fps)


def merge_frames_into_webm(
    emote_frames_dir: str,
    webm_dir: str,
    in_fps: int,
    out_fps: int = 30,
    max_duration: int = 3,
    crf: int = 4,
    bitrate: str = "100K",
    width: int = 100,
    height: int = 100
) -> None:
    # create a pattern for frames
    image_pattern = f"{emote_frames_dir}/frame_%03d.png"
    # define a command
    emote_name = emote_frames_dir.split("/")[-1]
    webm_file = f"{webm_dir}/{emote_name}.webm"
    ffmpeg_command = [
        "ffmpeg",
        "-r", str(in_fps),
        "-i", image_pattern,
        "-vf", f"scale={width}:{height}",
        "-c:v", "libvpx-vp9",
        "-pix_fmt", "yuva420p",
        "-crf", str(crf),
        "-b:v", bitrate,
        "-auto-alt-ref", "0",
        "-lossless", "0",
        "-t", str(max_duration),
        "-fpsmax", str(out_fps),
        webm_file
    ]
    # run the command
    try:
        subprocess.run(ffmpeg_command, check=True)
        print(f"Video saved to {webm_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")


@click.command()
@click.option("--webp-dir", required=True, type=str, help="Folder that contains webp files")
@click.option("--webm-dir", required=True, type=str, help="Folder that will contain the resulting webm files")
@click.option("--temp-frames-dir", required=False, type=str, default="frames", help="Folder that would store frames of original webp files")
@click.option("--max-fps", required=False, type=int, default=30, help="Maximum FPS of the resulting webm files")
@click.option("--max-duration", required=False, type=int, default=3, help="Maximum duration of the resulting webm files in seconds")
@click.option("--crf", required=False, type=int, default=4, help="Constant rate factor, the lower the CRF the more details are preserved during conversion")
@click.option("--bitrate", required=False, type=str, default="100K", help="Output bitrate of the webm resulting file, the more the bitrate, the more details are preserved during conversion")
@click.option("--width", required=False, type=int, default=100, help="Width of resulting webm files")
@click.option("--height", required=False, type=int, default=100, help="Height of the resulting webm files")
def run(
    webp_dir: str,
    webm_dir: str,
    temp_frames_dir: str = "frames",
    max_fps: int = 30,
    max_duration: int = 3,
    crf: int = 4,
    bitrate: str = "100K",
    width: int = 100,
    height: int = 100
) -> None:
    # get the files with webp emotes
    webp_files = [str(p) for p in Path(webp_dir).glob("*.webp")]
    if not webp_files:
        raise ValueError(f"no `webp` files found in {webp_dir}")
    # make folder for storing temporary frames
    temp_frames_path = Path(temp_frames_dir)
    temp_frames_path.mkdir(parents=True, exist_ok=True)
    # make a lookup for fps per webp emote
    fps_lookup = {}
    for webp_file in webp_files:
        emote_name = Path(webp_file).stem
        fps = extract_frames(
            webp_file=webp_file,
            frames_dir=temp_frames_dir
        )
        fps_lookup[emote_name] = fps
    # merge frames into `webm` files
    webm_path = Path(webm_dir)
    webm_path.mkdir(parents=True, exist_ok=True)
    for frame_dir in Path(temp_frames_dir).glob("*"):
        emote_name = str(frame_dir).split("/")[-1]
        merge_frames_into_webm(
            emote_frames_dir=str(frame_dir),
            webm_dir=webm_dir,
            in_fps=fps_lookup[emote_name],
            out_fps=max_fps,
            max_duration=max_duration,
            crf=crf,
            bitrate=bitrate,
            width=width,
            height=height
        )
    print("original fps:", fps_lookup)


if __name__ == "__main__":
    run()
