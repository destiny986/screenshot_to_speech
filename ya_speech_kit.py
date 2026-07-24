from __future__ import annotations

import numpy as np
from sounddevice import OutputStream
from dotenv import dotenv_values
import os

from yandex_ai_studio_sdk import AIStudio
from yandex_ai_studio_sdk._speechkit.enums import LoudnessNormalization, PCM16


# Динамики (Realtek(R) Audio)
SAMPLERATE = 44100

config = dotenv_values(os.path.join(os.getenv("LOCALAPPDATA"), "ScreenshotToSpeech/.env"))

def convert(data: bytes):
    '''
    Коневертирует тип данных из буфера в 32-битные числа с плавающей точкой
    для возможности воспроизведения в sounddevice.
    '''
    audio_int16 = np.frombuffer(data, dtype=np.int16)
    audio_normalized = audio_int16.astype(np.float32) / 32768.0
    return audio_normalized


def text_to_voice(text, output_device_id) -> None:
    '''Озвучивает принятый текст.'''
    # Логин в Яндекс AI Studio.
    sdk = AIStudio(
        folder_id=config['YC_FOLDER_ID'],
        auth=config['YC_API_KEY'],
    ).setup_default_logging()


    tts = sdk.speechkit.text_to_speech(
        # Нормализация громкости LUFS (по умолчанию) или MAX_PEAK
        # loudness_normalization=LoudnessNormalization.LUFS,

        # Определяет выходной аудио формат
        # Default: 22050Hz, linear 16-bit signed little-endian PCM, with WAV header
        # MP3, WAV, OGG_OPUS. Для sounddevice выбрать PCM16 (WAV)
        # audio_format=PCM16(SAMPLERATE,1),
        audio_format=f'PCM16({SAMPLERATE})',

        # Используемая для синтеза TTS модель.
        # На текущий момент должно быть пусто.
        # model= ,       [str]

        # Выбор голоса, роли("амплуа" в песочнице), скорости чтения. Список тут:
        # https://aistudio.yandex.ru/docs/en/speechkit/tts/voices.html
        voice='kirill', # [str]
        # role= ,       # [str]
        speed=1,        # [float]

        # Для LUFS в диапазоне [-149;0), по умолчанию -19
        # Для MAX_PEAK в дипапзоне (0;1], по умолчанию 0.7
        # volume= ,     [float]

        # Высота голоса в диапазоне [-1000;1000] Гц.
        # Ноль по умолчанию
        # pitch_shift= ,[float]
    )

    with OutputStream(samplerate=SAMPLERATE, device=output_device_id, channels=1) as out:
        # Basic method - .run_stream, which yields result chunk by chunk
        for partial_result in tts.run_stream(text):
            print(f'Chunk [{partial_result.start_ms}, {partial_result.end_ms}] ms: {partial_result.text}')
            out.write(convert(partial_result.data))

if __name__ == '__main__':
    text_to_voice("Плодородные некогда угодья превратились в блёклую пустошь, по которой были разбросаны деревянные остовы заброшенных мельниц",1)
