"""
Diagnostic script to capture raw watchdog events with precise timing.

Usage:
    python debug_events.py <folder_to_monitor>

Then save a file (from Photoshop, Notepad, etc.) into the monitored folder.
After ~30 seconds, press Ctrl+C and copy the full output.
"""

import sys
import time
import threading
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Track everything
events_log = []
start_time = time.perf_counter()
log_lock = threading.Lock()

def ts():
    """Millisecond-precision timestamp relative to start."""
    return f"{(time.perf_counter() - start_time) * 1000:10.1f}ms"

def thread_id():
    return f"T-{threading.current_thread().ident}"

class DiagnosticHandler(FileSystemEventHandler):
    def __init__(self, label):
        self.label = label

    def _log(self, event_type, event):
        src = event.src_path
        is_dir = event.is_directory
        t = ts()
        tid = thread_id()

        # Get file stat if possible
        stat_info = ""
        try:
            p = Path(src)
            if p.exists() and not is_dir:
                s = p.stat()
                stat_info = f" size={s.st_size} mtime={s.st_mtime:.6f}"
        except Exception as e:
            stat_info = f" stat_err={e}"

        entry = f"[{t}] [{tid}] {event_type:10s} {'DIR' if is_dir else 'FILE'} {src}{stat_info}"
        with log_lock:
            events_log.append(entry)
        print(entry)

    def on_created(self, event):
        self._log("CREATED", event)

    def on_modified(self, event):
        self._log("MODIFIED", event)

    def on_deleted(self, event):
        self._log("DELETED", event)

    def on_moved(self, event):
        self._log("MOVED", event)
        # Also log destination
        dest_entry = f"[{ts()}] [{thread_id()}] MOVED_TO    {event.dest_path}"
        with log_lock:
            events_log.append(dest_entry)
        print(dest_entry)

    def on_closed(self, event):
        self._log("CLOSED", event)


def main():
    if len(sys.argv) < 2:
        print("Usage: python debug_events.py <folder_to_monitor>")
        print("\nThis will log every raw filesystem event with millisecond timestamps.")
        print("Save a file into the monitored folder, then press Ctrl+C to stop.")
        sys.exit(1)

    folder = Path(sys.argv[1]).resolve()
    if not folder.is_dir():
        print(f"Error: {folder} is not a directory")
        sys.exit(1)

    print("=" * 70)
    print("WATCHDOG EVENT DIAGNOSTIC")
    print("=" * 70)
    print(f"Monitoring:  {folder}")
    print(f"Observer:    {Observer.__name__}")
    print(f"Platform:    {sys.platform}")
    print(f"Python:      {sys.version}")
    print(f"Watchdog events: CREATED, MODIFIED, DELETED, MOVED, CLOSED")
    print("=" * 70)
    print()
    print("Now save a file into the monitored folder.")
    print("Wait ~15 seconds after saving, then press Ctrl+C to stop.")
    print()
    print(f"{'Timestamp':>14s}   {'Thread':<16s} {'Event':<10s} {'Type':<5s} Path")
    print("-" * 70)

    handler = DiagnosticHandler(str(folder))
    observer = Observer()
    observer.schedule(handler, str(folder), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()

    # Summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total events captured: {len(events_log)}")
    print()

    # Group events by file
    from collections import defaultdict
    file_events = defaultdict(list)
    for entry in events_log:
        # Extract file path (after FILE or DIR)
        parts = entry.split(" FILE ", 1)
        if len(parts) == 2:
            fpath = parts[1].split(" size=")[0].split(" stat_err=")[0].strip()
            file_events[fpath].append(entry)
        else:
            parts = entry.split(" DIR ", 1)
            if len(parts) == 2:
                fpath = parts[1].split(" size=")[0].split(" stat_err=")[0].strip()
                file_events[fpath].append(entry)

    for fpath, entries in file_events.items():
        fname = Path(fpath).name
        print(f"\n--- {fname} ({len(entries)} events) ---")
        for e in entries:
            print(f"  {e}")

    print()
    print("Copy everything above and paste it for analysis.")

if __name__ == "__main__":
    main()
