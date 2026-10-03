import requests
import ollama

# 1. Ask the LLM to make a decision
prompt = "You are a Minecraft bot. Reply with exactly one word: JUMP or SPIN."
print("Asking Ollama...")

response = ollama.chat(
    model='llama3.2:3b',
    messages=[{'role': 'user', 'content': prompt}]
)

decision = response['message']['content'].strip().upper()
print(f"LLM decided to: {decision}")

# 2. Send the decision to the Mineflayer body
if "JUMP" in decision:
    requests.post("http://localhost:3000/action", json={"action": "JUMP"})
elif "SPIN" in decision:
    requests.post("http://localhost:3000/action", json={"action": "SPIN"})
else:
    print("Model generated an invalid action.")