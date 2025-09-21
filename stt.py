import whisper
import os
import time
from multiprocessing import Pool, cpu_count

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

# Global variable to hold the model in each worker process
worker_model = None

def init_worker():
    """Initializer for each worker process. Loads the model into memory."""
    global worker_model
    print(f"Initializing worker process {os.getpid()}...")
    worker_model = whisper.load_model(MODEL_SIZE)
    print(f"Worker {os.getpid()} initialized.")

def transcribe_and_save(filepath):
    """Transcribes a file using the worker's model and appends the result to the output file."""
    global worker_model
    try:
        result = worker_model.transcribe(filepath, language=LANGUAGE)
        text = result.get("text", "").strip()
        print(f"Transcribed {os.path.basename(filepath)}: {text}")
        
        output_text = text if text else "[no speech]"
        
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            f.write(output_text + " ")
            
        print(f"Appended '{output_text}' to {OUTPUT_FILE}")
        return True
    except Exception as e:
        print(f"Error transcribing {filepath} in worker {os.getpid()}: {e}")
        return False

class NewFileHandler(FileSystemEventHandler):
    def __init__(self, pool):
        self.pool = pool
        self.processed_files = set()

    def on_created(self, event):
        if event.is_directory:
            return

        filepath = event.src_path
        if filepath.endswith(".mp3") and filepath not in self.processed_files:
            print(f"New audio chunk detected: {os.path.basename(filepath)}")
            self.processed_files.add(filepath)
            # Wait a moment for the file to be fully written before processing
            time.sleep(0.25)
            self.pool.apply_async(transcribe_and_save, (filepath,))

def main():
    if not os.path.exists(AUDIO_CHUNKS_FOLDER):
        print(f"Error: The directory '{AUDIO_CHUNKS_FOLDER}' was not found.")
        return

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("")
    print(f"Output file '{OUTPUT_FILE}' cleared for this session.")

    num_processes = max(1, cpu_count() - 1)
    print(f"Starting process pool with {num_processes} workers.")

    with Pool(processes=num_processes, initializer=init_worker) as pool:
        event_handler = NewFileHandler(pool)
        observer = Observer()
        observer.schedule(event_handler, AUDIO_CHUNKS_FOLDER, recursive=False)
        observer.start()

        print(f"Watching for new .mp3 files in '{AUDIO_CHUNKS_FOLDER}'...")
        print("Press Ctrl+C to stop.")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping file watcher...")
            observer.stop()
        
        observer.join()
        print("Shutting down worker processes...")
        pool.close()
        pool.join()

    print("Processing stopped.")

if __name__ == "__main__":
    main()
