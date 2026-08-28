## Nuitka==2.5.1
## Certifi==2024.8.30
## PySide6==6.8.0.2
# nuitka-project: --mingw64
## nuitka-project: --onefile
## nuitka-project: --windows-console-mode=disable
#
# nuitka-project: --enable-plugin=pyside6
# nuitka-project: --include-qt-plugins=qml
#
# nuitka-project: --windows-icon-from-ico=data/icon.ico
# nuitka-project: --file-version=1.0
# nuitka-project: --company-name=KabanTechnologies
# nuitka-project: --product-name=Screen to Speech
# nuitka-project: --output-filename=Screen to Speech

# nuitka-project: --enable-plugin=numpy
# nuitka-project: --follow-imports
# nuitka-project: --include-data-dir=data/={MAIN_DIRECTORY}/data

import threading

from pynput import mouse
from yandex_ai_studio_sdk._experimental.audio.utils import choose_audio_device

from screen_to_text import capture_screen_with_finereader


def on_click(x, y, button, pressed):
    """Узнать key для нажатой кнопки мыши."""
    print(
        "{0} at {1} - {2}".format(
            "Pressed" if pressed else "Released",
            (x, y),
            button,
        )
    )
    if not pressed:
        pass
    # боковая верх - Button.x1
    # боковая низ - Button.x2


def screen_to_text_clicks(x, y, button, pressed):
    try:
        if (
            button in (mouse.Button.x1,mouse.Button.x2)
            and not event_text_capture_in_process.is_set()
        ):
            event_text_capture_in_process.set()
            capture_scr_thread = threading.Thread(
                target=capture_screen_with_finereader,
                args=(event_text_capture_in_process, output_device_id),
                daemon=True,
            )
            capture_scr_thread.start()
        elif (
            button == mouse.Button.right
            and event_text_capture_in_process.is_set()
        ):
            event_text_capture_in_process.clear()
        elif button == mouse.Button.middle:
            return False
        else:
            pass

    except:
        pass


if __name__ == "__main__":
    # Выбор id девайсов для воспроизведения. Может меняться.
    output_device_id = choose_audio_device("out")
    print(
        "====================================================\n"
        "Screen to Speech loaded\n"
        "Mouse button x1 or x2 - capture image for StS\n"
        "Right mouse button - image capture cancellation\n"
        "Middle mouse button - exit program\n"
        "===================================================="
    )
    event_text_capture_in_process = threading.Event()
    # Создание и запуск слушателя в блоке with
    with mouse.Listener(on_click=screen_to_text_clicks) as listener:
        listener.join()
