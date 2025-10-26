# oo_adventure 
# Project Introduction
oo_adventure is a rhythm-based platformer game where you control the character by opening your mouth in front of a webcam. The background music is David Tao's "Find Yourself", and a bubble pop sound plays when you jump.

## Demo Video
[Watch gameplay demo on YouTube](https://youtu.be/DLdJlzucmjM)

## Screenshots
![](screenshot1.JPG)
![](screenshot2.JPG)

# File Structure
```
oo_adventure/
├── game.py                  # Main game file (webcam mouth control, rhythm platformer)
├── find_yourself.mp3        # Background music (download, see below)
├── bubblepop-254773.mp3     # Jump sound effect (download, see below)
├── requirements.txt         # Python dependencies
├── install_requirements.sh  # One-click install script
└── README.md                # Project documentation
```

# Resource Download
- David Tao "Find Yourself" MP3: [Google Drive Link](https://drive.google.com/file/d/1QlHNg6zMcciLXTHnjFBFHlAVqkRuMQY9/view?usp=drive_link)
  - After downloading, rename to `find_yourself.mp3` and place in the project root
- Jump sound effect MP3: [Google Drive Link](https://drive.google.com/file/d/10qPV0qKGVayyi0aazKi6OAu1jF7b_7cJ/view?usp=drive_link)
  - After downloading, rename to `bubblepop-254773.mp3` and place in the project root

# Installation & Run
1. Install dependencies
   - Recommended: `pip install -r requirements.txt`
   - Or run `./install_requirements.sh`
2. Make sure resource files are placed (see download section above)
3. Run the game
   ```bash
   python game.py
   ```

# How to Play
- Face the webcam and open your mouth to jump
- Platforms are generated according to the music rhythm, gaps appear on beats
- Bubble pop sound plays when jumping
- UI shows distance, beat progress, and controls
- Press R to restart, ESC to exit

# Tech Stack
- Python 3.8+
- Pygame
- OpenCV
- MediaPipe
- Librosa
- NumPy

# Dependencies (requirements.txt)
```
pygame>=2.5.0
opencv-python>=4.8.0
mediapipe>=0.10.0
numpy>=1.24.0
```

# FAQ
- Webcam not working: Check permissions or device
- No music/sound: Make sure filenames and paths are correct
- Face detection not sensitive: Ensure good lighting, keep face centered

# License
- Game code: MIT License
- Music copyright belongs to the original author, for learning and entertainment only