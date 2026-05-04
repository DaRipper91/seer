import sys

# ANSI Colors for that Flashy Purple Witchy Vibe
PURPLE = "\033[95m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Handcrafted Witch Cat Art
ART = f"""
{PURPLE}               .
              / \\
             /   \\
            /_____\\
           /       \\
          /  {YELLOW}^   ^{PURPLE}  \\
         /  {YELLOW}(o) (o){PURPLE}  \\
         \\     {CYAN}V{PURPLE}     /
          \\   {CYAN}___   {PURPLE}/
           \\_______/
           /       \\
          /         \\
         /           \\

    {BOLD}🔮 S E E R : The Eye of Automation{RESET}
"""

def show_splash():
    sys.stdout.write(ART + "\n")

if __name__ == "__main__":
    show_splash()
