# Air Canvas with OpenCV & MediaPipe

A real-time virtual drawing application controlled by hand gestures. This project uses computer vision to track the user's fingertip, allowing them to draw on the screen without any physical hardware other than a webcam.

Built with Python, OpenCV, and MediaPipe.

![Air Canvas Demo](demo.gif)

## Features

- 🖐️ **Hand Tracking**: Real-time finger detection using MediaPipe
- 🎨 **Drawing Tools**: 
  - Freehand drawing
  - Line tool
  - Rectangle tool
  - Circle tool
  - Eraser (activated by fist gesture or selection)
- 🪣 **Flood Fill**: Fill closed shapes with color
- 🎨 **Color Palette**: 10 colors including Purple, Blue, Green, Red, Yellow, Cyan, Orange, White, Pink, and Lime
- ↩️ **Undo/Redo**: Stack-based history (up to 20 steps)
- 💾 **Save Function**: Export your artwork as a PNG file
- 🖱️ **Smart UI**: Prevents accidental drawing over toolbars and buttons
- 🎚️ **Brush Size Control**: Adjust brush thickness on the fly

## Requirements

- Python (MediaPipe has limited support for Python 3.12+)
- opencv-python
- mediapipe
- numpy

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/furkanertal/air-canvas.git
cd air-canvas
```

2. **Install the required libraries:**
```bash
pip install opencv-python mediapipe numpy
```

3. **Run the application:**
```bash
python main.py
```

## Controls & Usage

The application distinguishes between **Drawing Mode** and **Selection/Pause Mode** based on your hand gesture.

### Hand Gestures

| Gesture | Action |
|---------|--------|
| ☝️ **Index Finger Up** | **Draw / Use Tool**: Moves the cursor. If in the drawing area, it draws. If over a menu, it selects the item. |
| ✌️ **Index + Middle Fingers Up** | **Pause / Confirm**: Stops drawing. Used to move the cursor without leaving a trail, confirm a shape (Line/Rect/Circle), or trigger the Fill tool. |
| ✊ **Fist (All Fingers Closed)** | **Eraser Mode**: Automatically activates the eraser with larger brush size. |

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `q` | Quit application |
| `c` | Clear canvas |
| `s` | Save drawing to disk |
| `u` | Undo last action |
| `r` | Redo last action |
| `+` / `=` | Increase brush size |
| `-` / `_` | Decrease brush size |
| `SPACE` | Toggle drawing mode ON/OFF |
| `1-6` | Quick tool selection (Draw/Eraser/Line/Rectangle/Circle/Fill) |

## User Interface

### Top Bar - Color Palette
Click on any color in the top bar to select it. The current color is highlighted with a green border.

### Left Sidebar - Tool Selection
- ✏️ **Draw**: Freehand drawing
- 🧹 **Eraser**: Remove parts of your drawing
- **/** **Line**: Draw straight lines (two-point)
- **▭** **Rectangle**: Draw rectangles (two-point)
- **○** **Circle**: Draw circles (center + radius)
- 🪣 **Fill**: Flood fill closed areas

### Bottom Status Bar
Displays current mode, active tool, and selected color.

## How It Works

1. **Detection**: The webcam captures the video feed, and MediaPipe processes the frame to find hand landmarks (21 points per hand).

2. **Finger Tracking**: 
   - The application tracks specific landmarks: Index finger tip (point 8) and Middle finger tip (point 12).
   - Finger position is determined by comparing tip positions with knuckle positions.

3. **Mode Logic**: 
   - **Drawing Mode**: Only index finger extended
   - **Selection/Pause Mode**: Both index and middle fingers extended
   - **Eraser Mode**: Fist gesture (all fingers closed)

4. **Rendering Pipeline**:
   - Drawing is created on a separate black "Canvas" layer (`img_canvas`)
   - The video feed is processed to overlay this canvas onto the real-time camera feed
   - Uses bitwise operations and masking for seamless blending

5. **Shape Handling**: 
   - Shapes (Line, Rectangle, Circle) are previewed on the screen in real-time
   - Only committed to the canvas when user switches to "Pause Mode" (two fingers up)
   - This prevents accidental partial shapes

6. **Undo/Redo System**: 
   - Canvas states are saved in a stack after each significant action
   - Maximum history of 20 states to prevent memory issues

## Project Structure
```
air-canvas/
│
├── main.py              # Main application file
├── README.md            # This file
├── requirements.txt     # Python dependencies
└── examples/            # Example drawings (optional)
```

## Troubleshooting

### Camera Not Working
- Ensure your webcam is properly connected
- Check if another application is using the camera
- Try changing `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)` if you have multiple cameras

### Hand Not Detected
- Ensure good lighting conditions
- Keep your hand within the camera frame
- Adjust `min_detection_confidence` in the code (default: 0.7)

### Performance Issues
- Reduce camera resolution in the code
- Close other resource-intensive applications
- Ensure your system meets the minimum requirements

## Future Enhancements

- [ ] Text tool for adding labels
- [ ] Multiple layers support
- [ ] More shape options (polygon, star, etc.)
- [ ] Gradient and pattern fills
- [ ] Export to different formats (SVG, PDF)
- [ ] Two-hand gesture support
- [ ] Drawing smoothing algorithms

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is open source and available under the [MIT License](LICENSE).



⭐ If you found this project helpful, please consider giving it a star!
