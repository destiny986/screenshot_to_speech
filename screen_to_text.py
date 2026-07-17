import subprocess
import time

import pygetwindow as gw
import pyperclip
from pynput.keyboard import Controller, Key

# Путь к исполняемому файлу и заголовок окна ScreenshotReader
finereader_path = "C:\Program Files\ABBYY FineReader 16\ScreenshotReader.exe"
window_title = "ABBYY Screenshot Reader"


def waitForNewPaste(timeout=None):
    """
    Блокирует исполнение пока строка в буфере не поменяется.
    Код взят из старой версии pyperclip == 1.8.2
    В следующих после этой версии автор вырезал этот функционал потому что
    считает что его не должно быть в core библиотеках.
    """
    startTime = time.time()
    originalText = pyperclip.paste()
    while True:
        currentText = pyperclip.paste()
        if currentText != originalText:
            return currentText
        time.sleep(0.01)

        if timeout is not None and time.time() > startTime + timeout:
            raise Exception(
                "waitForNewPaste() timed out after "
                + str(timeout)
                + " seconds."
            )


def capture_screen_with_finereader(
    finereader_path=finereader_path, window_title=window_title
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
        print("ABBYY Screenshot Reader запущен...")

        # Нахожу и активирую окно
        windows = gw.getWindowsWithTitle(
            window_title
        )   # возвращает объект окна заголовок которого содержит эту строку
        while not windows:
            print(f"Ошибка: Окно '{window_title}' не найдено.")
            time.sleep(0.2)
            windows = gw.getWindowsWithTitle(window_title)
            continue
        window = windows[0]
        if window.isMinimized:
            window.restore()
        window.activate()

        # Отправляю команду на захват изображения
        keyboard = Controller()
        with keyboard.pressed(Key.alt):
            keyboard.press(Key.enter)
            keyboard.release(Key.enter)
        print("Команда на захват изображения отправлена.")

        # Жду завершения распознавания (пока пользователь не выберет область
        # и подтвердит распознавание или таймаут 30 сек)
        print("Ожидание завершения распознавания...")
        waitForNewPaste(30)

        # Получаю текст из буфера обмена
        text = pyperclip.paste()

        return text if text else None

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None


if __name__ == "__main__":
    recognized_text = capture_screen_with_finereader()

    if recognized_text:
        print("\nРаспознанный текст:")
        print(recognized_text)
