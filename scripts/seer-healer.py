import sys
import os
import subprocess
import json

# Try to use Gemini CLI first, fallback to Ollama if unavailable
def consult_alchemist(script_path, exit_code, error_log):
    print(f"\n\033[38;5;201m🧪 The Alchemist is analyzing the failure...\033[0m")
    
    try:
        with open(script_path, 'r', errors='ignore') as f:
            script_content = f.read()
    except Exception as e:
        script_content = f"Could not read script: {e}"

    prompt = f"""
You are the Alchemist, an expert debugging AI. 
The following script failed with exit code {exit_code}.

Script Path: {script_path}

Script Content:
```
{script_content}
```

Error Log (stderr):
```
{error_log}
```

Provide a concise, highly technical explanation of WHY it failed, and provide the EXACT code to fix it. 
Keep your response short and "witchy/mystical" in tone, but the code must be perfect.
"""

    # Try Gemini CLI
    try:
        # Check if gemini is available
        subprocess.run(["gemini", "--version"], capture_output=True, check=True)
        
        print(f"\033[38;5;141m✨ Summoning Gemini for guidance...\033[0m\n")
        # Run gemini and stream output
        process = subprocess.Popen(["gemini", "ask", prompt], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
        process.wait()
        return
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass # Fallback to Ollama
        
    # Try Ollama Fallback
    try:
        print(f"\033[38;5;141m✨ Summoning Local Ollama for guidance...\033[0m\n")
        import requests
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3", # Assuming a standard model is available
            "prompt": prompt,
            "stream": True
        }, stream=True)
        
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                sys.stdout.write(data.get("response", ""))
                sys.stdout.flush()
        print()
    except Exception as e:
        print(f"\033[31m❌ The Alchemist's connection was broken: {e}\033[0m")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: seer-healer.py <script_path> <exit_code>")
        sys.exit(1)
        
    script_path = sys.argv[1]
    exit_code = sys.argv[2]
    
    # Read stderr from stdin (piped from fish)
    error_log = sys.stdin.read()
    
    consult_alchemist(script_path, exit_code, error_log)
