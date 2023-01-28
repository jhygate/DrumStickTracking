import subprocess
import matplotlib.pyplot as plt
import numpy as np
import wave
import scipy.signal
import sys

def extract_audio(video_path, audio_path):
    command = ['ffmpeg', '-i', video_path, '-vn', '-ac', '1', '-ar', '16000','-y', '-acodec', 'pcm_s16le', audio_path]
    subprocess.run(command)


def audio_hit_frames(video_path):
    extract_audio(video_path, 'Videos/temp.wav')
    spf = wave.open("Videos/temp.wav", "r")

    # Extract Raw Audio from Wav File
    signal = spf.readframes(-1)
    signal = np.fromstring(signal, np.int16)
    peaks = scipy.signal.find_peaks(signal,height=5000,distance=5000)[0]

    SAMPLE_RATE = spf.getframerate()
    rateConversion = SAMPLE_RATE/30

    peaks = [int(round(peak/rateConversion,0)) for peak in peaks]
    return peaks





extract_audio("Videos/Above60BPM.MOV","Videos/Above60BPM.wav")


spf = wave.open("Videos/Above60BPM.wav", "r")

# Extract Raw Audio from Wav File
signal = spf.readframes(-1)
signal = np.fromstring(signal, np.int16)


# If Stereo
if spf.getnchannels() == 2:
    print("Just mono files")
    sys.exit(0)

plt.figure(1)
plt.title("Signal Wave...")
plt.plot(signal)
print(signal)
print(len(signal))
peaks = scipy.signal.find_peaks(signal,height=5000,distance=5000)[0]
print(len(peaks))

plt.plot(peaks,[1000 for i in peaks], marker="o", ls="", ms=3 )

print(peaks)
plt.show()

# from scipy.fft import fft, fftfreq
# SAMPLE_RATE = spf.getframerate()
# N = spf.getnframes()

# yf = fft(signal)
# xf = fftfreq(N, 1 / SAMPLE_RATE)

# plt.plot(xf, np.abs(yf))
# plt.show()