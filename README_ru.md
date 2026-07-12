# SVGify

🌐 [English](README.md) | **Русский**

SVGify преобразует растровые логотипы и фотографии в цветную SVG-графику прямо из терминала. Для трассировки используется VTracer, поэтому проект не зависит от OpenCV.

Программа принимает отдельные изображения, папки, PDF, существующие SVG и ZIP-архивы. Удаление фона, сложность палитры, детализация контуров и фильтрация результата настраиваются через интерактивный интерфейс или параметры командной строки.

> Векторизация не может восстановить детали, отсутствующие в исходном изображении. Лучший результат дают четкие изображения с равномерным освещением, заметными границами и простым фоном.

## Установка

Для работы SVGify требуется Python 3.10 или новее. Каждая инструкция ниже клонирует репозиторий, создает изолированное окружение, устанавливает зависимости из `requirements.txt` и запускает `SVGify.py`.

### Windows

Откройте PowerShell:

```powershell
winget install --id Git.Git -e
winget install --id Python.Python.3.12 -e
git clone https://github.com/Datvex/SVGify.git
cd SVGify
py -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python SVGify.py
```

Если после установки команды Git или Python недоступны, перезапустите PowerShell. Если команда `py` отсутствует, замените ее на `python`.

### macOS

Установите необходимые инструменты через Homebrew:

```bash
brew install python git
git clone https://github.com/Datvex/SVGify.git
cd SVGify
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python SVGify.py
```

Команда установки самого Homebrew:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Ubuntu и Debian

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git
git clone https://github.com/Datvex/SVGify.git
cd SVGify
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python SVGify.py
```

### Arch Linux и Manjaro

```bash
sudo pacman -Syu --needed python python-pip git
git clone https://github.com/Datvex/SVGify.git
cd SVGify
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python SVGify.py
```

### Fedora

```bash
sudo dnf install -y python3 python3-pip git
git clone https://github.com/Datvex/SVGify.git
cd SVGify
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python SVGify.py
```

### openSUSE

```bash
sudo zypper install -y python3 python3-pip python3-virtualenv git
git clone https://github.com/Datvex/SVGify.git
cd SVGify
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python SVGify.py
```

### Gentoo

```bash
sudo emerge --ask dev-lang/python dev-vcs/git
git clone https://github.com/Datvex/SVGify.git
cd SVGify
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python SVGify.py
```

### Alpine Linux

```bash
sudo apk add python3 py3-pip py3-virtualenv git build-base
git clone https://github.com/Datvex/SVGify.git
cd SVGify
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python SVGify.py
```

### Termux

Используйте актуальную версию Termux из F-Droid или GitHub. Версия из Google Play устарела.

```bash
pkg update
pkg upgrade
pkg install python git rust clang make pkg-config libjpeg-turbo libpng libwebp libheif libraw
git clone https://github.com/Datvex/SVGify.git
cd SVGify
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python SVGify.py
```

Некоторые Python-пакеты не выпускают официальные сборки для Android. На неподдерживаемых архитектурах Termux может потребоваться локальная компиляция VTracer, Pillow HEIF, RawPy или PyMuPDF.

## Использование

Запуск интерактивного интерфейса:

```bash
python SVGify.py
```

Преобразование одного изображения без открытия меню:

```bash
python SVGify.py logo.png
```

Файлы, папки и ZIP-архивы можно передавать одновременно:

```bash
python SVGify.py logo.png ./brand-assets icons.zip
```

Выбор другой папки сохранения:

```bash
python SVGify.py logo.png --output ./output
```

Настройка цветов, детализации и удаления фона:

```bash
python SVGify.py logo.png --colors 16 --detail 85 --background auto
```

Для фотографии со сложным фоном можно включить принудительное удаление:

```bash
python SVGify.py photo.jpg --background on --background-tolerance 38
```

## Параметры командной строки

| Параметр | Назначение |
| --- | --- |
| `inputs` | Изображения, PDF, SVG, папки или ZIP-архивы |
| `-o`, `--output PATH` | Папка сохранения |
| `-c`, `--colors NUMBER` | Сложность цветов от 2 до 64 |
| `-d`, `--detail NUMBER` | Детализация контуров от 1 до 100 |
| `-b`, `--background MODE` | Режим фона: `auto`, `on` или `off` |
| `--max-size NUMBER` | Максимальный размер изображения при обработке |
| `--min-area NUMBER` | Уровень фильтрации мелких элементов VTracer |
| `--background-tolerance NUMBER` | Допуск цвета фона от 1 до 255 |

Режим `auto` сохраняет имеющуюся прозрачность и удаляет только достаточно однородный фон, соединенный с краями изображения. Режим `on` всегда пытается удалить фон, а `off` передает VTracer исходное изображение.

Удаление фона рассчитано на однотонные или почти однотонные поверхности. Оно намеренно не использует тяжелую модель машинного обучения и не выполняет семантическое выделение объектов.

## Поддерживаемые форматы

| Категория | Форматы |
| --- | --- |
| Обычные изображения | PNG, JPG, JPEG, JFIF, WebP, BMP, GIF, TIFF, ICO, TGA |
| Portable maps | PPM, PGM, PBM, PNM |
| Современные изображения | HEIC, HEIF, AVIF |
| Камерные RAW-файлы | RAW, DNG, CR2, CR3, NEF, ARW, ORF, RW2, RAF, PEF, SRW |
| Документы и векторы | PDF, SVG |
| Архивы | ZIP |

Существующие SVG копируются без повторной растеризации. Для PDF обрабатывается первая страница, а для анимированного изображения первый кадр. Папки сканируются рекурсивно.

Поддержка конкретного формата изображения также зависит от кодеков Pillow, доступных на используемой платформе.

## Выбор настроек

Для простого плоского логотипа обычно подходит невысокий уровень цветов и средняя или высокая детализация:

```bash
python SVGify.py logo.png --colors 8 --detail 75 --background auto
```

Для детализированной графики можно увеличить уровень цветов:

```bash
python SVGify.py artwork.png --colors 32 --detail 90 --background off
```

Чтобы получить более чистый и компактный SVG, уменьшите детализацию и усильте фильтрацию мелких элементов:

```bash
python SVGify.py logo.png --colors 8 --detail 60 --min-area 12
```

Параметр `--colors` управляет точностью цвета VTracer, а не задает строгое количество цветов. Итоговый SVG может содержать другое число оттенков.

## Результаты и конфигурация

По умолчанию результаты сохраняются в `Downloads/SVGify`. Существующие файлы не перезаписываются: при совпадении имени добавляется суффикс `_2`, `_3` и так далее.

Настройки интерактивного режима хранятся в файле:

```text
~/.svgify_memory.json
```

Удалите этот файл, чтобы восстановить настройки по умолчанию.

## Решение проблем

Если отсутствует какой-либо модуль, переустановите все зависимости внутри активного виртуального окружения:

```bash
python -m pip install --upgrade -r requirements.txt
```

Если не открывается RAW, HEIC или PDF, проверьте, что пакеты `rawpy`, `pillow-heif` и `PyMuPDF` установились без ошибок.

Фон с тенями, градиентами или большим количеством цветов по краям может не удалиться в режиме `auto`. Используйте `--background on`, настройте `--background-tolerance` или заранее подготовьте изображение с прозрачным фоном.

Если SVG содержит слишком много мелких путей, увеличьте `--min-area`. Если контуры слишком упрощены, увеличьте `--detail`. Уменьшение `--max-size` снижает расход памяти и ускоряет обработку.

## Лицензия

SVGify является свободным программным обеспечением и распространяется на условиях [GNU General Public License v3.0](LICENSE).

Лицензия разрешает использовать, изучать, изменять и распространять проект при соблюдении ее условий.
