# SVGify

🌐 **Язык:** [English](Readme.md) | [Русский](Readme_ru.md)

SVGify — консольный инструмент для преобразования логотипов из растровых изображений и других поддерживаемых источников в цветную векторную графику SVG.

Он поддерживает интерактивный режим и командную строку, пакетную конвертацию, обработку папок и ZIP-архивов, удаление фона, сокращение палитры, сглаживание контуров и многоязычный интерфейс.

## Поддерживаемые форматы

- Изображения: PNG, JPG, JPEG, JFIF, WebP, BMP, GIF, TIFF, ICO, PPM, PGM, PBM, PNM, TGA
- Современные форматы: HEIC, HEIF, AVIF
- RAW-форматы: RAW, DNG, CR2, CR3, NEF, ARW, ORF, RW2, RAF, PEF, SRW
- Документы и векторные файлы: PDF, SVG
- Архивы: ZIP
- Папки с поддерживаемыми файлами

Для PDF обрабатывается только первая страница, а для анимированных изображений — только первый кадр.

## Возможности

- Создание цветных SVG
- Автоматическое или принудительное удаление фона
- Настраиваемое количество цветов
- Настраиваемая детализация контуров
- Шумоподавление
- Пакетная конвертация
- Рекурсивная обработка папок
- Обработка ZIP-архивов
- Сохранение существующих SVG без повторной трассировки
- Английский, русский и китайский интерфейс
- Поддержка Windows, Linux и macOS
- Интерактивный терминальный интерфейс
- Полноценный режим командной строки

## Важное ограничение

Автоматическая трассировка не может восстановить скрытые детали или гарантировать математически идентичную копию любого логотипа.

Качество результата зависит от:

- Разрешения изображения
- Освещения
- Артефактов сжатия
- Угла съемки и перспективы
- Теней и отражений
- Сложности фона
- Сложности исходного логотипа

Для получения лучшего результата используйте изображение высокого разрешения с четкими краями, равномерным освещением, минимальным сжатием, простым фоном и без перспективных искажений.

## Требования

- Python 3.10 или новее
- pip
- Для CairoSVG могут потребоваться системные библиотеки Cairo

## Установка

Клонируйте репозиторий или скачайте его файлы, откройте папку проекта и создайте виртуальное окружение.

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Linux и macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Ubuntu или Debian

Для CairoSVG могут потребоваться дополнительные системные пакеты:

```bash
sudo apt update
sudo apt install libcairo2 libffi-dev
```

### macOS с Homebrew

```bash
brew install cairo libffi
```

## Интерактивный режим

Запустите `SVGify.py` без аргументов:

```bash
python SVGify.py
```

В интерактивном меню можно настроить:

- Папку сохранения
- Количество цветов
- Детализацию контуров
- Режим удаления фона
- Язык интерфейса

Пути можно вводить вручную или перетаскивать в окно совместимого терминала.

## Режим командной строки

Преобразовать одно изображение:

```bash
python SVGify.py logo.png
```

Преобразовать несколько файлов:

```bash
python SVGify.py logo.png brand.jpg icon.webp
```

Рекурсивно обработать папку:

```bash
python SVGify.py ./logos
```

Обработать ZIP-архив:

```bash
python SVGify.py logos.zip
```

Выбрать папку сохранения:

```bash
python SVGify.py logo.png --output ./svg
```

Настроить векторизацию:

```bash
python SVGify.py logo.png --colors 16 --detail 85 --background auto
```

Отключить шумоподавление:

```bash
python SVGify.py logo.png --no-denoise
```

Обрабатывать большие изображения в повышенном внутреннем разрешении:

```bash
python SVGify.py logo.png --max-size 4000
```

Удалять мелкие фрагменты контуров:

```bash
python SVGify.py logo.png --min-area 12
```

## Параметры командной строки

```text
inputs                  Файлы, папки или ZIP-архивы
-o, --output PATH       Папка сохранения
-c, --colors NUMBER     Количество цветов от 2 до 64
-d, --detail NUMBER     Детализация контуров от 1 до 100
-b, --background MODE   Режим фона: auto, on или off
--max-size NUMBER       Максимальный внутренний размер изображения
--min-area NUMBER       Минимальная площадь контура
--no-denoise            Отключить шумоподавление
```

## Режимы удаления фона

### `auto`

Удаляет фон только при необходимости. Прозрачные изображения обычно сохраняют существующий альфа-канал.

```bash
python SVGify.py logo.png --background auto
```

### `on`

Всегда пытается удалить фон.

```bash
python SVGify.py photo.jpg --background on
```

### `off`

Сохраняет исходный фон.

```bash
python SVGify.py image.png --background off
```

## Рекомендуемые настройки

### Простой плоский логотип

```bash
python SVGify.py logo.png --colors 6 --detail 80 --background auto
```

### Детализированный многоцветный логотип

```bash
python SVGify.py logo.png --colors 24 --detail 90 --background auto
```

### Логотип на сложной фотографии

```bash
python SVGify.py photo.jpg --colors 16 --detail 85 --background on
```

### Более чистый и компактный SVG

```bash
python SVGify.py logo.png --colors 8 --detail 60 --min-area 15
```

## Результат

SVG-файлы сохраняются в выбранную папку.

Папки по умолчанию:

- Windows: `Downloads\SVGify`
- Linux и macOS: `~/Downloads/SVGify`
- Android-совместимые среды: `/storage/emulated/0/Download/SVGify`

Существующие файлы не перезаписываются. SVGify добавляет числовой суффикс, например `_2` или `_3`.

## Конфигурация

Настройки интерактивного режима хранятся в файле:

```text
~/.svgify_memory.json
```

Чтобы восстановить настройки по умолчанию, удалите этот файл.

## Решение проблем

### Не открываются RAW-файлы

Убедитесь, что установлен пакет `rawpy`:

```bash
pip install --upgrade rawpy
```

### Не открываются HEIC или HEIF

Установите или обновите Pillow HEIF:

```bash
pip install --upgrade pillow-heif
```

### Не открываются PDF

Установите или обновите PyMuPDF:

```bash
pip install --upgrade pymupdf
```

### Не обрабатывается входной SVG

Установите CairoSVG и необходимые системные библиотеки Cairo:

```bash
pip install --upgrade cairosvg
```

### Не работает удаление фона

Установите или обновите пакеты удаления фона:

```bash
pip install --upgrade rembg onnxruntime
```

### В SVG слишком много мелких фигур

Уменьшите детализацию или увеличьте минимальную площадь контура:

```bash
python SVGify.py logo.png --detail 60 --min-area 15
```

### Цвета выглядят слишком упрощенно

Увеличьте количество цветов:

```bash
python SVGify.py logo.png --colors 24
```

### Обработка выполняется медленно

Уменьшите внутренний размер изображения:

```bash
python SVGify.py logo.png --max-size 1600
```

## Лицензия

SVGify распространяется на условиях **GNU General Public License v3.0**.

Полный текст лицензии находится в файле [LICENSE](LICENSE).
