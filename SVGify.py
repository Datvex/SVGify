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
from collections import deque, defaultdict
from xml.sax.saxutils import escape

from PIL import Image, ImageOps, ImageFilter

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
C_LOGO = "\033[38;2;248;246;117m"   # #F8F675
C_LOGO_SHADOW = "\033[38;2;90;90;40m"  # #5A5A28

SUPPORTED_EXTS = {
    ".png", ".jpg", ".jpeg", ".jfif", ".webp", ".bmp", ".dib",
    ".gif", ".tif", ".tiff", ".ico", ".ppm", ".pgm", ".pbm",
    ".pnm", ".tga"
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
        "colors": "Colors",
        "detail": "Detail",
        "background": "Background removal",
        "language": "Language",
        "tip_main": "Type a number to select, or Ctrl+C to exit",
        "action": "Action:",
        "input": "Input",
        "input_help": "Enter paths to images, ZIP archives or folders.",
        "path": "Path:",
        "not_found": "No supported files found.",
        "processing": "Vectorizing",
        "success": "Success",
        "success_msg": "Vectorization completed.",
        "output_loc": "Output location",
        "failed": "Failed",
        "press_enter": "Press Enter to return",
        "change_path": "Change output path",
        "change_colors": "Change number of colors",
        "change_detail": "Change contour detail",
        "change_background": "Change background removal",
        "change_language": "Change language",
        "new_path": "New path:",
        "new_colors": "Colors from 2 to 64:",
        "new_detail": "Detail from 1 to 100:",
        "auto": "Auto",
        "on": "Enabled",
        "off": "Disabled",
        "back": "Back",
        "exit": "Exit"
    },
    "ru": {
        "commands": "Команды",
        "actions": "Действия",
        "start": "Преобразовать логотипы в SVG",
        "settings": "Настройки",
        "system": "Система",
        "output_path": "Путь сохранения",
        "colors": "Количество цветов",
        "detail": "Детализация",
        "background": "Удаление фона",
        "language": "Язык",
        "tip_main": "Введите номер для выбора, или Ctrl+C для выхода",
        "action": "Действие:",
        "input": "Ввод",
        "input_help": "Введите пути к изображениям, ZIP-архивам или папкам.",
        "path": "Путь:",
        "not_found": "Поддерживаемые файлы не найдены.",
        "processing": "Векторизация",
        "success": "Успешно",
        "success_msg": "Векторизация завершена.",
        "output_loc": "Место сохранения",
        "failed": "Ошибка",
        "press_enter": "Нажмите Enter для возврата",
        "change_path": "Изменить путь сохранения",
        "change_colors": "Изменить количество цветов",
        "change_detail": "Изменить детализацию",
        "change_background": "Изменить удаление фона",
        "change_language": "Изменить язык",
        "new_path": "Новый путь:",
        "new_colors": "Количество цветов от 2 до 64:",
        "new_detail": "Детализация от 1 до 100:",
        "auto": "Авто",
        "on": "Включено",
        "off": "Отключено",
        "back": "Назад",
        "exit": "Выход"
    },
    "zh": {
        "commands": "命令",
        "actions": "操作",
        "start": "将徽标转换为 SVG",
        "settings": "设置",
        "system": "系统",
        "output_path": "输出路径",
        "colors": "颜色数量",
        "detail": "细节",
        "background": "背景移除",
        "language": "语言",
        "tip_main": "输入数字进行选择，或按 Ctrl+C 退出",
        "action": "操作:",
        "input": "输入",
        "input_help": "输入图像、ZIP 压缩包或文件夹的路径。",
        "path": "路径:",
        "not_found": "未找到支持的文件。",
        "processing": "矢量化",
        "success": "成功",
        "success_msg": "矢量化完成。",
        "output_loc": "输出位置",
        "failed": "错误",
        "press_enter": "按 Enter 返回",
        "change_path": "更改输出路径",
        "change_colors": "更改颜色数量",
        "change_detail": "更改轮廓细节",
        "change_background": "更改背景移除",
        "change_language": "更改语言",
        "new_path": "新路径:",
        "new_colors": "颜色数量 2 到 64:",
        "new_detail": "细节 1 到 100:",
        "auto": "自动",
        "on": "启用",
        "off": "禁用",
        "back": "返回",
        "exit": "退出"
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
    # Каждый символ хранит два вертикальных «пикселя»:
    # ▀ — верхний, ▄ — нижний, █ — оба.
    logo = [
        "▄███████  ████  ████ ███████▄  ▀███▀ ███████▄ ███   ███",
        "▀████▄     ███  ███  ███        ███  ███      ███▄ ▄███",
        "  ▀▀███▄▄  ███  ███  ███  ▄▄▄▄  ███  █████     ▀█████▀",
        "▄▄▄▄▄████  ████████  ███▄▄███   ███  ███         ███",
        "███████▀    ▀████▀   ▀██████▀  █████ ███         ███",
    ]

    def decode_half_blocks(lines):
        width = max(text_width(line) for line in lines)
        pixels = []

        for line in lines:
            line = line.ljust(width)
            upper = []
            lower = []

            for char in line:
                upper.append(char in ("▀", "█"))
                lower.append(char in ("▄", "█"))

            pixels.append(upper)
            pixels.append(lower)

        return pixels, width

    def color_code(color, background=False):
        prefix = 48 if background else 38
        return f"\033[{prefix};2;{color[0]};{color[1]};{color[2]}m"

    def render_pair(upper, lower):
        if upper is None and lower is None:
            return " "

        if upper == lower:
            return f"{color_code(upper)}█{C_RESET}"

        if upper is None:
            return f"{color_code(lower)}▄{C_RESET}"

        if lower is None:
            return f"{color_code(upper)}▀{C_RESET}"

        return (
            f"{color_code(upper)}"
            f"{color_code(lower, background=True)}"
            f"▀{C_RESET}"
        )

    source, logo_width = decode_half_blocks(logo)
    pixel_height = len(source) + 1
    composed = []

    # Сначала строим тень со смещением на один полупиксель вниз,
    # затем накладываем сверху жёлтую надпись.
    for y in range(pixel_height):
        row = []

        for x in range(logo_width):
            has_logo = y < len(source) and source[y][x]
            has_shadow = y > 0 and source[y - 1][x]

            if has_logo:
                row.append((248, 246, 117))
            elif has_shadow:
                row.append((90, 90, 40))
            else:
                row.append(None)

        composed.append(row)

    terminal_width = get_term_width()
    margin = " " * max(0, (terminal_width - logo_width) // 2)

    print()

    for y in range(0, pixel_height, 2):
        upper = composed[y]
        lower = (
            composed[y + 1]
            if y + 1 < pixel_height
            else [None] * logo_width
        )
        rendered = "".join(
            render_pair(upper[x], lower[x])
            for x in range(logo_width)
        ).rstrip()
        print(f"{margin}{rendered}{C_RESET}")

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
        "colors": 12,
        "detail": 75,
        "background": "auto",
        "max_size": 1600,
        "min_area": 8,
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


def load_image(path):
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
        return image, width, height

    ratio = max_size / float(longest)
    target = (
        max(1, round(width * ratio)),
        max(1, round(height * ratio))
    )

    return (
        image.resize(target, Image.Resampling.LANCZOS),
        width,
        height
    )


def color_distance(first, second):
    red = first[0] - second[0]
    green = first[1] - second[1]
    blue = first[2] - second[2]
    return math.sqrt(red * red + green * green + blue * blue)


def median(values):
    values = sorted(values)

    if not values:
        return 0

    middle = len(values) // 2

    if len(values) % 2:
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
    mask = Image.new("L", (width, height), 255)
    mask_pixels = mask.load()
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

    mask = mask.filter(ImageFilter.GaussianBlur(radius=0.65))
    original_alpha = image.getchannel("A")
    original_pixels = original_alpha.load()
    mask_pixels = mask.load()
    final_alpha = Image.new("L", (width, height), 0)
    final_pixels = final_alpha.load()

    for y in range(height):
        for x in range(width):
            final_pixels[x, y] = min(
                original_pixels[x, y],
                mask_pixels[x, y]
            )

    image.putalpha(final_alpha)
    return image


def prepare_image(image, background_mode, tolerance):
    image = image.convert("RGBA")

    if background_mode == "off":
        return image

    alpha = image.getchannel("A")

    if background_mode == "auto":
        if alpha.getextrema()[0] < 250:
            return image

        _, spread = estimate_background(image)

        if spread > 42:
            return image

    return remove_connected_background(image, tolerance)


def quantize_image(image, colors):
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")
    white = Image.new("RGB", rgba.size, (255, 255, 255))
    white.paste(rgba.convert("RGB"), mask=alpha)

    try:
        quantized = white.quantize(
            colors=max(2, min(64, int(colors))),
            method=Image.Quantize.FASTOCTREE,
            dither=Image.Dither.NONE
        )
    except AttributeError:
        quantized = white.quantize(
            colors=max(2, min(64, int(colors))),
            method=2,
            dither=0
        )

    palette = quantized.getpalette() or []
    used = quantized.getcolors(maxcolors=256) or []
    used.sort(reverse=True)

    colors_by_index = {}

    for _, index in used:
        offset = index * 3

        if offset + 2 < len(palette):
            colors_by_index[index] = (
                palette[offset],
                palette[offset + 1],
                palette[offset + 2]
            )

    return quantized, alpha, colors_by_index


def direction(first, second):
    dx = second[0] - first[0]
    dy = second[1] - first[1]

    if dx > 0:
        return 0

    if dy > 0:
        return 1

    if dx < 0:
        return 2

    return 3


def select_next(previous, current, candidates):
    previous_direction = direction(previous, current)
    priorities = {1: 0, 0: 1, 3: 2, 2: 3}

    return min(
        candidates,
        key=lambda point: priorities[
            (direction(current, point) - previous_direction) % 4
        ]
    )


def build_edges(indices, alpha, target, width, height):
    edges = set()
    index_pixels = indices.load()
    alpha_pixels = alpha.load()

    def matches(x, y):
        return (
            0 <= x < width
            and 0 <= y < height
            and alpha_pixels[x, y] >= 32
            and index_pixels[x, y] == target
        )

    for y in range(height):
        for x in range(width):
            if not matches(x, y):
                continue

            if not matches(x, y - 1):
                edges.add(((x, y), (x + 1, y)))

            if not matches(x + 1, y):
                edges.add(((x + 1, y), (x + 1, y + 1)))

            if not matches(x, y + 1):
                edges.add(((x + 1, y + 1), (x, y + 1)))

            if not matches(x - 1, y):
                edges.add(((x, y + 1), (x, y)))

    return edges


def trace_loops(edges):
    outgoing = defaultdict(set)

    for start, end in edges:
        outgoing[start].add(end)

    remaining = set(edges)
    loops = []

    while remaining:
        start_edge = min(remaining)
        start, current = start_edge
        previous = start
        loop = [start, current]
        remaining.remove(start_edge)
        outgoing[start].discard(current)
        safety = 0

        while current != start and safety <= len(edges) + 4:
            safety += 1
            candidates = [
                point
                for point in outgoing.get(current, ())
                if (current, point) in remaining
            ]

            if not candidates:
                break

            next_point = select_next(previous, current, candidates)
            remaining.remove((current, next_point))
            outgoing[current].discard(next_point)
            previous, current = current, next_point
            loop.append(current)

        if len(loop) >= 4 and loop[-1] == loop[0]:
            loops.append(loop[:-1])

    return loops


def perpendicular_distance(point, start, end):
    if start == end:
        return math.hypot(
            point[0] - start[0],
            point[1] - start[1]
        )

    numerator = abs(
        (end[1] - start[1]) * point[0]
        - (end[0] - start[0]) * point[1]
        + end[0] * start[1]
        - end[1] * start[0]
    )

    denominator = math.hypot(
        end[1] - start[1],
        end[0] - start[0]
    )

    return numerator / denominator


def simplify_open(points, tolerance):
    if len(points) <= 2:
        return points

    start = points[0]
    end = points[-1]
    maximum = 0
    selected = 0

    for index in range(1, len(points) - 1):
        distance = perpendicular_distance(
            points[index],
            start,
            end
        )

        if distance > maximum:
            maximum = distance
            selected = index

    if maximum > tolerance:
        left = simplify_open(points[:selected + 1], tolerance)
        right = simplify_open(points[selected:], tolerance)
        return left[:-1] + right

    return [start, end]


def polygon_area(points):
    total = 0

    for index, point in enumerate(points):
        next_point = points[(index + 1) % len(points)]
        total += point[0] * next_point[1]
        total -= next_point[0] * point[1]

    return total / 2.0


def simplify_closed(points, tolerance):
    if len(points) <= 4:
        return points

    center_x = sum(point[0] for point in points) / len(points)
    center_y = sum(point[1] for point in points) / len(points)

    pivot = max(
        range(len(points)),
        key=lambda index: (
            points[index][0] - center_x
        ) ** 2 + (
            points[index][1] - center_y
        ) ** 2
    )

    rotated = points[pivot:] + points[:pivot]
    simplified = simplify_open(
        rotated + [rotated[0]],
        tolerance
    )

    if simplified and simplified[-1] == simplified[0]:
        simplified.pop()

    return simplified


def remove_collinear(points):
    if len(points) < 3:
        return points

    result = []

    for index, current in enumerate(points):
        previous = points[index - 1]
        following = points[(index + 1) % len(points)]

        first_direction = (
            current[0] - previous[0],
            current[1] - previous[1]
        )
        second_direction = (
            following[0] - current[0],
            following[1] - current[1]
        )

        if (
            first_direction[0] * second_direction[1]
            != first_direction[1] * second_direction[0]
        ):
            result.append(current)

    return result


def format_number(value):
    rounded = round(value, 3)

    if rounded == int(rounded):
        return str(int(rounded))

    return f"{rounded:.3f}".rstrip("0").rstrip(".")


def loop_to_path(points, scale_x, scale_y):
    if len(points) < 3:
        return ""

    first = points[0]
    parts = [
        f"M{format_number(first[0] * scale_x)} "
        f"{format_number(first[1] * scale_y)}"
    ]

    for x, y in points[1:]:
        parts.append(
            f"L{format_number(x * scale_x)} "
            f"{format_number(y * scale_y)}"
        )

    parts.append("Z")
    return " ".join(parts)


def rgb_hex(color):
    return "#{:02x}{:02x}{:02x}".format(*color)


def build_svg(image, original_width, original_height, config, title):
    width, height = image.size
    quantized, alpha, palette = quantize_image(
        image,
        config["colors"]
    )
    scale_x = original_width / float(width)
    scale_y = original_height / float(height)
    detail = max(1, min(100, int(config["detail"])))
    tolerance = 0.15 + (100 - detail) * 0.035
    minimum_area = max(0.1, float(config["min_area"]))
    shapes = []

    usage = quantized.getcolors(maxcolors=256) or []
    usage.sort(reverse=True)

    for count, index in usage:
        if index not in palette:
            continue

        if count < minimum_area:
            continue

        edges = build_edges(
            quantized,
            alpha,
            index,
            width,
            height
        )

        if not edges:
            continue

        loops = trace_loops(edges)
        path_parts = []

        for loop in loops:
            loop = remove_collinear(loop)

            if len(loop) < 3:
                continue

            if abs(polygon_area(loop)) < minimum_area:
                continue

            loop = simplify_closed(loop, tolerance)

            if len(loop) < 3:
                continue

            path = loop_to_path(loop, scale_x, scale_y)

            if path:
                path_parts.append(path)

        if path_parts:
            shapes.append(
                f'<path d="{" ".join(path_parts)}" '
                f'fill="{rgb_hex(palette[index])}" '
                f'fill-rule="evenodd"/>'
            )

    if not shapes:
        raise RuntimeError("No visible vector contours were generated")

    safe_title = escape(title)
    content = "\n  ".join(shapes)

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{original_width}" height="{original_height}" '
        f'viewBox="0 0 {original_width} {original_height}" '
        f'role="img" aria-label="{safe_title}">\n'
        f'  <title>{safe_title}</title>\n'
        f'  {content}\n'
        '</svg>\n'
    )


def vectorize_file(source, output_dir, config):
    output_path = unique_output_path(
        os.path.join(
            output_dir,
            f"{Path(source).stem}.svg"
        )
    )

    image = load_image(source)
    image, original_width, original_height = resize_for_processing(
        image,
        int(config["max_size"])
    )
    image = prepare_image(
        image,
        config["background"],
        int(config["background_tolerance"])
    )

    svg = build_svg(
        image,
        original_width,
        original_height,
        config,
        Path(source).stem
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
        newline="\n"
    ) as file:
        file.write(svg)

    return output_path


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
    translations = T[lang]

    if raw_paths is None:
        clear_screen(14)
        draw_logo()
        _, width, margin = get_layout()
        draw_header(margin, width, translations["input"])
        print_wrapped_text(
            translations["input_help"],
            margin,
            width,
            C_GRAY
        )
        print()
        raw = ask(translations["path"])
        paths = split_paths(raw)
    else:
        paths = [
            clean_path(path)
            for path in raw_paths
            if os.path.exists(clean_path(path))
        ]

    if not paths:
        if raw_paths is None:
            show_message(
                lang,
                translations["failed"],
                translations["not_found"],
                C_RED
            )

        return []

    temporary = []
    results = []
    failures = []

    try:
        files, temporary = collect_inputs(paths)

        if not files:
            if raw_paths is None:
                show_message(
                    lang,
                    translations["failed"],
                    translations["not_found"],
                    C_RED
                )

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
                results.append(
                    vectorize_file(
                        source,
                        config["output"],
                        config
                    )
                )
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
        title = (
            translations["success"]
            if results
            else translations["failed"]
        )
        draw_header(margin, width, title)

        if results:
            print(
                f"{margin}{C_GREEN}"
                f"{translations['success_msg']}"
                f"{C_RESET}"
            )
            print(
                f"\n{margin}{C_BLUE}"
                f"{translations['output_loc']}"
                f"{C_RESET}"
            )
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
                f"{len(failures)} "
                f"{translations['failed'].lower()}"
                f"{C_RESET}"
            )

            for source, error in failures[:5]:
                print_wrapped_text(
                    f"{os.path.basename(source)}: {error}",
                    margin,
                    width,
                    C_GRAY
                )

        wait_return(translations["press_enter"])

    return results


def settings_menu(config):
    while True:
        lang = config["lang"]
        translations = T[lang]

        clear_screen(22)
        draw_logo()
        _, width, margin = get_layout()
        draw_header(margin, width, translations["settings"])

        draw_menu_item(
            margin,
            "1",
            translations["change_path"]
        )
        draw_menu_item(
            margin,
            "2",
            translations["change_colors"]
        )
        draw_menu_item(
            margin,
            "3",
            translations["change_detail"]
        )
        draw_menu_item(
            margin,
            "4",
            translations["change_background"]
        )
        draw_menu_item(
            margin,
            "5",
            translations["change_language"]
        )
        draw_menu_item(
            margin,
            "0",
            translations["back"]
        )

        print()
        draw_sys_item(
            margin,
            width,
            translations["output_path"],
            config["output"]
        )
        draw_sys_item(
            margin,
            width,
            translations["colors"],
            str(config["colors"])
        )
        draw_sys_item(
            margin,
            width,
            translations["detail"],
            str(config["detail"])
        )
        draw_sys_item(
            margin,
            width,
            translations["background"],
            translations.get(
                config["background"],
                config["background"]
            )
        )

        choice = ask(translations["action"])

        if choice == "0":
            save_config(config)
            return

        if choice == "1":
            value = clean_path(ask(translations["new_path"]))

            if value:
                try:
                    os.makedirs(value, exist_ok=True)
                    config["output"] = value
                except Exception:
                    pass

        elif choice == "2":
            value = ask(translations["new_colors"])

            try:
                config["colors"] = max(
                    2,
                    min(64, int(value))
                )
            except Exception:
                pass

        elif choice == "3":
            value = ask(translations["new_detail"])

            try:
                config["detail"] = max(
                    1,
                    min(100, int(value))
                )
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
            draw_header(
                margin,
                width,
                translations["language"]
            )
            draw_menu_item(margin, "1", "English")
            draw_menu_item(margin, "2", "Русс��ий")
            draw_menu_item(margin, "3", "中文")
            selected = ask(translations["action"])
            mapping = {"1": "en", "2": "ru", "3": "zh"}

            if selected in mapping:
                config["lang"] = mapping[selected]

        save_config(config)


def main_menu(config):
    while True:
        lang = config["lang"]
        translations = T[lang]

        clear_screen(20)
        draw_logo()
        _, width, margin = get_layout()
        draw_header(
            margin,
            width,
            translations["commands"]
        )

        print(
            f"{margin}{C_BLUE}"
            f"{translations['actions']}"
            f"{C_RESET}"
        )
        draw_menu_item(
            margin,
            "1",
            translations["start"]
        )
        draw_menu_item(
            margin,
            "2",
            translations["settings"]
        )
        draw_menu_item(
            margin,
            "0",
            translations["exit"]
        )
        print()

        print(
            f"{margin}{C_BLUE}"
            f"{translations['system']}"
            f"{C_RESET}"
        )
        draw_sys_item(
            margin,
            width,
            translations["output_path"],
            config["output"]
        )
        draw_sys_item(
            margin,
            width,
            translations["colors"],
            str(config["colors"])
        )
        draw_sys_item(
            margin,
            width,
            translations["detail"],
            str(config["detail"])
        )
        draw_sys_item(
            margin,
            width,
            translations["background"],
            translations.get(
                config["background"],
                config["background"]
            )
        )

        print_tip(
            translations["tip_main"],
            margin,
            width
        )
        choice = ask(translations["action"])

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
        config["colors"] = max(
            2,
            min(64, arguments.colors)
        )

    if arguments.detail is not None:
        config["detail"] = max(
            1,
            min(100, arguments.detail)
        )

    if arguments.background:
        config["background"] = arguments.background

    if arguments.max_size is not None:
        config["max_size"] = max(
            128,
            arguments.max_size
        )

    if arguments.min_area is not None:
        config["min_area"] = max(
            0.1,
            arguments.min_area
        )

    if arguments.background_tolerance is not None:
        config["background_tolerance"] = max(
            1,
            min(255, arguments.background_tolerance)
        )

    return config


def main():
    enable_ansi()
    arguments = parse_arguments()
    config = apply_arguments(
        load_config(),
        arguments
    )

    if arguments.inputs:
        os.makedirs(config["output"], exist_ok=True)
        results = run_conversion(
            config,
            arguments.inputs
        )

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