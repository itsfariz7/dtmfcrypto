import numpy as np
import wave
import matplotlib.pyplot as plt

DTMF_FREQS = {
    '1': (20697, 21209),
    '2': (20697, 21336),
    '3': (20697, 21477),
    '4': (20770, 21209),
    '5': (20770, 21336),
    '6': (20770, 21477),
    '7': (20852, 21209),
    '8': (20852, 21336),
    '9': (20852, 21477),
    '0': (20941, 21336),
    '*': (20941, 21209),
    '#': (20941, 21477)
}

# --------------------------------------------------------------------------------


def decode_dtmf(sig, Fs, window=0.05, ofset=10):
    # Initialize empty list to store the decoded keys and frequencies found
    keys = []
    found_freqs = []

    # Iterate through the signal in window-sized chunks
    for i in range(0, len(sig), int(Fs*window)):
        # Get the current chunk of the signal
        cut_sig = sig[i:i+int(Fs*window)]

        # Take the Fast Fourier Transform (FFT) of the current chunk
        fft_sig = np.fft.fft(cut_sig, Fs)

        # Take the absolute value of the FFT
        fft_sig = np.abs(fft_sig)

        # Set the first 500 elements of the FFT to 0 (removes DC component)
        fft_sig[:500] = 0

        # Only keep the first half of the FFT (removes negative frequencies)
        fft_sig = fft_sig[:int(len(fft_sig)/2)]

        # Set the lower bound to be 75% of the maximum value in the FFT
        lower_bound = 0.75 * np.max(fft_sig)

        # Initialize empty list to store the frequencies that pass the lower bound threshold
        filtered_freqs = []

        # Iterate through the FFT and store the indices of the frequencies that pass the lower bound threshold
        for i, mag in enumerate(fft_sig):
            if mag > lower_bound:
                filtered_freqs.append(i)

        # Iterate through the DTMF frequencies and check if any of the filtered frequencies fall within the expected range
        for char, frequency_pair in DTMF_FREQS.items():
            high_freq_range = range(
                frequency_pair[0] - ofset, frequency_pair[0] + ofset + 1)
            low_freq_range = range(
                frequency_pair[1] - ofset, frequency_pair[1] + ofset + 1)
            if any(freq in high_freq_range for freq in filtered_freqs) and any(freq in low_freq_range for freq in filtered_freqs):
                # If a match is found, append the key and frequency pair to the lists
                keys.append(char)
                found_freqs.append(frequency_pair)
    # Return the decoded keys and found frequencies
    return keys, found_freqs

# --------------------------------------------------------------------------------


def synthesize_DTMF(phone_number, duration, silence_duration, Fs):
    # Set the amplitude (A) of the sine waves
    A = 0.5
    # Create an empty list to store the DTMF tones
    DTMF = []
    # Iterate over the list of digits
    for digit in phone_number:
        # Get the frequencies for the digit
        f1, f2 = DTMF_FREQS[digit]

        # Generate the sine waves for the frequencies
        sine1 = A * np.sin(2 * np.pi * f1 * np.linspace(0,
                           duration, int(duration * Fs), False))
        sine2 = A * np.sin(2 * np.pi * f2 * np.linspace(0,
                           duration, int(duration * Fs), False))

        # Add the sine waves together to create the DTMF tone
        DTMF_tone = sine1 + sine2

        # Add the DTMF tone to the list
        DTMF.extend(DTMF_tone)

        # Add a period of silence to the list
        silence = np.zeros(int(silence_duration * Fs))
        DTMF.extend(silence)

    # Convert the DTMF signal to a 16-bit integer representation
    DTMF = np.int16(DTMF / np.max(np.abs(DTMF)) * 32767)

    # Open a wave file for writing
    with wave.open("phone_number.wav", "w") as file:
        # Set the parameters of the wave file
        file.setparams((1, 2, Fs, 0, "NONE", "not compressed"))

        # Write the DTMF signal to the wave file
        file.writeframes(DTMF)

# --------------------------------------------------------------------------------


def analyze_audio(filename):
    # Open the audio file

    wave_file = wave.open(filename, 'r')
    num_samples = wave_file.getnframes()
    Fs = wave_file.getframerate()
    data = wave_file.readframes(num_samples)

    sample_width = wave_file.getsampwidth()

    if sample_width == 1:
        data = data = np.frombuffer(data, dtype=np.uint8)
    elif sample_width == 2:
        data = data = np.frombuffer(data, dtype=np.int16)

    wave_file.close()

    # Decode the DTMF tones
    keys, found_freqs = decode_dtmf(data, Fs, duration + silence_duration)

    # Print the detected digits
    print(keys)

    # Plot the waveform in the time domain
    plt.figure()
    plt.plot(data)
    plt.xlabel('Sample index')
    plt.ylabel('Amplitude')
    plt.title('Waveform in the time domain')

    # Plot the detected DTMF frequencies in the time domain
    plt.figure()
    for f1, f2 in found_freqs:
        plt.stem([f1, f2], [1, 1], 'k')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude')
    plt.title('Detected DTMF frequencies in the time domain')

    # Calculate the frequency spectrum
    spectrum = np.abs(np.fft.fft(data))
    freqs = np.fft.fftfreq(len(data), 1/Fs)

    # Plot the frequency spectrum
    plt.figure()
    plt.plot(freqs, spectrum)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.title('Frequency spectrum')

    # Plot the detected DTMF frequencies in the frequency domain
    plt.figure()
    for f1, f2 in found_freqs:
        idx1 = np.argmin(np.abs(freqs - f1))
        idx2 = np.argmin(np.abs(freqs - f2))
        plt.stem([freqs[idx1], freqs[idx2]], [
                 spectrum[idx1], spectrum[idx2]], 'k')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.title('Detected DTMF frequencies in the frequency domain')

    # Show the plots
    plt.show()
# --------------------------------------------------------------------------------

# region main


# Define your phone number as a string of digits
phone_number = "34356154378"

# Set the sampling frequency (Fs) in Hz
Fs = 441000

# Set the duration of each DTMF tone in seconds
duration = 0.25

# Set the duration of silence between tones in seconds
silence_duration = 0.25

# Synthesize the DTMF signal
synthesize_DTMF(phone_number, duration, silence_duration, Fs)

# Analyze the synthesized audio file
analyze_audio("phone_number.wav")
analyze_audio("Ornek.wav")

# endregion