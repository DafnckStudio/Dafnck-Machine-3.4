from pathlib import Path
import inspect

def find_project_root(start_path: Path = None) -> Path:
    """
    Dynamically find the project root directory by searching upwards from the given path (or caller's file)
    for a marker file (pyproject.toml, .git, or cursor_agent subdirectory). Returns a pathlib.Path to the project root.
    If not found, returns the parent of the directory containing the caller's file.

    Args:
        start_path (Path, optional): The path to start searching from. If None, uses the caller's file location.

    Returns:
        Path: The project root directory as a pathlib.Path object.
    """
    if start_path is None:
        # Get the caller's file location
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        if module and hasattr(module, '__file__'):
            current = Path(module.__file__).resolve()
        else:
            current = Path.cwd()
    else:
        current = Path(start_path).resolve()
    # If current is a file, start from its parent
    if current.is_file():
        current = current.parent
    for parent in [current] + list(current.parents):
        if (parent / "pyproject.toml").exists() or (parent / ".git").exists() or (parent / "cursor_agent").is_dir():
            return parent
    # Fallback: if no project root found, return the current working directory
    # or the directory containing the file, whichever makes more sense
    return current 