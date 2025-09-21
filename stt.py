import whisper
import os
import time

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("Watchdog library not found. Please install it using: pip install watchdog")
    exit()

# --- Configuration ---
AUDIO_CHUNKS_FOLDER = "data1_audio_chunks"
OUTPUT_FILE = "result.txt"
MODEL_SIZE = "small"  # tiny, base, small, medium, large
LANGUAGE = "ko"
# --- End Configuration ---

def transcribe_file(model, filepath):
    """Transcribes a single audio file and returns the text."""
    try:
        result = model.transcribe(filepath, language=LANGUAGE)
        text = result.get("text", "").strip()
        print(f"Transcribed {os.path.basename(filepath)}: {text}")
        return text
    except Exception as e:
        print(f"Error transcribing {filepath}: {e}")
        return ""

class NewFileHandler(FileSystemEventHandler):
    def __init__(self, model, output_file):
        self.model = model
        self.output_file = output_file
        # Keep track of processed files to avoid duplicates
        self.processed_files = set()

    def on_created(self, event):
        """Called when a file or directory is created."""
        if event.is_directory:
            return

        filepath = event.src_path
        if filepath.endswith(".mp3") and filepath not in self.processed_files:
            print(f"New audio chunk detected: {os.path.basename(filepath)}")
            # Wait a moment for the file to be fully written
            time.sleep(0.25)
            
            transcribed_text = transcribe_file(self.model, filepath)
            
            # Use a placeholder if transcription is empty, otherwise use the transcribed text.
            output_text = transcribed_text if transcribed_text else "[no speech]"
            
            with open(self.output_file, "a", encoding="utf-8") as f:
                f.write(output_text + " ")

            # Add to processed files regardless of transcription result to avoid reprocessing.
            self.processed_files.add(filepath)
            print(f"Appended '{output_text}' to {self.output_file}")

def main():
    """
    Main function to initialize the model and start monitoring the directory.
    """
    if not os.path.exists(AUDIO_CHUNKS_FOLDER):
        print(f"Error: The directory '{AUDIO_CHUNKS_FOLDER}' was not found.")
        print("Please create it and ensure audio chunks are saved there.")
        return

    # Clear the output file at the start of a new session
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("") 
    print(f"Output file '{OUTPUT_FILE}' cleared for this session.")

    print(f"Loading Whisper model '{MODEL_SIZE}'...")
    model = whisper.load_model(MODEL_SIZE)
    print("Model loaded. Starting live transcription monitoring.")

    event_handler = NewFileHandler(model, OUTPUT_FILE)
    observer = Observer()
    observer.schedule(event_handler, AUDIO_CHUNKS_FOLDER, recursive=False)
    
    observer.start()
    print(f"Watching for new .mp3 files in '{AUDIO_CHUNKS_FOLDER}'...")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nStopping observer.")
    
    observer.join()
    print("Processing stopped.")

if __name__ == "__main__":
    main()
