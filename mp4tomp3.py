import subprocess
import argparse
import os

def convert_mp4_to_mp3(input_file, output_file=None):
    """
    Converts an MP4 file to an MP3 file using ffmpeg.

    :param input_file: Path to the input MP4 file.
    :param output_file: Path to the output MP3 file. If not provided, it will be the same as the input file with the extension changed to .mp3.
    """
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert an MP4 file to an MP3 file.")
    parser.add_argument("input_file", help="The path to the input MP4 file.")
    parser.add_argument("-o", "--output", help="The path to the output MP3 file.")
    args = parser.parse_args()

    convert_mp4_to_mp3(args.input_file, args.output)
