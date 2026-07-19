import subprocess
import time

import pyperclip
import pywinctl as pwc
from pynput.keyboard import Controller, Key

keyboard = Controller()
# Путь к исполняемому файлу и заголовок окна ScreenshotReader
finereader_path = "C:\Program Files\ABBYY FineReader 16\ScreenshotReader.exe"
window_title = "ABBYY Screenshot Reader"
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
                "waitForNewPaste() таймаут после " + str(timeout) + " секунд."
            )


def capture_screen_with_finereader(
    event,
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
        print("ABBYY Screenshot Reader запущен...")

        # Нахожу pid окна
        windows = pwc.getWindowsWithTitle(window_title)
        while not windows:
            print(f"Ошибка: Окно '{window_title}' не найдено.")
            time.sleep(0.2)
            windows = pwc.getWindowsWithTitle(window_title)
            continue
        print("Окно Screenshot Reader найдено, дескриптор окна ", windows)

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
        print("Команда на захват изображения отправлена.")

        # Жду завершения распознавания (пока пользователь выберет область
        # и подтвердит распознавание или отменит операцию или таймаут 30 сек)
        print("Ожидание завершения распознавания...")
        waitForNewPaste(event, timeout)

        # Получаю текст из буфера обмена
        text = pyperclip.paste()
        if event.is_set() and text != original_text:
            event.clear()
            print("готово: ", text)
            return text if text else None
        else:
            print("Распознование текста прервано.")

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        event.clear()
        return None


if __name__ == "__main__":
    pass
