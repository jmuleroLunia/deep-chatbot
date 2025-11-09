"""File system tools for deep agent - enables per-thread persistent storage of notes."""
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from datetime import datetime, timezone
from sqlalchemy import select
from database import SessionLocal
from models import Note, Thread


def _get_thread_id_from_config(config: RunnableConfig) -> str:
    """
    Extract thread_id from the RunnableConfig.

    Args:
        config: The RunnableConfig object passed by LangGraph

    Returns:
        The thread_id string, defaults to "default" if not found
    """
    if config and isinstance(config, dict):
        configurable = config.get("configurable", {})
        if configurable:
            return configurable.get("thread_id", "default")
    return "default"


@tool
def save_note(title: str, content: str, config: RunnableConfig) -> str:
    """
    Save a note for the current thread for later reference.
    Each thread has its own independent notes.

    Args:
        title: The title/identifier for the note
        content: The content of the note

    Returns:
        Confirmation with the note identifier
    """
    thread_id = _get_thread_id_from_config(config)

    # Create a safe filename from title
    safe_title = "".join(c if c.isalnum() or c in "-_" else "_" for c in title)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{safe_title}"

    with SessionLocal() as db:
        # Check if thread exists
        thread = db.execute(select(Thread).where(Thread.id == thread_id)).scalar_one_or_none()
        if not thread:
            return f"Error: Thread '{thread_id}' does not exist. Cannot save note."

        # Create new note
        note = Note(
            thread_id=thread_id,
            filename=filename,
            content=content
        )

        db.add(note)
        db.commit()

    return f"Note '{title}' saved for this thread"


@tool
def read_note(filename: str, config: RunnableConfig) -> str:
    """
    Read a note from the current thread's workspace.

    Args:
        filename: The filename to read (can be partial match)

    Returns:
        The content of the note
    """
    thread_id = _get_thread_id_from_config(config)

    with SessionLocal() as db:
        # Try exact match first
        note = db.execute(
            select(Note).where(
                Note.thread_id == thread_id,
                Note.filename == filename
            )
        ).scalar_one_or_none()

        if note:
            return note.content

        # Try partial match
        notes = db.execute(
            select(Note).where(
                Note.thread_id == thread_id,
                Note.filename.like(f"%{filename}%")
            )
        ).scalars().all()

        if not notes:
            return f"No note found matching: {filename} in this thread"

        if len(notes) > 1:
            return f"Multiple notes found: {', '.join(n.filename for n in notes)}"

        return notes[0].content


@tool
def list_notes(config: RunnableConfig) -> str:
    """
    List all notes for the current thread.

    Returns:
        A list of all note filenames for this thread
    """
    thread_id = _get_thread_id_from_config(config)

    with SessionLocal() as db:
        notes = db.execute(
            select(Note).where(Note.thread_id == thread_id).order_by(Note.created_at)
        ).scalars().all()

        if not notes:
            return "No notes found for this thread."

        return "Notes:\n" + "\n".join(f"- {n.filename}" for n in notes)


# Context tools removed since they weren't explicitly required in the per-thread plan
# If needed later, they can be implemented similar to notes
