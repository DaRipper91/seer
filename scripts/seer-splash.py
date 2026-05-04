import sys
import time
import random

# Witchy Gradient Colors
PURPLE = "\033[38;5;129m"
LAVENDER = "\033[38;5;141m"
CYAN = "\033[38;5;51m"
MAGENTA = "\033[38;5;201m"
GOLD = "\033[38;5;220m"
BOLD = "\033[1m"
RESET = "\033[0m"
CLEAR = "\033[2J\033[H"

ART = [
    f"{PURPLE}          .          .          ",
    f"{PURPLE}                .          *    ",
    f"{PURPLE}       *      _/{LAVENDER}\"_{PURPLE}         ",
    f"{PURPLE}             / {GOLD}o . o{PURPLE} \        ",
    f"{PURPLE}     .      (   {CYAN}^{PURPLE}   )       *  ",
    f"{LAVENDER}             )     (      .     ",
    f"{PURPLE}    *       /       \           ",
    f"{PURPLE}           /         \          ",
    f"{PURPLE}          /           \         ",
    f"{PURPLE}         /             \        "
]

def animate_splash():
    # 1. Drawing Animation
    sys.stdout.write(CLEAR)
    for line in ART:
        sys.stdout.write(line + "\n")
        sys.stdout.flush()
        time.sleep(0.03)
    
    # 2. Pulsing Glow for the "Eye"
    glow_frames = [
        f"{MAGENTA}  ✨ The Eye of Automation is Opening... ✨{RESET}",
        f"{PURPLE}  ✨ The Eye of Automation is Opening... ✨{RESET}",
        f"{LAVENDER}  ✨ The Eye of Automation is Opening... ✨{RESET}",
        f"{CYAN}  ✨ The Eye of Automation is Opening... ✨{RESET}",
        f"{GOLD}  ✨ The Eye of Automation is OPEN! ✨{RESET}"
    ]
    
    for frame in glow_frames:
        # Move cursor up one line, clear line, and print frame
        sys.stdout.write("\033[F\033[K" + frame + "\n")
        sys.stdout.flush()
        time.sleep(0.1)

    quotes = [
        "The stars are aligned for automation.",
        "A script in the hand is worth two in the bin.",
        "The cat purrs at your clean code.",
        "Incantations are ready. Focus your intent.",
        "Your SQLite memory is crystalline and sharp."
    ]
    
    omen = f"\n{LAVENDER}💬 Omen: {GOLD}{random.choice(quotes)}{RESET}"
    # Typewriter effect for Omen
    for char in omen:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.01)
    sys.stdout.write("\n\n")

if __name__ == "__main__":
    animate_splash()
