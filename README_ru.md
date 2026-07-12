# SVGify

🌐 [English](README.md) | **Русский**

SVGify преобразует логотипы и растровые изображения в аккуратную цветную SVG-графику прямо из терминала.

Программа обрабатывает отдельные изображения, целые папки и ZIP-архивы. Она умеет удалять фон, сокращать цветовую палитру, сглаживать контуры и сохранять результат в редактируемом формате SVG.

> Автоматическая трассировка не может восстановить детали, которых нет в исходном изображении. Лучший результат дают четкие фотографии высокого разрешения с равномерным освещением и простым фоном.

## Быстрый запуск

```bash
git clone https://github.com/Datvex/SVGify.git
cd SVGify
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python SVGify.py
```

Пользователям Windows следует использовать инструкцию для PowerShell ниже.

## Установка

Для работы SVGify требуется Python 3.10 или новее. Каждая инструкция ниже клонирует репозиторий, создает изолированное окружение, устанавливает все Python-зависимости из `requirements.txt` и запускает программу.

### Windows

Откройте PowerShell и выполните:

```powershell
git clone https://github.com/Datvex/SVGify.git
cd SVGify
py -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python SVGify.py
```

Если команда `py` недоступна, замените ее на `python`. Git и Python можно установить через `winget`:

```powershell
winget install --id Git.Git -e
winget install --id Python.Python.3.12 -e
```

После установки перезапустите PowerShell и выполните основные команды установки.

### macOS

Установите системные зависимости через Homebrew:

```bash
brew install python git cairo libffi
git clone https://github.com/Datvex/SVGify.git
cd SVGify
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python SVGify.py
```

Если Homebrew еще не установлен:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Ubuntu и Debian

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git libcairo2 libffi-dev
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
sudo pacman -Syu --needed python python-pip git cairo libffi
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
sudo dnf install -y python3 python3-pip git cairo libffi-devel
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
sudo zypper install -y python3 python3-pip python3-virtualenv git cairo-devel libffi-devel
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
sudo emerge --ask dev-lang/python dev-vcs/git x11-libs/cairo dev-libs/libffi
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
sudo apk add python3 py3-pip py3-virtualenv git cairo-dev libffi-dev build-base
git clone https://github.com/Datvex/SVGify.git
cd SVGify
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python SVGify.py
```

### Termux

Устанавливайте Termux из F-Droid или GitHub. Версия из Google Play устарела.

```bash
pkg update
pkg upgrade
pkg install python git clang make pkg-config libffi cairo
git clone https://github.com/Datvex/SVGify.git
cd SVGify
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python SVGify.py
```

Некоторые библиотеки машинного обучения не публикуют официальные пакеты для Android. Если `onnxruntime` или `rembg` не устанавливаются в Termux, удаление фона через эти библиотеки будет недоступно, но встроенная обработка SVGify продолжит работать.

## Использование

Для запуска интерактивного интерфейса:

```bash
python SVGify.py
```

Для преобразования одного изображения без открытия меню:

```bash
python SVGify.py logo.png
```

Файлы, папки и ZIP-архивы можно передавать одновременно:

```bash
python SVGify.py logo.png ./brand-assets icons.zip
```

Для выбора другой папки сохранения:

```bash
python SVGify.py logo.png --output ./output
```

Для настройки векторизации:

```bash
python SVGify.py logo.png --colors 16 --detail 85 --background auto
```

## Параметры командной строки

| Параметр | Назначение |
| --- | --- |
| `inputs` | Изображения, папки или ZIP-архивы |
| `-o`, `--output PATH` | Папка сохранения |
| `-c`, `--colors NUMBER` | Количество цветов от 2 до 64 |
| `-d`, `--detail NUMBER` | Детализация контуров от 1 до 100 |
| `-b`, `--background MODE` | Режим фона: `auto`, `on` или `off` |
| `--max-size NUMBER` | Максимальный размер изображения при обработке |
| `--min-area NUMBER` | Минимальная площадь сохраняемого контура |
| `--no-denoise` | Отключение шумоподавления |

Режим `auto` удаляет фон только при необходимости. Используйте `on` для логотипа, снятого на сложной поверхности, и `off`, если фон должен остаться частью изображения.

## Поддерживаемые форматы

| Категория | Форматы |
| --- | --- |
| Обычные изображения | PNG, JPG, JPEG, JFIF, WebP, BMP, GIF, TIFF, ICO, TGA |
| Portable maps | PPM, PGM, PBM, PNM |
| Современные изображения | HEIC, HEIF, AVIF |
| Камерные RAW-файлы | RAW, DNG, CR2, CR3, NEF, ARW, ORF, RW2, RAF, PEF, SRW |
| Документы и векторы | PDF, SVG |
| Архивы | ZIP |

Для PDF обрабатывается первая страница, а для анимированного изображения первый кадр. Папки сканируются рекурсивно.

## Выбор настроек

Для простого плоского логотипа обычно достаточно от 4 до 8 цветов. Детализированной графике может потребоваться от 16 до 32 цветов, но большая палитра увеличивает размер SVG.

```bash
python SVGify.py logo.png --colors 8 --detail 75 --background auto
```

Для логотипа на сложной фотографии:

```bash
python SVGify.py photo.jpg --colors 16 --detail 85 --background on
```

Для более компактного и чистого SVG уменьшите детализацию и удалите мелкие контуры:

```bash
python SVGify.py logo.png --colors 8 --detail 60 --min-area 15
```

## Результаты и конфигурация

По умолчанию результаты сохраняются в `Downloads/SVGify`. Существующие файлы не перезаписываются: при совпадении имени программа добавляет суффикс `_2`, `_3` и так далее.

Настройки интерактивного режима хранятся в файле:

```text
~/.svgify_memory.json
```

Удалите этот файл, чтобы восстановить настройки по умолчанию.

## Решение проблем

Если SVGify не открывает RAW, HEIC, PDF или SVG, сначала переустановите зависимости проекта внутри активного виртуального окружения:

```bash
python -m pip install --upgrade -r requirements.txt
```

Для CairoSVG также может потребоваться системная библиотека Cairo. В приведенных выше инструкциях она устанавливается вместе с остальными системными пакетами.

Если SVG содержит слишком много мелких элементов, увеличьте `--min-area` или уменьшите `--detail`. Если цвета выглядят слишком упрощенно, увеличьте `--colors`. Уменьшение `--max-size` снижает расход памяти и ускоряет обработку.

## Лицензия

SVGify распространяется на условиях [GNU General Public License v3.0](LICENSE).

Лицензия разрешает использовать, изучать, изменять и распространять проект при соблюдении ее условий.
