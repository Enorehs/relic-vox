import cv2
import mediapipe as mp
import mido
import math
import random
import time
import numpy as np

#MIDI setup
try:
    midi_out = mido.open_output('PythonMIDI 1')
    print("SYS.LOG: MIDI Bridge Connected.")
except Exception as e:
    print(f"MIDI Error: {e}\nEnsure LoopMIDI is running and 'PythonMIDI 1' exists.")
    exit()

#MediaPipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.75, min_tracking_confidence=0.75)

#chords
CHORDS = {
    'A_Minor': [45, 48, 52], # Y Sign
    'B_Major': [47, 51, 54], # B Sign (Flat Palm)
    'C_Major': [48, 52, 55], # C Sign (Claw)
    'D_Major': [50, 54, 57], # D Sign (Pointer Up)
    'E_Major': [52, 56, 59], # I Sign (Pinky Up)
    'F_Major': [53, 57, 60], # F Sign (OK Sign)
    'G_Major': [55, 59, 62], # L Sign
}

current_chord_name = None
current_notes = []

def send_midi_chord(chord_notes):
    for note in chord_notes:
        midi_out.send(mido.Message('note_on', note=note, velocity=100))

def stop_midi_chord(chord_notes):
    for note in chord_notes:
        midi_out.send(mido.Message('note_off', note=note, velocity=0))

#HUD colours (ref to cyberpunk)
CYBER_YELLOW = (0, 220, 255)
CYBER_CYAN = (255, 255, 0)
CYBER_RED = (0, 0, 255)
BLACK = (0, 0, 0)

#neon glow text effect
def draw_neon_text(img, text, pos, color, scale=0.5, thickness=1):
    #faux glow effect
    dark_glow = (int(color[0]*0.4), int(color[1]*0.4), int(color[2]*0.4))
    cv2.putText(img, text, pos, cv2.FONT_HERSHEY_SIMPLEX, scale, dark_glow, thickness+2)
    cv2.putText(img, text, pos, cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness)

#frame
def draw_dented_frame(img, color):
    h, w = img.shape[:2]
    thick = 2
    margin = 15
    #main rectangle
    cv2.rectangle(img, (margin, margin), (w-margin, h-margin), color, thick)
    #tactical "dents" (small geometric cutouts/additions)
    cv2.line(img, (margin, 100), (margin+10, 100), color, thick)
    cv2.line(img, (margin+10, 100), (margin+10, 150), color, thick)
    cv2.line(img, (margin+10, 150), (margin, 150), color, thick)
    
    cv2.line(img, (w-margin, h-200), (w-margin-10, h-200), color, thick)
    cv2.line(img, (w-margin-10, h-200), (w-margin-10, h-150), color, thick)
    cv2.line(img, (w-margin-10, h-150), (w-margin, h-150), color, thick)

#main video loop
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

while cap.isOpened():
    success, frame = cap.read()
    if not success: continue

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    detected_chord = None
    hand_bbox = None
    system_state = "SEARCHING"

    if results.multi_hand_landmarks:
        hand = results.multi_hand_landmarks[0].landmark
        
        #finger states (the math part)
        index_open = hand[8].y < hand[6].y
        middle_open = hand[12].y < hand[10].y
        ring_open = hand[16].y < hand[14].y
        pinky_open = hand[20].y < hand[18].y
        thumb_open = hand[4].x < hand[3].x # Right hand logic
        
        #distances for complex signs
        thumb_index_dist = math.sqrt((hand[4].x - hand[8].x)**2 + (hand[4].y - hand[8].y)**2)
        wrist_to_middle = math.sqrt((hand[0].x - hand[12].x)**2 + (hand[0].y - hand[12].y)**2)

        #ASL classifier
        if thumb_open and pinky_open and not index_open and not middle_open and not ring_open:
            detected_chord = 'A_Minor' # Y Sign
        elif index_open and middle_open and ring_open and pinky_open and wrist_to_middle > 0.4:
            detected_chord = 'B_Major' # B Sign (Flat Palm)
        elif index_open and middle_open and ring_open and pinky_open and wrist_to_middle < 0.35:
            detected_chord = 'C_Major' # C Sign (Clawed/Curved)
        elif index_open and not middle_open and not ring_open and not pinky_open and not thumb_open:
            detected_chord = 'D_Major' # D Sign
        elif pinky_open and not index_open and not middle_open and not ring_open and not thumb_open:
            detected_chord = 'E_Major' # I Sign
        elif thumb_index_dist < 0.05 and middle_open and ring_open and pinky_open:
            detected_chord = 'F_Major' # F Sign (OK Sign)
        elif thumb_open and index_open and not middle_open and not ring_open and not pinky_open:
            detected_chord = 'G_Major' # L Sign
        elif not index_open and not middle_open and not ring_open and not pinky_open:
            detected_chord = 'MUTED' # Fist

        #set system state
        if detected_chord == 'MUTED':
            system_state = "MUTED"
        elif detected_chord:
            system_state = "ACTIVE"
            
        #box for the hand
        x_min, y_min = w, h
        x_max, y_max = 0, 0
        for lm in hand:
            x, y = int(lm.x * w), int(lm.y * h)
            x_min, y_min = min(x_min, x), min(y_min, y)
            x_max, y_max = max(x_max, x), max(y_max, y)
        hand_bbox = (x_min - 20, y_min - 20, x_max + 20, y_max + 20)

    #MIDI trigger logic
    if detected_chord != current_chord_name:
        if current_notes: 
            stop_midi_chord(current_notes)
        
        if detected_chord and detected_chord != 'MUTED':
            current_notes = CHORDS[detected_chord]
            send_midi_chord(current_notes)
        else:
            current_notes = []
            
        current_chord_name = detected_chord

    #rendering the HUD 
      
    #colours and themes based on state
    if system_state == "ACTIVE":
        ui_color = CYBER_CYAN
        head_color = CYBER_YELLOW
        box_color = CYBER_YELLOW
        top_txt = CYBER_YELLOW
        bot_txt = CYBER_CYAN
        lat_val = f"{random.randint(10, 14)}ms"
        status = ["STABLE", "DETECTED", "ACTIVE", "SYNCHRONIZED", "STABLE", "ONLINE"]
    elif system_state == "MUTED":
        ui_color = CYBER_RED
        head_color = CYBER_RED
        box_color = CYBER_RED
        top_txt = CYBER_RED
        bot_txt = CYBER_RED
        lat_val = "ERR_TIMEOUT"
        status = ["SEVERED", "MUTED", "STANDBY", "DE-SYNCED", "PURGED", "OFFLINE"]
    else: #searching
        ui_color = CYBER_CYAN
        head_color = CYBER_YELLOW
        box_color = CYBER_CYAN
        top_txt = CYBER_CYAN
        bot_txt = CYBER_CYAN
        lat_val = "---"
        status = ["SEARCHING...", "LOST", "OFFLINE", "AWAITING INPUT", "EMPTY", "STANDBY"]

    #dented frame
    draw_dented_frame(frame, ui_color)

    #solid header bar
    cv2.rectangle(frame, (0, 0), (w, 40), head_color, -1)
    text_size = cv2.getTextSize("VOICE RECONSTRUCTION SYSTEM — RELIC//VOX v2.7", cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
    cv2.putText(frame, "VOICE RECONSTRUCTION SYSTEM — RELIC//VOX v2.7", ((w - text_size[0]) // 2, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, BLACK, 2)

    #top left data
    draw_neon_text(frame, f"NEURAL LINK: {status[0]}", (30, 80), top_txt)
    draw_neon_text(frame, f"BIO-SIGNAL: {status[1]}", (30, 105), top_txt)
    draw_neon_text(frame, f"HANDTRACK: {status[2]}", (30, 130), top_txt)

    #bottom right data
    draw_neon_text(frame, f"VOICEPRINT: {status[3]}", (w - 320, h - 120), bot_txt)
    draw_neon_text(frame, f"AUDIO BUFFER: {status[4]}", (w - 320, h - 95), bot_txt)
    draw_neon_text(frame, f"FORMANT MATRIX: {status[5]}", (w - 320, h - 70), bot_txt)
    draw_neon_text(frame, f"LATENCY: {lat_val}", (w - 320, h - 45), bot_txt)

    #hand tracking box and label
    if system_state != "SEARCHING" and hand_bbox:
        hx1, hy1, hx2, hy2 = hand_bbox
        #draw box
        cv2.rectangle(frame, (hx1, hy1), (hx2, hy2), box_color, 2)
        #draw label above box
        if system_state == "ACTIVE":
            label = f">> {current_chord_name.upper()} <<"
        else:
            label = "GATE_CLOSED"
        
        #center label above box
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
        label_x = hx1 + ((hx2 - hx1) - label_size[0]) // 2
        draw_neon_text(frame, label, (label_x, hy1 - 15), box_color, 0.7, 2)

    cv2.imshow('RELIC//VOX Interface', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

#finishing
if current_notes: stop_midi_chord(current_notes)
cap.release()
cv2.destroyAllWindows()