#!/usr/bin/env python
"""A slideshow application that displays images with transition effects and monitors for new images."""

import argparse
import logging
import time
import tkinter as tk
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from PIL import Image, ImageTk
from watchdog.events import (
    EVENT_TYPE_CREATED,
    EVENT_TYPE_DELETED,
    EVENT_TYPE_MOVED,
    FileSystemEvent,
    FileSystemEventHandler,
)
from watchdog.observers import Observer

_DEFAULT_DURATION_MS = 5000
_DEFAULT_START_INDEX = 0
_TRANSITION_STEPS = 0.025
_TRANSITION_SLEEP = 0.0001
_HEIGHT = 1080
_WIDTH = 1650


@dataclass
class CliArguments:
    """Container for command line arguments."""

    images: Path
    start: int
    duration: int


def parse_arguments() -> CliArguments:
    """Parse command line arguments for the slideshow application."""
    parser = argparse.ArgumentParser(description="Diashow")
    parser.add_argument("--images", help="Path to the image directory")
    parser.add_argument("--start", type=int, default=_DEFAULT_START_INDEX, help="Starting number, default: 0")
    parser.add_argument(
        "--duration",
        type=int,
        default=_DEFAULT_DURATION_MS,
        help="Duration in milliseconds, default: 5000ms",
    )
    arguments = parser.parse_args()
    return CliArguments(images=Path(arguments.images), start=arguments.start, duration=arguments.duration)


class State(Enum):
    """Represents the current state of the slideshow."""

    NORMAL = 0
    PREVIEW = 1


class Slideshow(tk.Tk, FileSystemEventHandler):
    """
    Main slideshow application that displays images with transitions
    and monitors for new images in the specified directory.
    """

    _image_queue: list[Path]
    _image_preview_queue: list[Path]
    _image_queue_index: int
    _current_image: tk.Label

    def __init__(self, images_dir: Path, start: int, duration_ms: int) -> None:
        super().__init__()

        if not images_dir.exists():
            msg = f"{images_dir} does not exists."
            raise FileNotFoundError(msg)

        if duration_ms <= 0:
            msg = f"Invalid duration of {duration_ms}ms. Must be > 0ms"
            raise ValueError(msg)

        # Tkinter
        self.title("Slideshow")
        self.resizable(width=False, height=False)
        self.label = tk.Label(self)
        self.label.pack()
        self.current_image: Image.Image = None
        self.duration_ms = duration_ms
        self.attributes("-fullscreen", True)  # noqa: FBT003
        self.images_dir = images_dir
        self.configure(bg="black")

        # Watchdog
        self.observer = Observer()
        self.observer.schedule(self, self.images_dir, recursive=False)

        self.image_queue = sorted(images_dir.glob("*.JPG"))
        if len(self.image_queue) == 0:
            msg = f"No images found in {self.images_dir}"
            raise RuntimeError(msg)

        logging.debug("%i images loaded", len(self.image_queue))
        if abs(start) > len(self.image_queue):
            msg = f"Invalid start index {start}. Must be abs(index) < {len(self.images_queue)}"
            raise ValueError(msg)

        self.image_queue_index = start
        self.image_preview_queue = []

    def _next_image(self) -> None:
        """Load and display the next image in the queue."""
        if self._get_state() == State.PREVIEW:
            next_image_path = self.image_preview_queue.pop(0)
            logging.info("Next preview image %s", next_image_path)
        else:
            if self.image_queue_index == len(self.image_queue):
                self.image_queue_index = 0
            next_image_path = self.image_queue[self.image_queue_index]
            self.image_queue_index += 1
            logging.info("Next image %s", next_image_path)

        next_image = self._get_image(next_image_path)
        if self.current_image is None:
            self.current_image = next_image
        else:
            self._transition(next_image)
        self.after(self.duration_ms, self._next_image)

    def _get_state(self) -> State:
        """Determine the current state of the slideshow."""
        if len(self.image_preview_queue) > 0:
            return State.PREVIEW
        return State.NORMAL

    def _get_image(self, path: Path) -> Image.Image:
        """Load and resize an image from the given path."""
        image = Image.open(path)
        return image.resize((_WIDTH, _HEIGHT))

    def _display_image(self, image: Image.Image) -> None:
        """Display the given image in the application window."""
        tk_image = ImageTk.PhotoImage(image)
        self.label.config(image=tk_image)
        self.label.image = tk_image
        self.label.update()

    def _transition(self, next_image: Image.Image) -> None:
        """Create a smooth transition effect between the current and next image."""
        alpha = 0
        while alpha < 1:
            blended_image = Image.blend(self.current_image, next_image, alpha)
            self._display_image(blended_image)
            alpha += _TRANSITION_STEPS
            time.sleep(_TRANSITION_SLEEP)

        self.current_image = next_image
        self._display_image(self.current_image)

    def on_any_event(self, event: FileSystemEvent) -> None:
        """Handle file system events."""
        if event.is_directory:
            if event.event_type == EVENT_TYPE_CREATED:
                logging.debug("File created: %s", event.src_path)
                image_path = Path(event.src_path)
                self._handle_created_file(image_path)
            elif event.event_type in (EVENT_TYPE_DELETED, EVENT_TYPE_MOVED):
                logging.debug("File deleted or moved: %s", event.src_path)
                image_path = Path(event.src_path)
                self._handel_deleted_or_moved_file(image_path)

    def _handle_created_file(self, image_path: Path) -> None:
        self.image_queue.insert(0, image_path)
        self.image_queue_index += 1
        self.image_preview_queue.append(image_path)

    def _handel_deleted_or_moved_file(self, image_path: Path) -> None:
        if image_path in self.image_queue:
            removed_index = self.image_queue.index(image_path)
            self.image_queue.pop(removed_index)
            # Correct current position
            if self.image_queue_index >= removed_index:
                self.image_queue_index -= 1
        elif image_path in self.image_preview_queue:
            self.image_preview_queue.remove(image_path)

    def start(self) -> None:
        """Start the slideshow."""
        logging.info(
            "Starting diashow in %s at index %i with an image duration of %ims",
            self.images_dir,
            self.image_queue_index,
            self.duration_ms,
        )
        self.observer.start()
        self._next_image()


def main() -> None:
    """Entry point for the slideshow application."""
    logging.basicConfig(level=logging.INFO)

    try:
        cli_arguments = parse_arguments()
        slideshow = Slideshow(cli_arguments.images, cli_arguments.start, cli_arguments.duration)
        slideshow.start()
        slideshow.mainloop()
    except Exception as error:  # noqa: BLE001
        logging.error("%s", error)  # noqa: TRY400


if __name__ == "__main__":
    main()
