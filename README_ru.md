# SVGify

🌐 [English](README.md) | **Русский**

SVGify преобразует растровые изображения в аккуратные цветные SVG прямо из терминала. В первую очередь программа рассчитана на логотипы, иконки, эмблемы, надписи и другую графику с четкими формами и небольшой палитрой.

В проекте используется собственный движок трассировки, написанный на Python. SVGify не использует VTracer, OpenCV, NumPy, внешние консольные программы или онлайн-сервисы. Единственная сторонняя Python-зависимость проекта это Pillow.

Программа умеет обрабатывать одно изображение, несколько файлов, папку или ZIP-архив. Можно работать через интерактивный интерфейс или полностью через параметры командной строки.

> Векторизация не может восстановить детали, которых нет в исходном изображении. Лучший результат дают четкие картинки с хорошим контрастом, заметными границами и простым фоном.

## Как работает движок

Сначала SVGify анализирует изображение и строит компактную палитру. Похожие оттенки, появившиеся из-за JPEG-сжатия и сглаживания, объединяются. Благодаря этому по краям логотипа не создаются сотни мелких цветных слоев.

Затем движок определяет фон, находит границы видимых цветовых областей, обходит замкнутые контуры, сохраняет внутренние отверстия, удаляет мелкие артефакты и упрощает геометрию. Острые углы сохраняются, а лишние пиксельные ступеньки удаляются.

Итоговый файл содержит обычные SVG-пути, составные контуры, `fill-rule="evenodd"`, исходные размеры изображения и соответствующий `viewBox`. Растровая картинка внутрь SVG не встраивается.

## Требования

Для работы SVGify нужен Python 3.10 или новее.

У проекта одна Python-зависимость:

```text
Pillow>=10.0.0,<13.0.0
```

Такая запись подходит для `requirements.txt`. Она разрешает Pillow 10, 11 и 12, но не устанавливает автоматически будущую основную версию, которая еще не проверялась с программой.

## Установка

### Windows

Откройте PowerShell и установите Git и Python, если их еще нет:

```powershell
winget install --id Git.Git -e
winget install --id Python.Python.3.12 -e
```

После установки перезапустите PowerShell и выполните:

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

Если команда `py` недоступна, используйте `python`.

### macOS

Установите Python и Git через Homebrew:

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

Команда установки Homebrew:

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
sudo apk add python3 py3-pip py3-virtualenv git build-base jpeg-dev zlib-dev
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
pkg install python git clang make libjpeg-turbo libpng libwebp
git clone https://github.com/Datvex/SVGify.git
cd SVGify
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python SVGify.py
```

Если для текущей архитектуры Android нет готовой сборки, Pillow может быть скомпилирован локально.

## Использование

Запуск интерактивного интерфейса:

```bash
python SVGify.py
```

Преобразование одного изображения без открытия меню:

```bash
python SVGify.py logo.png
```

Одновременная обработка нескольких файлов, папок и ZIP-архивов:

```bash
python SVGify.py logo.png ./brand-assets icons.zip
```

Выбор другой папки сохранения:

```bash
python SVGify.py logo.png --output ./output
```

Настройка палитры, детализации и режима фона:

```bash
python SVGify.py logo.png --colors 8 --detail 75 --background auto
```

Сохранение исходного фона:

```bash
python SVGify.py logo.jpg --background off
```

## Параметры командной строки

| Параметр | Назначение |
| --- | --- |
| `inputs` | Изображения, папки или ZIP-архивы |
| `-o`, `--output PATH` | Папка сохранения |
| `-c`, `--colors NUMBER` | Сложность палитры от 2 до 64 |
| `-d`, `--detail NUMBER` | Детализация контуров от 1 до 100 |
| `-b`, `--background MODE` | Режим фона: `auto`, `on` или `off` |
| `--max-size NUMBER` | Максимальный размер изображения при трассировке |
| `--min-area NUMBER` | Минимальная площадь контура, сохраняемого в SVG |
| `--background-tolerance NUMBER` | Допуск цвета фона от 1 до 255 |

В режиме `auto` SVGify удаляет достаточно однородный фон, обнаруженный по краям изображения. Уже имеющаяся прозрачность сохраняется. Режим `on` запрашивает удаление фона, а `off` сохраняет исходный фон как часть SVG.

Определение фона рассчитано на однотонные или почти однотонные поверхности. Программа не выполняет семантическое выделение объектов и не использует модель машинного обучения.

## Поддерживаемые форматы

| Категория | Форматы |
| --- | --- |
| Обычные изображения | PNG, JPG, JPEG, JFIF, WebP, BMP, DIB, GIF, TIFF, ICO, TGA |
| Portable maps | PPM, PGM, PBM, PNM |
| Архивы | ZIP |

Папки сканируются рекурсивно. У анимированного изображения используется первый кадр. ZIP-архивы распаковываются во временную папку, которая удаляется после обработки.

Поддержка конкретного формата зависит от кодеков, включенных в установленную сборку Pillow.

## Выбор настроек

Для простого плоского логотипа обычно подходит небольшая палитра и стандартная детализация:

```bash
python SVGify.py logo.png --colors 8 --detail 75 --background auto
```

Для графики с большим количеством цветов можно увеличить палитру:

```bash
python SVGify.py artwork.png --colors 24 --detail 85 --background off
```

Низкая детализация создает меньше сегментов и уменьшает размер SVG. Высокая точнее повторяет мелкие изменения исходного изображения:

```bash
python SVGify.py logo.png --detail 60
python SVGify.py logo.png --detail 90
```

Если из-за сжатия или отдельных пикселей появляются лишние фрагменты, увеличьте `--min-area`:

```bash
python SVGify.py logo.jpg --min-area 12
```

Значение `--colors` задает максимальную сложность палитры, а не точное количество цветов в готовом файле. Если изображение распознано как простая графика, SVGify может автоматически использовать меньше оттенков.

## Результаты и конфигурация

По умолчанию файлы сохраняются в `Downloads/SVGify`. Существующие результаты не перезаписываются. Если такое имя уже занято, SVGify добавляет суффикс `_2`, `_3` и так далее.

Настройки интерактивного режима хранятся в файле:

```text
~/.svgify_memory.json
```

Удалите его, чтобы восстановить стандартные настройки.

## Решение проблем

Если Pillow не импортируется, активируйте окружение проекта и переустановите зависимость:

```bash
python -m pip install --upgrade -r requirements.txt
```

Если формат изображения не открывается, проверьте, поддерживает ли его текущая сборка Pillow. Самый простой обходной вариант обычно состоит в преобразовании исходника в PNG.

Если в SVG появляются мелкие лишние фрагменты, увеличьте `--min-area`. Если контуры выглядят слишком упрощенными, увеличьте `--detail`. Уменьшение `--max-size` снижает расход памяти и ускоряет обработку очень больших изображений.

Если режим `auto` сохраняет фон, попробуйте `--background on`. Для градиентов, теней или детализированного окружения лучше заранее подготовить PNG с прозрачностью.

## Лицензия

SVGify является свободным программным обеспечением и распространяется на условиях [GNU General Public License v3.0](LICENSE).

Лицензия разрешает использовать, изучать, изменять и распространять проект при соблюдении ее условий.