import os
import subprocess
import time

from dotenv import dotenv_values
import pyperclip
import pywinctl as pwc
from pynput.keyboard import Controller, Key

from ya_speech_kit import text_to_voice

keyboard = Controller()
# Путь к исполняемому файлу и заголовок окна ScreenshotReader
config = dotenv_values(
    os.path.join(os.getenv("LOCALAPPDATA"), "ScreenshotToSpeech/.env")
)
finereader_path = config["APP_FOLDER"]
window_title = config["APP_WINDOW_TITLE"]
# Позволяет избежать повторных распознаваний и пустого текста
original_text = "text to avoid double clip recognition"
timeout = 30  # таймаут времени распознавания для FineReader


def waitForNewPaste(
    event,
    timeout=None,
):
    """
    Блокирует исполнение пока строка в буфере не поменяется.
    Код взят из старой версии pyperclip == 1.8.2
    В следующих после этой версии автор вырезал этот функционал потому что
    считает что его не должно быть в core библиотеках.
    """
    start_time = time.time()
    pyperclip.copy(original_text)
    while True:
        current_text = pyperclip.paste()
        if current_text != original_text or not event.is_set():
            return
        time.sleep(0.01)

        if timeout is not None and time.time() > start_time + timeout:
            raise Exception(
                "waitForNewPaste() timeout after " + str(timeout) + " seconds."
            )


def capture_screen_with_finereader(
    event,
    output_device_id,
    finereader_path=finereader_path,
    window_title=window_title,
) -> str:
    """
    Запускает ABBYY Screenshot Reader, делает скриншот и возвращает
    распознанный текст.
    """
    try:
        # Запуск процесса в фоне
        # subprocess.run() - в основном потоке
        # subprocess.Popen() - в основном потоке, но создает дочерний процесс,
        # не блокируя основной поток
        subprocess.Popen([finereader_path])
        print("ABBYY Screenshot Reader loaded")

        # Нахожу pid окна
        windows = pwc.getWindowsWithTitle(window_title)
        while not windows:
            print(f"Window '{window_title}' not found yet...")
            time.sleep(0.2)
            windows = pwc.getWindowsWithTitle(window_title)
            continue
        print("Window Screenshot Reader found, descriptor ", windows)

        # В windows, ForegroundLockTimeout запрещает перехватывать фокус окну
        # запущеному скриптом.
        # Либо отключаем полностью в реестре для всех приложений
        # Либо клавиша АЛЬТ сбрасывает блок
        keyboard.press(Key.alt)
        keyboard.release(Key.alt)

        # Активирую (фокус) окно
        window = windows[0]
        # window.show(True)
        # window.restore(True)
        # window.acceptInput(True)
        if not window.isActive:
            window.activate(True)

        # Отправляю команду на захват изображения
        with keyboard.pressed(Key.alt):
            keyboard.press(Key.enter)
            keyboard.release(Key.enter)
        print("Image capture started")

        # Жду завершения распознавания (пока пользователь выберет область
        # и подтвердит распознавание или отменит операцию или таймаут 30 сек)
        print("Waiting for image capture and text recognition...")
        waitForNewPaste(event, timeout)

        # Получаю текст из буфера обмена
        text = pyperclip.paste()
        text_fixed = " ".join(text.split())

        if event.is_set() and text_fixed != original_text:
            event.clear()
            print(
                "=========== Text to voice ===========",
                text_fixed,
                "=====================================",
                sep="\n"
            )
            text_to_voice(text_fixed, output_device_id)
        else:
            print("Image capture or text recognition interrupted")

    except Exception as e:
        print(f"Error occured: {e}")
        event.clear()


if __name__ == "__main__":
    pass
