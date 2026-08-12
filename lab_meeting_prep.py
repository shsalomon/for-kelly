"""Prepare neuroscience lab-meeting briefs with a persistent Backboard agent."""

import argparse
import json
import os
import sys
from pathlib import Path

from backboard import BackboardClient, BackboardError


STATE_FILE = Path(".lab_meeting_prep_state.json")
SYSTEM_PROMPT = """You are Kelly's neuroscience lab meeting preparation assistant.
Turn rough research notes, paper abstracts, results, and questions into a concise,
scientifically careful meeting brief. Use these sections when appropriate:
1. One-sentence takeaway
2. Background and motivation
3. Methods and design
4. Key findings
5. Interpretation and limitations
6. Discussion questions
7. Suggested next steps

Do not invent papers, results, citations, statistics, or experimental details. Clearly
label assumptions and identify missing information. This is research support, not
medical or clinical advice.
"""


def load_state() -> dict[str, str]:
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_state(state: dict[str, str]) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def setup_conversation(client: BackboardClient) -> tuple[str, str]:
    state = load_state()
    assistant_id = state.get("assistant_id")
    thread_id = state.get("thread_id")

    if not assistant_id:
        assistant = client.create_assistant(
            name="Kelly's Lab Meeting Prep Agent",
            description="Prepares structured neuroscience lab-meeting briefs.",
            system_prompt=SYSTEM_PROMPT,
        )
        assistant_id = str(assistant.assistant_id)
        state["assistant_id"] = assistant_id

    if not thread_id:
        thread = client.create_thread(assistant_id)
        thread_id = str(thread.thread_id)
        state["thread_id"] = thread_id

    save_state(state)
    return assistant_id, thread_id


def response_text(messages: list[dict]) -> str:
    for message in reversed(messages):
        if message.get("role") == "assistant" and message.get("content"):
            return str(message["content"])
    return "No assistant response was returned."


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Turn neuroscience research notes into a lab-meeting brief."
    )
    parser.add_argument(
        "notes",
        nargs="?",
        help="Research notes or an abstract. If omitted, paste multi-line notes interactively.",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Start a new meeting conversation, retaining the same assistant.",
    )
    args = parser.parse_args()

    api_key = os.getenv("BACKBOARD_API_KEY")
    if not api_key:
        print("Set BACKBOARD_API_KEY before running this agent.", file=sys.stderr)
        return 2

    notes = args.notes or sys.stdin.read().strip()
    if not notes:
        print("Provide notes as an argument or pipe them through standard input.", file=sys.stderr)
        return 2

    try:
        client = BackboardClient(api_key=api_key)
        assistant_id, thread_id = setup_conversation(client)
        if args.reset:
            thread_id = str(client.create_thread(assistant_id).thread_id)
            save_state({"assistant_id": assistant_id, "thread_id": thread_id})

        prompt = f"""Prepare a lab-meeting brief from the following material:\n\n{notes}"""
        response = client.add_message(thread_id, content=prompt, memory="auto")
        print(response_text(response.messages))
    except BackboardError as error:
        print(f"Backboard API error: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())