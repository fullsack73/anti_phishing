import whisper
import os
from multiprocessing import Pool, cpu_count

# It's important to have a separate transcription function for each process
def transcribe_chunk(filepath):
    """
    Worker function to transcribe a single audio chunk.
    A new model object is created in each process to avoid issues with sharing.
    """
    # This print statement now happens inside the worker process
    # print(f"Processing {os.path.basename(filepath)}...") 
    model = whisper.load_model("base")
    result = model.transcribe(filepath, language='ko')
    return result.get("text", "").strip()

def main():
    # Folder containing audio chunks
    audio_chunks_folder = "data1_audio_chunks"
    output_file = "result.txt"

    # Get all chunk files and sort them to process in order
    try:
        files = sorted([f for f in os.listdir(audio_chunks_folder) if f.startswith("chunk_") and f.endswith(".mp3")])
        filepaths = [os.path.join(audio_chunks_folder, f) for f in files]
    except FileNotFoundError:
        print(f"Error: The directory '{audio_chunks_folder}' was not found.")
        return

    if not filepaths:
        print(f"No 'chunk_*.mp3' files found in '{audio_chunks_folder}'.")
        return

    # Use a pool of processes to transcribe chunks in parallel
    num_processes = min(cpu_count(), len(filepaths))
    print(f"Found {len(filepaths)} audio chunks. Processing in parallel using {num_processes} processes.")

    # Clear the output file before starting
    with open(output_file, "w", encoding="utf-8") as f:
        pass
    
    print(f"Results will be written to {output_file} as they are completed.")

    with Pool(num_processes) as pool:
        # Use imap to get results as they are completed, while preserving order.
        results_iterator = pool.imap(transcribe_chunk, filepaths)
        
        for i, transcribed_text in enumerate(results_iterator):
            with open(output_file, "a", encoding="utf-8") as f:
                f.write(transcribed_text + " ")
            print(f"Finished processing and saved chunk {i + 1}/{len(filepaths)}.")

    print("Processing complete.")

if __name__ == "__main__":
    main()
