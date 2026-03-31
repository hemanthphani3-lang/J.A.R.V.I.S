import asyncio
import os
import requests
from jarvis import jarvis_brain

async def test_god_mode_execution():
    print("Testing God Mode Autonomous Execution...")
    # Simulate a command that requires terminal access
    command = "list the current directory using bash"
    response = await jarvis_brain(command)
    
    print(f"\nJARVIS Response:\n{response}")
    
    if "[TERMINAL]" in response:
        print("\nGod Mode Success: Terminal command executed autonomously.")
    else:
        print("\nGod Mode Failure: Terminal tag not found or execution failed.")

if __name__ == "__main__":
    # Ensure Ollama is running if possible (skipping in CI-like test)
    try:
        asyncio.run(test_god_mode_execution())
    except Exception as e:
        print(f"God Mode Test Error: {e}")
