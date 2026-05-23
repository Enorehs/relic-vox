# RELIC//VOX 
**Real-Time ASL Gesture Vocoder & Cyberpunk HUD**

RELIC//VOX is a zero-latency computer vision performance instrument with visuals inspired by Cyberpunk. It utilizes a custom Python engine to track hand geometry in 3D space, translating American Sign Language (ASL) into live MIDI arrays. These arrays are routed via a virtual bridge into a Digital Audio Workstation (DAW) to drive a polyphonic synth vocoder in real-time.

Basically: My hands are the MIDI controller.

I have combined my love for music, gaming and development into this <3 

## Tech Stack & Architecture
* **The Brain:** Python 3.12, OpenCV, Google MediaPipe (Hand Landmark & BlazePalm Models)
* **The Bridge:** `mido`, `python-rtmidi`, loopMIDI (Virtual Patch Bay)
* **The Voice:** Waveform (DAW), TAL-Vocoder-2 (Synth Engine)
* **Visuals:** Custom hardcoded OpenCV telemetry HUD

---

## Installation & Environment

*CRITICAL: This engine heavily relies on the legacy Google MediaPipe `solutions` API. You MUST use Python 3.12 and the exact MediaPipe version specified below. Upgrading to Python 3.13+ or newer MediaPipe versions will break the pre-compiled ML binaries.*

### 1. Prerequisites
* **Python 3.12** (Verify by running `py -3.12 --version` in your terminal).
* **Git** (For pulling the repository).

### 2. Clone the Repository
Open your terminal and pull the source code to your local machine:

    git clone https://github.com/Enorehs/relic-vox.git
    cd relic-vox

### 3. Install the Engine Dependencies
Run this exact command to install the ML models, the math libraries, and the MIDI drivers:

    py -3.12 -m pip install mediapipe==0.10.21 mido python-rtmidi opencv-python numpy

### 4. Verify the Engine
To ensure your Python environment compiled everything correctly, launch the tracker (and yes it needs to be either 3.11 or 3.12):

    py -3.12 main.py

*Note: If you have not set up the Virtual MIDI bridge yet, the terminal will instantly throw a `MIDI Error: unknown port 'PythonMIDI 1'`. This is completely normal and means your Python engine is working perfectly. It is just waiting for the audio cables to be plugged in.*

---

## Usage & ASL Chord Dictionary

Once the routing is locked and Waveform is armed, launch the visual tracker in your terminal (`py -3.12 main.py`). Step into the webcam frame. Utilize the following American Sign Language (ASL) signs to trigger specific triad chords in real-time:

* **'C' Sign (Claw):** C Major `[48, 52, 55]`
* **'Y' Sign:** A Minor `[45, 48, 52]`
* **'B' Sign (Flat Palm):** B Major `[47, 51, 54]`
* **'D' Sign (Pointer Up):** D Major `[50, 54, 57]`
* **'I' Sign (Pinky Up):** E Major `[52, 56, 59]`
* **'F' Sign (OK Sign):** F Major `[53, 57, 60]`
* **'L' Sign:** G Major `[55, 59, 62]`

---

<details>
<summary><b>Click here for the Step-by-Step Audio Routing Tutorial</b></summary>

### Phase 1: System Prep
Before Python or the DAW even open, you have to lay down the digital wiring.

* **Open loopMIDI:** Launch the loopMIDI application on your computer.
* **Create the Port:** In the bottom text box, type exactly `PythonMIDI 1` and hit the **+** button. 
* *Result:* Windows now has an invisible MIDI cable waiting to carry data. Leave this app running in the background.

### Phase 2: DAW Prep
Python is broadcasting the data, but now Waveform needs to catch it and synthesize it.

* **Open Waveform:** Open your project.
* **Setup Track 2 (The Data Pipe):**
  * Change the input to `PythonMIDI`.
  * Change the **Destination** from "Default Output" directly to **Track 1**. 
* **Setup Track 1 (The Voice):**
  * Change the input to your Headset Mic (Input 1).
  * Drag and drop the **Compressor** plugin onto the track.
  * Drag and drop the `TAL-Vocoder-2` plugin onto the track, placing it to the right of the Compressor.
* **Arm the Track:** Click the tiny Speaker Icon on Track 1 so it turns green. This lets you hear the live effect in your headphones.

### Phase 3: Performance
Everything is connected. 

1. Double-click the `TAL-Vocoder-2` block to open its interface.
2. Turn up the **Volume** and **Ess** knobs in the Modulator section (whatever settings work for you).
3. Put on your headphones.
4. Step into the camera frame and throw up the signs. 

*Your voice will instantly synthesize.*

Hope this helps and you enjoy it <3

</details>