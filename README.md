# screenshot_to_speech
**Озвучивание текста на области захваченной курсором.**

Использует функционал ABBYY Screenshot Reader для распознавания текста и tts SpeechKit Яндекса для генерации голоса.  
<br/>
Конфигурация в .env по адресу  
```
%LOCALAPPDATA%/ScreenshotToSpeech/.env
```
В формате
```
YC_API_KEY = "key"
YC_FOLDER_ID = "id"
APP_FOLDER = "C:\Program Files\ABBYY FineReader 16\ScreenshotReader.exe"
APP_WINDOW_TITLE = "ABBYY Screenshot Reader
```
