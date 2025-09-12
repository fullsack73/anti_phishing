import whisper

model = whisper.load_model("base")
audio = whisper.load_audio("audio.mp3")

# Using word_timestamps=True to get token-level data.
# Note: This requires a recent version of openai-whisper.
result = model.transcribe(audio, language='ko', word_timestamps=True)

with open("result.txt", "w", encoding="utf-8") as f:
    if result.get("segments") and result["segments"] and result["segments"][0].get("words"):
        f.write("Token analysis (word timestamps):\n")
        for segment in result["segments"]:
            for word in segment["words"]:
                start = word['start']
                end = word['end']
                text = word['word']
                f.write(f"[{start:.2f} -> {end:.2f}] {text}\n")
    else:
        f.write("Could not get word-level timestamps. Saving full transcript instead:\n")
        f.write(result.get("text", "Transcription failed."))

print("Processing complete. Results saved to result.txt")
