import numpy as np
import random
import time
import threading

import sounddevice as sd

from matrix import Pixel
from synth import Synth



class RealTimeSoundManager:
    def __init__(self, synth, bpm=120, beats_per_bar=8, subdivisions=4, channels=2):

        self.synth = synth

        self.bpm = bpm
        self.beats_per_bar = beats_per_bar
        self.subdivisions = subdivisions

        self.is_playing = False
        self.current_beat = 0
        self.total_bars_played = 0
        self.channels = channels
        self.stream = sd.OutputStream(samplerate=synth.sample_rate, channels=channels)
        self.stream.start()

        self.buffer_length = int(synth.sample_rate * 60 / bpm * beats_per_bar / subdivisions)
        self.current_buffer = np.zeros((self.buffer_length, channels), dtype=np.float32)
        self.sound_queue = []  # Queue to hold scheduled sounds
        self.current_bar = 0

        self.trigger_callback = self.trigger_callback

        self.visuals = Pixel('data/Matrix_Data.txt', True)

    def trigger_callback(self):
        thread = threading.Thread(target=self.visuals.refresh())
        thread.start()
        

    def start(self):
        self.is_playing = True
        threading.Thread(target=self._run).start()

    def stop(self):
        self.is_playing = False
        self.stream.stop()

    def add_sound_to_queue(self, sound, start_beat, duration_beats, is_trigger=False):
        self.sound_queue.append({
            "sound": sound,
            "start_beat": start_beat,
            "duration_beats": duration_beats,
            "played": False,
            "is_trigger": is_trigger
        })

    def _run(self):
        interval = 60.0 / (self.bpm * self.subdivisions)
        while self.is_playing:
            self.total_bars_played += 1 / self.subdivisions
            self.current_bar = self.current_beat // self.beats_per_bar
            if self.current_beat%4 == 0:
                print("[-]",self.current_beat)
            else:
                print("[]",self.current_beat)

            start_time = time.time()

            # Happy music scne
            if self.current_bar > 3:
                self.scene1()
            else:
                print(self.current_bar)
                print("X")
                self.scene2()
            #  Mix and write to buffer
            self._process_and_mix_sounds()
            self.stream.write(self.current_buffer)

            # Move to the next beat and handle buffer shifting
            self.current_beat = (self.current_beat + 1) % (self.beats_per_bar * self.subdivisions)
            if self.current_beat == 0:
                self.total_bars_played += 1 
            self._shift_buffer()

            time.sleep(max(0, start_time + interval - time.time()))

    def _process_and_mix_sounds(self):
        # Iterate over sound queue and mix sounds for the current beat
        for sound_info in self.sound_queue:
            if self.current_beat == sound_info["start_beat"] and not sound_info["played"]:
                self._mix_to_buffer(sound_info["sound"])
                sound_info["played"] = True
                if sound_info["is_trigger"] and self.trigger_callback:
                    self.trigger_callback() 

    def _mix_to_buffer(self, sound):
        # Ensure the sound is in stereo format (2 channels)
        if sound.ndim == 1:  # Mono sound
            sound = np.tile(sound[:, np.newaxis], (1, self.channels))

        # Mix the new sound into the current buffer
        mix_length = min(len(sound), len(self.current_buffer))
        self.current_buffer[:mix_length] += sound[:mix_length]


    def _shift_buffer(self):
        # Shift the buffer to remove played sound and make room for new sound
        shift_amount = self.buffer_length
        self.current_buffer = np.roll(self.current_buffer, -shift_amount, axis=0)
        self.current_buffer[-shift_amount:] = 0


    def _add_sounds_continuously(self):
        # Calculate the current bar based on the current beat
        current_bar = self.current_beat // self.beats_per_bar
        self.scene1(current_bar)



#---------------
# Scenes
#---------------

    def scene1(self):
        current_bar = self.current_bar
        # Kick sound on every beat
        if self.current_beat % self.beats_per_bar == 0:
            self.add_sound_to_queue(self.synth.generate_kick_sound(0.5), self.current_beat, 1)

        # Snare on the off beat (2nd and 4th beat of a bar)
        if self.current_beat % self.beats_per_bar in [1, 3]:
            self.add_sound_to_queue(self.synth.generate_snare_sound(0.5), self.current_beat, 1, True)

        # Chord progression
        chords = [
            [261.63, 329.63, 392.00],  # C major
            [293.66, 349.23, 440.00],  # D major
            [329.63, 415.30, 493.88],  # E major
            [349.23, 440.00, 523.25]   # F major
        ]
        chord = chords[current_bar % len(chords)]
        if self.current_beat % self.beats_per_bar == 0:
            self.add_sound_to_queue(self.synth.generate_chord(chord, 1.0), self.current_beat, self.beats_per_bar, True)

        # Bass note based on the chord progression
        bass_note = chord[0] / 2
        self.add_sound_to_queue(self.synth.generate_bass_note(bass_note, 0.5), self.current_beat, 1)

        # Random melody using chord notes
        if random.random() < 0.5:
            melody_note = random.choice(chord)
            self.add_sound_to_queue(self.synth.generate_sine_wave(melody_note, 0.5), self.current_beat, 1, True)


    def scene2(self):
        current_bar = self.current_bar

        # Swing factor (0 for no swing, up to 0.5 for maximum swing)
        swing_factor = 0.2

        # Soft kick sound on the first beat of every bar
        if self.current_beat % self.beats_per_bar == 0:
            self.add_sound_to_queue(self.synth.generate_kick_sound(0.3), self.current_beat, 1)

        # Soft snare on the 2nd and 4th beat of a bar with swing
        if self.current_beat % self.beats_per_bar in [1, 3]:
            snare_start_beat = self.current_beat + swing_factor if self.current_beat % 2 == 0 else self.current_beat
            #self.add_sound_to_queue(self.synth.generate_snare_sound(0.3), snare_start_beat, 1)

        # Faster hi-hats: Trigger on every subdivision, potentially with swing
        for subdivision in range(self.subdivisions*self.beats_per_bar):
            hi_hat_start_beat = subdivision

            self.add_sound_to_queue(self.synth.generate_hihat_sound(0.2) * 0.2, hi_hat_start_beat, 1)
        

        # Ambient chord progression
        chords = [
            [261.63, 329.63, 392.00, 523.25],  # C major 7th
            [220.00, 261.63, 329.63, 392.00],  # A minor 7th
            [329.63, 415.30, 493.88, 659.26],  # E major 7th
            [349.23, 440.00, 523.25, 698.46],  # F major 7th
            [392.00, 493.88, 587.33, 739.99],  # G major 7th
        ]
        chord = chords[current_bar % len(chords)]
        if self.current_beat % self.beats_per_bar == 0:
            self.add_sound_to_queue(self.synth.generate_chord(chord, 0.8), self.current_beat, self.beats_per_bar, True)

        # Soft bass note based on the chord progression with swing
        bass_note = chord[0] / 2
        if self.current_beat % 2 == 0:  # Play bass note on alternate beats with swing
            bass_start_beat = self.current_beat + swing_factor
            self.add_sound_to_queue(self.synth.generate_bass_note(bass_note, 0.3), bass_start_beat, 1)

        pentatonic_scale = [chord[0], chord[1], chord[2], chord[0]*2, chord[1]*2]
        if random.random() < 0.3:  # Less frequent melody notes
            melody_note = random.choice(pentatonic_scale)
            self.add_sound_to_queue(self.synth.generate_sine_wave(melody_note, 0.5), self.current_beat, 1, True)

        if self.total_bars_played % 4 == 0: 
            pentatonic_scale = [chord[0]*4, chord[1]*4, chord[2]*4, chord[0]*4, chord[1]*4]
            if random.random() < 0.8:  # Less frequent melody notes
                melody_note = random.choice(pentatonic_scale)
                self.add_sound_to_queue(self.synth.generate_sine_wave(melody_note, 0.5)*0.3, self.current_beat, 1, True)
        else:

            if self.current_beat % self.beats_per_bar == 0:
                if random.random() < 0.6:

                    snare_start_beat = self.current_beat + swing_factor if self.current_beat % 2 == 0 else self.current_beat
                    self.add_sound_to_queue(self.synth.generate_snare_sound(0.3)*1.4, snare_start_beat, 1, False)

            

    def create_varied_melody(self):

        # Define a set of notes (C Major scale in a higher octave)
        scale_notes = [523.25, 587.33, 659.26, 698.46, 783.99, 880.00, 987.77]
        
        # Create a pattern of 8 notes with some variation
        melody = [random.choice(scale_notes) for _ in range(8)]
        
        # Introduce some rhythmic and melodic variation
        for i in range(2, len(melody), 2):
            melody[i] = melody[i-1] * 1.05946  # Slightly increase the frequency (move one semitone up)

        return melody


# Example usage
# Constants
bpm = 160 / 2
beats_per_bar = 8
bars = 4
subdivisions = 16# For hi-hat on off-beats

# Initialize Synth and Sound Manager
synth = Synth()
sound_manager = RealTimeSoundManager(synth, bpm, beats_per_bar, subdivisions)
sound_manager.start()




 
