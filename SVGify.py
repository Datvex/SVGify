import os
import sys
import json
import math
import time
import atexit
import shutil
import zipfile
import tempfile
import argparse
import urllib.parse
import unicodedata
import textwrap
from pathlib import Path
from collections import deque

from PIL import Image, ImageOps, ImageFilter

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except Exception:
    pass

try:
    import vtracer
except Exception:
    vtracer = None

C_BLUE = "\033[38;2;0;175;255m"
C_YELLOW = "\033[38;2;248;246;117m"
C_GRAY = "\033[38;2;110;110;110m"
C_WHITE = "\033[38;2;210;210;210m"
C_DARK_GRAY = "\033[38;2;80;80;80m"
C_GREEN = "\033[38;2;90;220;140m"
C_RED = "\033[38;2;255;100;100m"
C_BOLD = "\033[1m"
C_RESET = "\033[0m"
C_BG_INPUT = "\033[48;2;45;45;45m"

SUPPORTED_EXTS = {
    ".png", ".jpg", ".jpeg", ".jfif", ".webp", ".bmp", ".dib", ".gif",
    ".tif", ".tiff", ".ico", ".ppm", ".pgm", ".pbm", ".pnm", ".tga",
    ".heic", ".heif", ".avif", ".raw", ".dng", ".cr2", ".cr3", ".nef",
    ".arw", ".orf", ".rw2", ".raf", ".pef", ".srw", ".pdf", ".svg"
}

RAW_EXTS = {
    ".raw", ".dng", ".cr2", ".cr3", ".nef", ".arw", ".orf", ".rw2",
    ".raf", ".pef", ".srw"
}

ARCHIVE_EXTS = {".zip"}

IGNORE_DIRS = {
    ".git", "node_modules", "venv", "env", ".venv", "__pycache__",
    ".idea", ".vscode", "dist", "build"
}

MEMORY_FILE = Path.home() / ".svgify_memory.json"

T = {
    "en": {
        "commands": "Commands",
        "actions": "Actions",
        "start": "Convert logos to SVG",
        "settings": "Settings",
        "system": "System",
        "output_path": "Output path",
        "colors": "Color level",
        "detail": "Detail",
        "background": "Background removal",
        "language": "Language",
        "tip_main": "Type a number to select, or Ctrl+C to exit",
        "action": "Action:",
        "input": "Input",
        "input_help": "Enter paths to images, PDF files, SVG files, ZIP archives or folders.",
        "path": "Path:",
        "not_found": "No supported files found.",
        "processing": "Vectorizing",
        "success": "Success",
        "success_msg": "Vectorization completed.",
        "output_loc": "Output location",
        "failed": "Failed",
        "press_enter": "Press Enter to return",
        "change_path": "Change output path",
        "change_colors": "Change color level",
        "change_detail": "Change contour detail",
        "change_background": "Change background removal",
        "change_language": "Change language",
        "new_path": "New path:",
        "new_colors": "Color level from 2 to 64:",
        "new_detail": "Detail from 1 to 100:",
        "auto": "Auto",
        "on": "Enabled",
        "off": "Disabled",
        "back": "Back",
        "exit": "Exit",
        "missing_vtracer": "VTracer is not installed. Run: python -m pip install -r requirements.txt"
    },
    "ru": {
        "commands": "Команды",
        "actions": "Действия",
        "start": "Преобразовать логотипы в SVG",
        "settings": "Настройки",
        "system": "Система",
        "output_path": "Путь сохранения",
        "colors": "Уровень цветов",
        "detail": "Детализация",
        "background": "Удаление фона",
        "language": "Язык",
        "tip_main": "Введите номер для выбора, или Ctrl+C для выхода",
        "action": "Действие:",
        "input": "Ввод",
        "input_help": "Введите пути к изображениям, PDF, SVG, ZIP-архивам или папкам.",
        "path": "Путь:",
        "not_found": "Поддерживаемые файлы не найдены.",
        "processing": "Векторизация",
        "success": "Успешно",
        "success_msg": "Векторизация завершена.",
        "output_loc": "Место сохранения",
        "failed": "Ошибка",
        "press_enter": "Нажмите Enter для возврата",
        "change_path": "Изменить путь сохранения",
        "change_colors": "Изменить уровень цветов",
        "change_detail": "Изменить детализацию контуров",
        "change_background": "Изменить удаление фона",
        "change_language": "Изменить язык",
        "new_path": "Новый путь:",
        "new_colors": "Уровень цветов от 2 до 64:",
        "new_detail": "Детализация от 1 до 100:",
        "auto": "Авто",
        "on": "Включено",
        "off": "Отключено",
        "back": "Назад",
        "exit": "Выход",
        "missing_vtracer": "VTracer не установлен. Выполните: python -m pip install -r requirements.txt"
    },
    "zh": {
        "commands": "命令",
        "actions": "操作",
        "start": "将徽标转换为 SVG",
        "settings": "设置",
        "system": "系统",
        "output_path": "输出路径",
        "colors": "颜色级别",
        "detail": "细节",
        "background": "背景移除",
        "language": "语言",
        "tip_main": "输入数字进行选择，或按 Ctrl+C 退出",
        "action": "操作:",
        "input": "输入",
        "input_help": "输入图像、PDF、SVG、ZIP 压缩包或文件夹的路径。",
        "path": "路径:",
        "not_found": "未找到支持的文件。",
        "processing": "矢量化",
        "success": "成功",
        "success_msg": "矢量化完成。",
        "output_loc": "输出位置",
        "failed": "错误",
        "press_enter": "按 Enter 返回",
        "change_path": "更改输出路径",
        "change_colors": "更改颜色级别",
        "change_detail": "更改轮廓细节",
        "change_background": "更改背景移除",
        "change_language": "更改语言",
        "new_path": "新路径:",
        "new_colors": "颜色级别 2 到 64:",
        "new_detail": "细节 1 到 100:",
        "auto": "自动",
        "on": "启用",
        "off": "禁用",
        "back": "返回",
        "exit": "退出",
        "missing_vtracer": "未安装 VTracer。运行: python -m pip install -r requirements.txt"
    }
}


def enable_ansi():
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)
            mode = ctypes.c_uint32()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                kernel32.SetConsoleMode(handle, mode.value | 0x0004)
        except Exception:
            pass


def restore_console():
    sys.stdout.write(f"{C_RESET}\033[?25h")
    sys.stdout.flush()


atexit.register(restore_console)


def char_width(ch):
    if unicodedata.combining(ch):
        return 0
    return 2 if unicodedata.east_asian_width(ch) in ("F", "W") else 1


def text_width(text):
    return sum(char_width(ch) for ch in str(text))


def truncate_text(text, max_len):
    text = str(text)

    if max_len <= 0:
        return ""

    if text_width(text) <= max_len:
        return text

    if max_len <= 3:
        return "." * max_len

    result = ""
    width = 0

    for ch in text:
        current = char_width(ch)

        if width + current > max_len - 3:
            break

        result += ch
        width += current

    return result + "..."


def get_term_width():
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 80


def get_layout():
    terminal_width = get_term_width()
    block_width = max(20, min(terminal_width - 4, 76))
    margin = " " * max(0, (terminal_width - block_width) // 2)
    return terminal_width, block_width, margin


def clear_screen(lines=18):
    sys.stdout.write(f"{C_RESET}\033[2J\033[H")

    try:
        terminal_height = os.get_terminal_size().lines
        padding = max(0, (terminal_height - lines) // 2)

        if padding:
            sys.stdout.write("\n" * padding)
    except OSError:
        pass

    sys.stdout.flush()


def print_wrapped_text(text, margin, width, color=C_GRAY):
    lines = textwrap.wrap(
        str(text),
        width=max(10, width),
        break_long_words=False,
        break_on_hyphens=False
    )

    for line in lines or [""]:
        print(f"{margin}{color}{line}{C_RESET}")


def draw_logo():
    logo = [
        "███████ ██    ██  ██████  ██ ███████ ██    ██",
        "██      ██    ██ ██       ██ ██       ██    ██",
        "███████  ██  ██  ██   ███ ██ █████     ████  ",
        "     ██   ████   ██    ██ ██ ██         ██   ",
        "███████    ██     ██████  ██ ██         ██   "
    ]

    terminal_width = get_term_width()
    print()

    for line in logo:
        margin = " " * max(0, (terminal_width - len(line)) // 2)
        print(f"{margin}{C_YELLOW}{line}{C_RESET}")

    print()


def draw_header(margin, width, title):
    spaces = " " * max(1, width - text_width(title))
    print(f"{margin}{C_WHITE}{C_BOLD}{title}{C_RESET}{spaces}\n")


def draw_menu_item(margin, number, text):
    print(f"{margin}{C_YELLOW}{number}{C_RESET}  {C_WHITE}{text}{C_RESET}")


def draw_sys_item(margin, width, label, value):
    prefix = f"{label}   "
    displayed = truncate_text(value, max(1, width - text_width(prefix)))
    print(f"{margin}{C_WHITE}{prefix}{C_RESET}{C_GRAY}{displayed}{C_RESET}")


def print_tip(text, margin, width):
    lines = textwrap.wrap(
        str(text),
        width=max(10, width - 6),
        break_long_words=False,
        break_on_hyphens=False
    )

    if lines:
        print(f"\n{margin}{C_YELLOW}● Tip{C_RESET} {C_GRAY}{lines[0]}{C_RESET}")

        for line in lines[1:]:
            print(f"{margin}      {C_GRAY}{line}{C_RESET}")

    print()


def ask(prompt):
    try:
        return input(
            f"{C_BLUE}▌{C_BG_INPUT}{C_GRAY} {prompt} "
            f"{C_RESET}{C_WHITE}"
        ).strip()
    finally:
        sys.stdout.write(C_RESET)


def wait_return(text):
    try:
        input(f"\n{C_GRAY}{text}:{C_RESET} ")
    except EOFError:
        pass


def show_message(lang, title, message, color=C_YELLOW):
    clear_screen(13)
    draw_logo()
    _, width, margin = get_layout()
    draw_header(margin, width, title)
    print_wrapped_text(message, margin, width, color)
    wait_return(T[lang]["press_enter"])


def clean_path(path):
    if not path:
        return ""

    path = str(path).strip(" \r\n\t")

    if len(path) >= 2 and path[0] == path[-1] and path[0] in ("'", '"'):
        path = path[1:-1]

    if path.startswith("file://"):
        path = urllib.parse.unquote(path[7:])

        if (
            sys.platform == "win32"
            and path.startswith("/")
            and len(path) > 2
            and path[2] == ":"
        ):
            path = path[1:]

    return os.path.normpath(os.path.expanduser(path))


def split_paths(raw):
    raw = raw.strip()
    direct = clean_path(raw)

    if os.path.exists(direct):
        return [direct]

    try:
        import shlex
        tokens = shlex.split(raw, posix=os.name != "nt")
    except Exception:
        tokens = raw.split()

    result = []
    index = 0

    while index < len(tokens):
        found = None
        found_index = index

        for end in range(index, len(tokens)):
            candidate = clean_path(" ".join(tokens[index:end + 1]))

            if os.path.exists(candidate):
                found = candidate
                found_index = end

        if found:
            result.append(found)
            index = found_index + 1
        else:
            index += 1

    return result


def get_default_output():
    if sys.platform == "win32":
        home = os.environ.get("USERPROFILE", str(Path.home()))
        return os.path.join(home, "Downloads", "SVGify")

    if "ANDROID_ROOT" in os.environ:
        return "/storage/emulated/0/Download/SVGify"

    return os.path.join(str(Path.home()), "Downloads", "SVGify")


def default_config():
    return {
        "lang": "ru",
        "output": get_default_output(),
        "colors": 16,
        "detail": 75,
        "background": "auto",
        "max_size": 2400,
        "min_area": 6,
        "background_tolerance": 34
    }


def load_config():
    config = default_config()

    try:
        if MEMORY_FILE.exists():
            with open(MEMORY_FILE, "r", encoding="utf-8") as file:
                saved = json.load(file)

                if isinstance(saved, dict):
                    config.update(saved)
    except Exception:
        pass

    if config["lang"] not in T:
        config["lang"] = "ru"

    return config


def save_config(config):
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as file:
            json.dump(config, file, ensure_ascii=False, indent=4)
    except Exception:
        pass


def unique_output_path(path):
    path = Path(path)

    if not path.exists():
        return str(path)

    index = 2

    while True:
        candidate = path.with_name(f"{path.stem}_{index}{path.suffix}")

        if not candidate.exists():
            return str(candidate)

        index += 1


def safe_extract_zip(path, destination):
    root = os.path.abspath(destination)

    with zipfile.ZipFile(path, "r") as archive:
        for member in archive.infolist():
            target = os.path.abspath(os.path.join(root, member.filename))

            try:
                safe = os.path.commonpath([root, target]) == root
            except ValueError:
                safe = False

            if safe:
                archive.extract(member, root)


def collect_inputs(paths):
    files = []
    temporary = []
    seen = set()

    def add_file(path):
        absolute = os.path.abspath(path)

        if absolute in seen:
            return

        if Path(absolute).suffix.lower() in SUPPORTED_EXTS:
            seen.add(absolute)
            files.append(absolute)

    def walk(path):
        if os.path.isdir(path):
            for root, directories, names in os.walk(path):
                directories[:] = [
                    name
                    for name in sorted(directories)
                    if name not in IGNORE_DIRS
                ]

                for name in sorted(names):
                    child = os.path.join(root, name)
                    extension = Path(child).suffix.lower()

                    if extension in ARCHIVE_EXTS:
                        temporary_directory = tempfile.mkdtemp(
                            prefix="svgify_"
                        )
                        temporary.append(temporary_directory)

                        try:
                            safe_extract_zip(child, temporary_directory)
                            walk(temporary_directory)
                        except Exception:
                            pass
                    else:
                        add_file(child)

        elif os.path.isfile(path):
            extension = Path(path).suffix.lower()

            if extension in ARCHIVE_EXTS:
                temporary_directory = tempfile.mkdtemp(prefix="svgify_")
                temporary.append(temporary_directory)
                safe_extract_zip(path, temporary_directory)
                walk(temporary_directory)
            else:
                add_file(path)

    for source in paths:
        walk(source)

    return files, temporary


def load_raw(path):
    try:
        import rawpy
    except Exception as error:
        raise RuntimeError("RAW support requires rawpy") from error

    with rawpy.imread(path) as raw:
        rgb = raw.postprocess(
            use_camera_wb=True,
            no_auto_bright=False,
            output_bps=8,
            gamma=(2.222, 4.5)
        )

    return Image.fromarray(rgb, "RGB").convert("RGBA")


def load_pdf(path):
    try:
        import fitz
    except Exception as error:
        raise RuntimeError("PDF support requires PyMuPDF") from error

    document = fitz.open(path)

    try:
        if document.page_count < 1:
            raise RuntimeError("PDF has no pages")

        page = document.load_page(0)
        pixmap = page.get_pixmap(matrix=fitz.Matrix(3.0, 3.0), alpha=True)
        mode = "RGBA" if pixmap.alpha else "RGB"

        return Image.frombytes(
            mode,
            (pixmap.width, pixmap.height),
            pixmap.samples
        ).convert("RGBA")
    finally:
        document.close()


def load_image(path):
    extension = Path(path).suffix.lower()

    if extension in RAW_EXTS:
        return load_raw(path)

    if extension == ".pdf":
        return load_pdf(path)

    with Image.open(path) as source:
        try:
            source.seek(0)
        except Exception:
            pass

        return ImageOps.exif_transpose(source).convert("RGBA")


def resize_for_processing(image, max_size):
    width, height = image.size
    longest = max(width, height)

    if longest <= max_size:
        return image

    ratio = max_size / float(longest)
    target = (
        max(1, round(width * ratio)),
        max(1, round(height * ratio))
    )

    return image.resize(target, Image.Resampling.LANCZOS)


def color_distance(first, second):
    red = first[0] - second[0]
    green = first[1] - second[1]
    blue = first[2] - second[2]
    return math.sqrt(red * red + green * green + blue * blue)


def median(values):
    values = sorted(values)
    length = len(values)

    if not length:
        return 0

    middle = length // 2

    if length % 2:
        return values[middle]

    return (values[middle - 1] + values[middle]) / 2


def sample_border(image, limit=2000):
    rgb = image.convert("RGB")
    width, height = rgb.size
    pixels = rgb.load()
    perimeter = max(1, width * 2 + height * 2)
    step = max(1, perimeter // limit)
    samples = []

    for x in range(0, width, step):
        samples.append(pixels[x, 0])

        if height > 1:
            samples.append(pixels[x, height - 1])

    for y in range(0, height, step):
        samples.append(pixels[0, y])

        if width > 1:
            samples.append(pixels[width - 1, y])

    return samples


def estimate_background(image):
    samples = sample_border(image)

    if not samples:
        return (255, 255, 255), 0

    background = (
        int(median([pixel[0] for pixel in samples])),
        int(median([pixel[1] for pixel in samples])),
        int(median([pixel[2] for pixel in samples]))
    )

    distances = [
        color_distance(pixel, background)
        for pixel in samples
    ]

    return background, median(distances)


def remove_connected_background(image, tolerance):
    image = image.convert("RGBA")
    width, height = image.size
    pixels = image.load()
    background, spread = estimate_background(image)
    threshold = max(float(tolerance), min(72.0, spread * 2.8 + 12.0))
    visited = bytearray(width * height)
    background_mask = Image.new("L", (width, height), 255)
    mask_pixels = background_mask.load()
    queue = deque()

    def add(x, y):
        index = y * width + x

        if visited[index]:
            return

        visited[index] = 1

        if color_distance(pixels[x, y], background) <= threshold:
            queue.append((x, y))

    for x in range(width):
        add(x, 0)

        if height > 1:
            add(x, height - 1)

    for y in range(height):
        add(0, y)

        if width > 1:
            add(width - 1, y)

    while queue:
        x, y = queue.popleft()
        mask_pixels[x, y] = 0

        if x > 0:
            add(x - 1, y)

        if x + 1 < width:
            add(x + 1, y)

        if y > 0:
            add(x, y - 1)

        if y + 1 < height:
            add(x, y + 1)

    background_mask = background_mask.filter(
        ImageFilter.GaussianBlur(radius=0.7)
    )

    original_alpha = image.getchannel("A")
    alpha_pixels = original_alpha.load()
    mask_pixels = background_mask.load()
    final_alpha = Image.new("L", (width, height), 0)
    final_pixels = final_alpha.load()

    for y in range(height):
        for x in range(width):
            final_pixels[x, y] = min(
                alpha_pixels[x, y],
                mask_pixels[x, y]
            )

    image.putalpha(final_alpha)
    return image


def prepare_image(image, background_mode, tolerance):
    image = image.convert("RGBA")
    alpha = image.getchannel("A")
    alpha_extrema = alpha.getextrema()
    has_transparency = alpha_extrema[0] < 250

    if background_mode == "off":
        return image

    if background_mode == "auto":
        if has_transparency:
            return image

        _, spread = estimate_background(image)

        if spread > 42:
            return image

    return remove_connected_background(image, tolerance)


def color_precision_from_level(colors):
    colors = max(2, min(64, int(colors)))
    return max(1, min(8, round(math.log2(colors))))


def vtracer_options(config):
    detail = max(1, min(100, int(config["detail"]))) / 100.0
    color_precision = color_precision_from_level(config["colors"])
    layer_difference = max(2, min(64, 48 - color_precision * 5))
    corner_threshold = round(35 + detail * 55)
    length_threshold = round(10.0 - detail * 6.5, 2)
    splice_threshold = round(30 + detail * 35)
    path_precision = max(3, min(8, round(3 + detail * 5)))
    filter_speckle = max(0, int(float(config["min_area"])))

    return {
        "colormode": "color",
        "hierarchical": "stacked",
        "mode": "spline",
        "filter_speckle": filter_speckle,
        "color_precision": color_precision,
        "layer_difference": layer_difference,
        "corner_threshold": corner_threshold,
        "length_threshold": length_threshold,
        "max_iterations": 10,
        "splice_threshold": splice_threshold,
        "path_precision": path_precision
    }


def vectorize_file(source, output_dir, config):
    extension = Path(source).suffix.lower()
    output_path = unique_output_path(
        os.path.join(output_dir, f"{Path(source).stem}.svg")
    )

    if extension == ".svg":
        shutil.copy2(source, output_path)
        return output_path

    if vtracer is None:
        raise RuntimeError(T[config["lang"]]["missing_vtracer"])

    image = load_image(source)
    image = resize_for_processing(image, int(config["max_size"]))
    image = prepare_image(
        image,
        config["background"],
        int(config["background_tolerance"])
    )

    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".png"
        ) as temporary:
            temporary_path = temporary.name

        image.save(temporary_path, "PNG", optimize=True)

        vtracer.convert_image_to_svg_py(
            temporary_path,
            output_path,
            **vtracer_options(config)
        )

        return output_path

    finally:
        if temporary_path and os.path.exists(temporary_path):
            try:
                os.remove(temporary_path)
            except Exception:
                pass


def draw_progress(lang, index, total, name):
    clear_screen(14)
    draw_logo()
    _, width, margin = get_layout()
    draw_header(margin, width, T[lang]["processing"])

    ratio = index / max(1, total)
    bar_width = max(10, min(48, width - 12))
    filled = round(bar_width * ratio)
    bar = "█" * filled + "░" * (bar_width - filled)

    print(f"{margin}{C_YELLOW}{bar}{C_RESET}")
    print(f"\n{margin}{C_WHITE}{index} / {total}{C_RESET}")
    print(f"{margin}{C_GRAY}{truncate_text(name, width)}{C_RESET}")
    sys.stdout.flush()


def run_conversion(config, raw_paths=None):
    lang = config["lang"]
    t = T[lang]

    if vtracer is None:
        show_message(lang, t["failed"], t["missing_vtracer"], C_RED)
        return []

    if raw_paths is None:
        clear_screen(14)
        draw_logo()
        _, width, margin = get_layout()
        draw_header(margin, width, t["input"])
        print_wrapped_text(t["input_help"], margin, width, C_GRAY)
        print()
        raw = ask(t["path"])
        paths = split_paths(raw)
    else:
        paths = [
            clean_path(path)
            for path in raw_paths
            if os.path.exists(clean_path(path))
        ]

    if not paths:
        if raw_paths is None:
            show_message(lang, t["failed"], t["not_found"], C_RED)
        return []

    temporary = []
    results = []
    failures = []

    try:
        files, temporary = collect_inputs(paths)

        if not files:
            if raw_paths is None:
                show_message(lang, t["failed"], t["not_found"], C_RED)
            return []

        os.makedirs(config["output"], exist_ok=True)

        for index, source in enumerate(files, 1):
            draw_progress(
                lang,
                index,
                len(files),
                os.path.basename(source)
            )

            try:
                result = vectorize_file(
                    source,
                    config["output"],
                    config
                )
                results.append(result)
            except Exception as error:
                failures.append((source, str(error)))

            time.sleep(0.03)

    finally:
        for folder in temporary:
            shutil.rmtree(folder, ignore_errors=True)

    if raw_paths is None:
        clear_screen(17)
        draw_logo()
        _, width, margin = get_layout()
        title = t["success"] if results else t["failed"]
        draw_header(margin, width, title)

        if results:
            print(f"{margin}{C_GREEN}{t['success_msg']}{C_RESET}")
            print(f"\n{margin}{C_BLUE}{t['output_loc']}{C_RESET}")
            print_wrapped_text(
                config["output"],
                margin,
                width,
                C_WHITE
            )
            print(f"\n{margin}{C_WHITE}{len(results)} SVG{C_RESET}")

        if failures:
            print(
                f"\n{margin}{C_RED}"
                f"{len(failures)} {t['failed'].lower()}"
                f"{C_RESET}"
            )

            for source, error in failures[:5]:
                print_wrapped_text(
                    f"{os.path.basename(source)}: {error}",
                    margin,
                    width,
                    C_GRAY
                )

        wait_return(t["press_enter"])

    return results


def settings_menu(config):
    while True:
        lang = config["lang"]
        t = T[lang]

        clear_screen(22)
        draw_logo()
        _, width, margin = get_layout()
        draw_header(margin, width, t["settings"])

        draw_menu_item(margin, "1", t["change_path"])
        draw_menu_item(margin, "2", t["change_colors"])
        draw_menu_item(margin, "3", t["change_detail"])
        draw_menu_item(margin, "4", t["change_background"])
        draw_menu_item(margin, "5", t["change_language"])
        draw_menu_item(margin, "0", t["back"])

        print()
        draw_sys_item(
            margin,
            width,
            t["output_path"],
            config["output"]
        )
        draw_sys_item(
            margin,
            width,
            t["colors"],
            str(config["colors"])
        )
        draw_sys_item(
            margin,
            width,
            t["detail"],
            str(config["detail"])
        )
        draw_sys_item(
            margin,
            width,
            t["background"],
            t.get(config["background"], config["background"])
        )

        choice = ask(t["action"])

        if choice == "0":
            save_config(config)
            return

        if choice == "1":
            value = clean_path(ask(t["new_path"]))

            if value:
                try:
                    os.makedirs(value, exist_ok=True)
                    config["output"] = value
                except Exception:
                    pass

        elif choice == "2":
            value = ask(t["new_colors"])

            try:
                config["colors"] = max(2, min(64, int(value)))
            except Exception:
                pass

        elif choice == "3":
            value = ask(t["new_detail"])

            try:
                config["detail"] = max(1, min(100, int(value)))
            except Exception:
                pass

        elif choice == "4":
            modes = ["auto", "on", "off"]
            current = modes.index(config["background"])
            config["background"] = modes[
                (current + 1) % len(modes)
            ]

        elif choice == "5":
            clear_screen(14)
            draw_logo()
            _, width, margin = get_layout()
            draw_header(margin, width, t["language"])
            draw_menu_item(margin, "1", "English")
            draw_menu_item(margin, "2", "Русский")
            draw_menu_item(margin, "3", "中文")
            selected = ask(t["action"])
            mapping = {"1": "en", "2": "ru", "3": "zh"}

            if selected in mapping:
                config["lang"] = mapping[selected]

        save_config(config)


def main_menu(config):
    while True:
        lang = config["lang"]
        t = T[lang]

        clear_screen(20)
        draw_logo()
        _, width, margin = get_layout()
        draw_header(margin, width, t["commands"])

        print(f"{margin}{C_BLUE}{t['actions']}{C_RESET}")
        draw_menu_item(margin, "1", t["start"])
        draw_menu_item(margin, "2", t["settings"])
        draw_menu_item(margin, "0", t["exit"])
        print()

        print(f"{margin}{C_BLUE}{t['system']}{C_RESET}")
        draw_sys_item(
            margin,
            width,
            t["output_path"],
            config["output"]
        )
        draw_sys_item(
            margin,
            width,
            t["colors"],
            str(config["colors"])
        )
        draw_sys_item(
            margin,
            width,
            t["detail"],
            str(config["detail"])
        )
        draw_sys_item(
            margin,
            width,
            t["background"],
            t.get(config["background"], config["background"])
        )

        print_tip(t["tip_main"], margin, width)
        choice = ask(t["action"])

        if choice == "1":
            run_conversion(config)
        elif choice == "2":
            settings_menu(config)
        elif choice == "0":
            return


def parse_arguments():
    parser = argparse.ArgumentParser(prog="SVGify")
    parser.add_argument("inputs", nargs="*")
    parser.add_argument("-o", "--output")
    parser.add_argument("-c", "--colors", type=int)
    parser.add_argument("-d", "--detail", type=int)
    parser.add_argument(
        "-b",
        "--background",
        choices=["auto", "on", "off"]
    )
    parser.add_argument("--max-size", type=int)
    parser.add_argument("--min-area", type=float)
    parser.add_argument("--background-tolerance", type=int)
    return parser.parse_args()


def apply_arguments(config, arguments):
    if arguments.output:
        config["output"] = clean_path(arguments.output)

    if arguments.colors is not None:
        config["colors"] = max(2, min(64, arguments.colors))

    if arguments.detail is not None:
        config["detail"] = max(1, min(100, arguments.detail))

    if arguments.background:
        config["background"] = arguments.background

    if arguments.max_size is not None:
        config["max_size"] = max(256, arguments.max_size)

    if arguments.min_area is not None:
        config["min_area"] = max(0, arguments.min_area)

    if arguments.background_tolerance is not None:
        config["background_tolerance"] = max(
            1,
            min(255, arguments.background_tolerance)
        )

    return config


def main():
    enable_ansi()
    arguments = parse_arguments()
    config = apply_arguments(load_config(), arguments)

    if arguments.inputs:
        os.makedirs(config["output"], exist_ok=True)
        results = run_conversion(config, arguments.inputs)

        for path in results:
            print(path)

        return 0 if results else 1

    try:
        main_menu(config)
        return 0
    except KeyboardInterrupt:
        return 0
    finally:
        save_config(config)


if __name__ == "__main__":
    sys.exit(main())
