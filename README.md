🖐️ Gesture + Voice Hybrid Calculator 🎙️📱
This is a real-time gesture-based calculator built with Python, OpenCV, and MediaPipe — designed to make calculations hands-free using intuitive hand gestures and voice responses!
(Also supports parentheses with swag 🤘 sign, undo, clear all, and even power operator! 💥)

💡 Features
✋ Hand Gesture Recognition using MediaPipe

🔢 Right Hand Digits (0-9) via finger count & gestures

➕ Left Hand Operators:

+ → 1 finger

- → 2 fingers

* → 3 fingers

/ → 4 fingers

🤘 Swag Sign (index + pinky up):

Left hand → ( (open bracket)

Right hand → ) (close bracket)

🧠 Smart Expression Validation

🧹 Clear All → Both hands open (all fingers)

🔄 Undo → Thumb + Index + Pinky up (rest down)

💯 Power (Exponent) → Left hand rock sign 🤘

✅ Evaluate → OK Sign (thumb + index close together)

🎙️ Text-to-Speech Output using PowerShell (Windows)

🧠 Result speaking & proper feedback on error

🛠️ Technologies Used
🐍 Python

📸 OpenCV

✋ MediaPipe

🔊 pyttsx3 (Text-to-Speech)

🧠 Regex & Math Expression Evaluation

👋 Gesture Mapping Summary
Hand	Gesture / Fingers	Action
Right	1-5 fingers	Digits 1–5
Right + Left(5)	1-4 fingers (Right)	Digits 6–9
Right	Rock Sign 🤘	Undo (U)
Right	All down, thumb up	0
Right	OK Sign (thumb-index touch)	Evaluate (=)
Left	1 finger	+
Left	2 fingers	-
Left	3 fingers	*
Left	4 fingers	/
Left	Rock Sign 🤘	Power (**)
Left	Swag Sign 🤘	(
Right	Swag Sign 🤘	)
Both Hands	All fingers up	Clear All (C)

🔁 Flow Logic
Detect stable gesture (confirmed across 5 frames)

Debounce using gesture_cooldown (1.2s)

Add to expression if valid

Speak feedback using pyttsx3 or PowerShell

Evaluate on = or handle U, C accordingly

🧠 Expression Validation Logic
✔️ Accepts incomplete but potentially valid expressions like:

2+

5*(3+

❌ Rejects invalid ones:

Consecutive ops like ++, //

Unbalanced ) without matching (

Starts with *, /, +

