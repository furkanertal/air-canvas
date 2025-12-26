Air Canvas with OpenCV \& MediaPipe



A real-time virtual drawing application controlled by hand gestures. This project uses computer vision to track the user's fingertip, allowing them to draw on the screen without any physical hardware other than a webcam.



Built with Python, OpenCV, and MediaPipe.

Features



&nbsp;   Hand Tracking: Real-time finger detection using MediaPipe.



&nbsp;   Drawing Tools: Freehand drawing, Line, Rectangle, Circle, and Eraser.



&nbsp;   Flood Fill: Fill closed shapes with color (includes a cooldown to prevent lag).



&nbsp;   Color Selection: multiple color options available in the UI.



&nbsp;   Undo/Redo: Stack-based history to undo or redo actions.



&nbsp;   Save Function: Save your artwork as a .png file.



&nbsp;   Smart UI: Prevents accidental drawing over toolbars and buttons.



Requirements



&nbsp;   Python 3.x



&nbsp;   opencv-python



&nbsp;   mediapipe



&nbsp;   numpy



Installation



&nbsp;   Clone the repository:

&nbsp;   Bash



git clone https://github.com/yourusername/air-canvas.git

cd air-canvas



Install the required libraries:

Bash



pip install opencv-python mediapipe numpy



Run the application:

Bash



&nbsp;   python main.py



Controls \& Usage



The application distinguishes between Drawing Mode and Selection/Pause Mode based on your hand gesture.

Hand Gestures

Gesture	Action

Index Finger Up	Draw / Use Tool: Moves the cursor. If in the drawing area, it draws. If over a menu, it selects the item.

Index + Middle Fingers Up	Pause / Confirm: Stops drawing. Used to move the cursor without leaving a trail, confirm a shape (Line/Rect/Circle), or trigger the Fill tool.

Keyboard Shortcuts

Key	Action

q	Quit application

c	Clear canvas

s	Save drawing to disk

u	Undo last action

r	Redo last action

How it Works



&nbsp;   Detection: The webcam captures the video feed, and MediaPipe processes the frame to find hand landmarks.



&nbsp;   Logic: The distance between the index and middle finger tips determines the mode (Drawing vs. Selection).



&nbsp;   Rendering:



&nbsp;       The drawing is created on a separate black "Canvas" layer (img\_canvas).



&nbsp;       The video feed is processed to overlay this canvas onto the real-time camera feed using bitwise operations and masking.



&nbsp;   Shape Handling: Shapes are previewed on the screen but only committed to the canvas when the user switches to "Selection/Pause Mode" (lifts two fingers).



License



This project is open source and available under the MIT License.

