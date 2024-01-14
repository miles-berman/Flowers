import numpy as np

class Synth:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate

    def apply_fade(self, sound, fade_duration):
        fade_length = int(fade_duration * self.sample_rate)
        fade_length = min(fade_length, len(sound) // 2)  # Ensure fade length is not more than half of the sound length

        fade_in = np.linspace(0, 1, fade_length, False)
        fade_out = np.linspace(1, 0, fade_length, False)

        # Apply fade-in
        #sound[:len(fade_in)] *= fade_in

        # Apply fade-out
        sound[-len(fade_out):] *= fade_out

        return sound.astype(np.float32)
        return sound

    def generate_sine_wave(self, freq, duration, fade_duration=0.01):
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        tone = np.sin(freq * t * 2 * np.pi)
        return self.apply_fade(tone, fade_duration)

    def generate_kick_sound(self, duration, fade_duration=0.1):
        start_freq = 150.0
        end_freq = 30.0
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        freq_env = np.logspace(np.log10(start_freq), np.log10(end_freq), t.size)
        kick = np.sin(2 * np.pi * freq_env * t)
        volume_env = np.exp(-3 * t)
        kick *= volume_env
        return self.apply_fade(kick, fade_duration)

    def generate_snare_sound(self, duration, sample_rate=44100, fade_duration=1.01):
        # White noise burst
        noise = np.random.normal(0, 1, int(duration * sample_rate))
        
        # Tone component
        tone_freq = 200  # Frequency for the tone component of the snare
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        tone = np.sin(tone_freq * t * 2 * np.pi)

        snare = noise * 0.5 + tone * 0.5
        volume_env = np.exp(-10 * t)
        snare *= volume_env
        return self.apply_fade(snare, fade_duration)

    def generate_hihat_sound(self, duration, sample_rate=44100, fade_duration=0.01):
        # White noise
        noise = np.random.normal(0, 1, int(duration * sample_rate))
        volume_env = np.exp(-30 * np.linspace(0, duration, int(duration * sample_rate), False))
        hihat = noise * volume_env 
        return self.apply_fade(hihat, fade_duration)


    def generate_bass_note(self, freq, duration, fade_duration=0.01):
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        wave = np.sin(freq * t * 2 * np.pi)
        volume_env = np.linspace(1, 0, wave.size)
        return self.apply_fade(wave * volume_env, fade_duration)

    def generate_chord(self, frequencies, duration, fade_duration=0.01):
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        chord = sum(np.sin(f * t * 2 * np.pi) for f in frequencies) / len(frequencies)
        return self.apply_fade(chord, fade_duration)

        