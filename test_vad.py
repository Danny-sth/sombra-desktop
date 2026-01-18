#!/usr/bin/env python3
"""Test Silero VAD with proper state reset."""
import sys
sys.stdout.reconfigure(line_buffering=True)

import numpy as np
import sounddevice as sd
import torch
from silero_vad import load_silero_vad

print("Loading Silero VAD...", flush=True)
model = load_silero_vad()
model.reset_states()  # RESET before use

print("Recording 12 sec. SPEAK then STOP.", flush=True)
print("-" * 50, flush=True)

SAMPLE_RATE = 16000
CHUNK = 512

frame_count = [0]
speech_started = [False]
silence_count = [0]
SILENCE_THRESHOLD = 47  # ~1.5 sec at 32ms/frame

def callback(indata, frames, time_info, status):
    frame_count[0] += 1

    # Convert to float tensor
    audio = indata.flatten().astype(np.float32) / 32768.0
    tensor = torch.from_numpy(audio)

    # Get probability
    with torch.no_grad():
        prob = model(tensor, SAMPLE_RATE).item()

    is_speech = prob > 0.5

    if is_speech:
        if not speech_started[0]:
            print(f">>> SPEECH STARTED (prob={prob:.3f})", flush=True)
        speech_started[0] = True
        silence_count[0] = 0
    elif speech_started[0]:
        silence_count[0] += 1
        if silence_count[0] >= SILENCE_THRESHOLD:
            print(f"\n*** END OF SPEECH ({silence_count[0]} frames silence) ***\n", flush=True)
            speech_started[0] = False
            silence_count[0] = 0
            model.reset_states()

    # Log every 20 frames (~0.6s)
    if frame_count[0] % 20 == 0:
        s = f"prob={prob:.3f}"
        if speech_started[0]:
            s += f" [SPEECH] silence={silence_count[0]}/{SILENCE_THRESHOLD}"
        else:
            s += " [quiet]"
        print(s, flush=True)

try:
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='int16',
                        blocksize=CHUNK, callback=callback):
        sd.sleep(12000)
except KeyboardInterrupt:
    pass

print("-" * 50, flush=True)
print("Done.", flush=True)
