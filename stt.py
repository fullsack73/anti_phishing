import whisper
import os
from multiprocessing import Pool, cpu_count

# It's important to have a separate transcription function for each process
def transcribe_chunk(filepath):
    """
    Worker function to transcribe a single audio chunk.
    A new model object is created in each process to avoid issues with sharing.
    """
    print(f"Processing {os.path.basename(filepath)} in a separate process...")
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

    if not files:
        print(f"No 'chunk_*.mp3' files found in '{audio_chunks_folder}'.")
        return

    # Use a pool of processes to transcribe chunks in parallel
    # Using cpu_count() is a good default for the number of processes
    num_processes = min(cpu_count(), len(filepaths))
    print(f"Found {len(files)} audio chunks. Processing them in parallel using {num_processes} processes.")

    with Pool(num_processes) as pool:
        # map applies the function to each item in the list and returns results in order
        transcribed_texts = pool.map(transcribe_chunk, filepaths)

    # Write the final results to the output file
    print(f"All chunks processed. Saving result to {output_file}...")
    with open(output_file, "w", encoding="utf-8") as f:
        # Join the results with a space, similar to the original intent
        f.write(" ".join(transcribed_texts))

    print("Processing complete.")

if __name__ == "__main__":
    main()