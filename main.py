import threading

from pynput import mouse

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
            button == mouse.Button.x1
            and not event_text_capture_in_process.is_set()
        ):
            event_text_capture_in_process.set()
            capture_scr_thread = threading.Thread(
                target=capture_screen_with_finereader,
                args=(event_text_capture_in_process,),
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

    event_text_capture_in_process = threading.Event()
    # Создание и запуск слушателя в блоке with
    with mouse.Listener(on_click=screen_to_text_clicks) as listener:
        listener.join()
