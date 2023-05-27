import tkinter as tk
import pathlib
from PIL import Image, ImageTk
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import glob
import sys
import time
from enum import Enum


_IMAGE_DIR = pathlib.Path('images')
_DURATION_MS = 5000
_TRANSITION_STEPS = 0.05
_TRANSITION_SLEEP = 0.025

class State(Enum):
    NORMAL = 0
    PREVIEW = 1


class Application(tk.Tk, FileSystemEventHandler):

    image_queue: list[pathlib.Path]
    image_preview_queue: list[pathlib.Path]
    image_queue_index: int
    current_image: tk.Label
    after_id: int


    def __init__(self, images_dir: pathlib.Path, duration_ms: int):
        super().__init__()

        # Tkinter
        self.title('Slideshow')
        self.resizable(width=False, height=False)
        self.label = tk.Label(self)
        self.label.pack()
        self.current_image: Image = None
        self.duration_ms = duration_ms
        self.attributes('-fullscreen', True)
        self.images_dir = images_dir

        # Watchdog
        self.observer = Observer()
        self.observer.schedule(self, self.images_dir, recursive=False)
        self.observer.start()

        self.image_queue = [pathlib.Path(image) for image in glob.glob(f'{images_dir}/*.jpg')]
        self.image_queue_index = 0
        self.image_preview_queue = []

          
    def _next_image(self) -> None:

        if self._get_state() == State.PREVIEW:
            next_image_path = self.image_preview_queue.pop(0)
            print(f'Next preview image {next_image_path}')
        else:
            if self.image_queue_index == len(self.image_queue):
                self.image_queue_index = 0
            next_image_path = self.image_queue[self.image_queue_index]
            self.image_queue_index += 1
            print(f'Next image {next_image_path}')

        next_image = self._get_image(next_image_path)
        if self.current_image is None:
            self.current_image = next_image
        else:
            self._transition(next_image)
        self.after(self.duration_ms, self._next_image)

    def _get_state(self) -> State:
        if len(self.image_preview_queue) > 0:
            return State.PREVIEW
        else:
            return State.NORMAL

    def _get_image(self, path: pathlib.Path) -> Image:
        image = Image.open(path)
        #image = image.resize((self.winfo_width(), self.winfo_height()))
        image = image.resize((1920, 1080))
        return image

    def _display_image(self, image: Image) -> None:
        image = ImageTk.PhotoImage(image)
        self.label.config(image=image)
        self.label.image = image
        self.label.update()

    def _transition(self, next_image: Image):
        alpha = 0
        while alpha < 1:
            blended_image = Image.blend(self.current_image, next_image, alpha)
            self._display_image(blended_image)
            alpha += _TRANSITION_STEPS
            time.sleep(_TRANSITION_SLEEP)

        self.current_image = next_image

    def on_created(self, event):
        if not event.is_directory:
            image_path = pathlib.Path(event.src_path)
            self.image_queue.insert(0, image_path)
            self.image_queue_index += 1
            self.image_preview_queue.append(image_path)
            print(f'File created: {event.src_path}')
        

    def start(self):
        self._next_image()

def main():
    application = Application(_IMAGE_DIR, _DURATION_MS)

    application.start()
    application.mainloop()


if __name__ == "__main__":
    sys.exit(main())