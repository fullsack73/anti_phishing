import subprocess
import argparse
import os

def convert_mp4_to_mp3(input_file, output_file=None):
    if not os.path.exists(input_file):
        print(f"Error: Input file not found at {input_file}")
        return

    if output_file is None:
        base, _ = os.path.splitext(input_file)
        output_file = base + ".mp3"

    command = [
        "ffmpeg",
        "-i", input_file,
        "-vn",  # Disable video recording
        "-acodec", "libmp3lame",  # Use LAME for MP3 encoding
        "-q:a", "2",  # VBR quality, 0 is highest, 9 is lowest. 2 is a good balance.
        output_file,
    ]

    try:
        print(f"Converting {input_file} to {output_file}...")
        subprocess.run(command, check=True, capture_output=True, text=True)
        print("Conversion successful!")
    except FileNotFoundError:
        print("Error: ffmpeg is not installed or not in your PATH. Please install ffmpeg.")
    except subprocess.CalledProcessError as e:
        print("Error during conversion:")
        print(e.stderr)

def convert_mp4_to_audio_chunks(input_file, output_dir=None, chunk_duration=10):
    if not os.path.exists(input_file):
        print(f"Error: Input file not found at {input_file}")
        return

    if output_dir is None:
        base, _ = os.path.splitext(input_file)
        output_dir = base + "_audio_chunks"

    os.makedirs(output_dir, exist_ok=True)

    output_pattern = os.path.join(output_dir, "chunk_%03d.mp3")

    command = [
        "ffmpeg",
        "-i", input_file,
        "-f", "segment",
        "-segment_time", str(chunk_duration),
        "-vn",  # Disable video recording
        "-acodec", "libmp3lame",  # Use LAME for MP3 encoding
        "-q:a", "2",  # VBR quality, 2 is a good balance.
        output_pattern,
    ]

    try:
        print(f"Converting {input_file} and splitting into {chunk_duration}s chunks in {output_dir}...")
        subprocess.run(command, check=True, capture_output=True, text=True)
        print("Conversion and splitting successful!")
    except FileNotFoundError:
        print("Error: ffmpeg is not installed or not in your PATH. Please install ffmpeg.")
    except subprocess.CalledProcessError as e:
        print("Error during conversion:")
        print(e.stderr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert an MP4 file to 3-second MP3 audio chunks by default.")
    parser.add_argument("input_file", nargs='?', default="data1.mp4", help="The path to the input MP4 file (default: data1.mp4).")
    parser.add_argument("-o", "--output", help="The path to the output MP3 file or directory.")
    parser.add_argument("--single", action="store_true", help="Convert to a single MP3 file instead of chunks.")
    args = parser.parse_args()

    if args.single:
        convert_mp4_to_mp3(args.input_file, args.output)
    else:
        convert_mp4_to_audio_chunks(args.input_file, args.output)
