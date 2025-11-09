"""File system tools for deep agent - enables persistent storage of context and notes."""
from langchain_core.tools import tool
from pathlib import Path
from datetime import datetime
import json


# Workspace directory for agent files
WORKSPACE_DIR = Path("workspace")
WORKSPACE_DIR.mkdir(exist_ok=True)

NOTES_DIR = WORKSPACE_DIR / "notes"
NOTES_DIR.mkdir(exist_ok=True)

CONTEXT_DIR = WORKSPACE_DIR / "context"
CONTEXT_DIR.mkdir(exist_ok=True)


@tool
def save_note(title: str, content: str) -> str:
    """
    Save a note to the workspace for later reference.

    Args:
        title: The title/filename for the note
        content: The content of the note

    Returns:
        Confirmation with the file path
    """
    # Create a safe filename
    safe_title = "".join(c if c.isalnum() or c in "-_" else "_" for c in title)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{safe_title}.txt"

    filepath = NOTES_DIR / filename
    filepath.write_text(content)

    return f"Note saved to: {filepath}"


@tool
def read_note(filename: str) -> str:
    """
    Read a note from the workspace.

    Args:
        filename: The filename to read (can be partial match)

    Returns:
        The content of the note
    """
    # Try exact match first
    filepath = NOTES_DIR / filename
    if filepath.exists():
        return filepath.read_text()

    # Try partial match
    matches = [f for f in NOTES_DIR.glob(f"*{filename}*")]

    if not matches:
        return f"No note found matching: {filename}"

    if len(matches) > 1:
        return f"Multiple notes found: {', '.join(f.name for f in matches)}"

    return matches[0].read_text()


@tool
def list_notes() -> str:
    """
    List all notes in the workspace.

    Returns:
        A list of all note filenames
    """
    notes = sorted(NOTES_DIR.glob("*.txt"))

    if not notes:
        return "No notes found in workspace."

    return "Notes:\n" + "\n".join(f"- {n.name}" for n in notes)


@tool
def save_context(key: str, data: dict) -> str:
    """
    Save context information for later retrieval.

    Args:
        key: The key to identify this context
        data: Dictionary of context data

    Returns:
        Confirmation of save
    """
    safe_key = "".join(c if c.isalnum() or c in "-_" else "_" for c in key)
    filepath = CONTEXT_DIR / f"{safe_key}.json"

    filepath.write_text(json.dumps(data, indent=2))

    return f"Context saved with key: {key}"


@tool
def load_context(key: str) -> str:
    """
    Load previously saved context information.

    Args:
        key: The key to identify the context

    Returns:
        The context data as a JSON string
    """
    safe_key = "".join(c if c.isalnum() or c in "-_" else "_" for c in key)
    filepath = CONTEXT_DIR / f"{safe_key}.json"

    if not filepath.exists():
        return f"No context found for key: {key}"

    return filepath.read_text()


@tool
def list_context_keys() -> str:
    """
    List all saved context keys.

    Returns:
        A list of all context keys
    """
    contexts = sorted(CONTEXT_DIR.glob("*.json"))

    if not contexts:
        return "No saved contexts found."

    return "Saved contexts:\n" + "\n".join(f"- {c.stem}" for c in contexts)