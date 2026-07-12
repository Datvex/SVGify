import os
import sys
import json
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
from xml.sax.saxutils import escape

import numpy as np
import cv2
from PIL import Image, ImageOps

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except Exception:
    pass

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

COLOR_NORMAL = {
    "blue": "\033[38;2;0;175;255m",
    "yellow": "\033[38;2;248;246;117m",
    "gray": "\033[38;2;110;110;110m",
    "white": "\033[38;2;210;210;210m",
    "dark_gray": "\033[38;2;80;80;80m",
    "green": "\033[38;2;90;220;140m",
    "red": "\033[38;2;255;100;100m",
    "bold": "\033[1m",
    "bg_input": "\033[48;2;45;45;45m"
}

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
        "colors": "Colors",
        "detail": "Detail",
        "background": "Background removal",
        "language": "Language",
        "tip_main": "Type a number to select, or Ctrl+C to exit",
        "action": "Action:",
        "input": "Input",
        "input_help": "Enter paths to images, PDFs, SVG files, ZIP archives or folders.",
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
        "off": "Disabled"
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
        "change_colors": "Изменить количество цветов",
        "change_detail": "Изменить детализацию контуров",
        "change_background": "Изменить удаление фона",
        "change_language": "Изменить язык",
        "new_path": "Новый путь:",
        "new_colors": "Количество цветов от 2 до 64:",
        "new_detail": "Детализация от 1 до 100:",
        "auto": "Авто",
        "on": "Включено",
        "off": "Отключено"
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
        "change_colors": "更改颜色数量",
        "change_detail": "更改轮廓细节",
        "change_background": "更改背景移除",
        "change_language": "更改语言",
        "new_path": "新路径:",
        "new_colors": "颜色数量 2 到 64:",
        "new_detail": "细节 1 到 100:",
        "auto": "自动",
        "on": "启用",
        "off": "禁用"
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
        cw = char_width(ch)
        if width + cw > max_len - 3:
            break
        result += ch
        width += cw
    return result + "..."


def get_term_width():
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 80


def get_layout():
    tw = get_term_width()
    bw = max(20, min(tw - 4, 76))
    return tw, bw, " " * max(0, (tw - bw) // 2)


def clear_screen(lines=18):
    sys.stdout.write(f"{C_RESET}\033[2J\033[H")
    try:
        th = os.get_terminal_size().lines
        padding = max(0, (th - lines) // 2)
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
    tw = get_term_width()
    print()
    for line in logo:
        margin = " " * max(0, (tw - len(line)) // 2)
        print(f"{margin}{C_YELLOW}{line}{C_RESET}")
    print()


def draw_header(margin, width, title):
    spaces = " " * max(1, width - text_width(title))
    print(f"{margin}{C_WHITE}{C_BOLD}{title}{C_RESET}{spaces}\n")


def draw_menu_item(margin, number, text):
    print(f"{margin}{C_YELLOW}{number}{C_RESET}  {C_WHITE}{text}{C_RESET}")


def draw_sys_item(margin, width, label, value):
    left = f"{label}   "
    shown = truncate_text(value, max(1, width - text_width(left)))
    print(f"{margin}{C_WHITE}{left}{C_RESET}{C_GRAY}{shown}{C_RESET}")


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


def clean_path(path):
    if not path:
        return ""
    path = str(path).strip(" \r\n\t")
    if len(path) >= 2 and path[0] == path[-1] and path[0] in ("'", '"'):
        path = path[1:-1]
    if path.startswith("file://"):
        path = urllib.parse.unquote(path[7:])
        if sys.platform == "win32" and path.startswith("/") and len(path) > 2 and path[2] == ":":
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
        return os.path.join(os.environ.get("USERPROFILE", str(Path.home())), "Downloads", "SVGify")
    if "ANDROID_ROOT" in os.environ:
        return "/storage/emulated/0/Download/SVGify"
    return os.path.join(str(Path.home()), "Downloads", "SVGify")


def default_config():
    return {
        "lang": "ru",
        "output": get_default_output(),
        "colors": 12,
        "detail": 70,
        "background": "auto",
        "max_size": 2400,
        "min_area": 6,
        "denoise": 1
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


def ask(prompt):
    try:
        return input(f"{C_BLUE}▌{C_BG_INPUT}{C_GRAY} {prompt} {C_RESET}{C_WHITE}").strip()
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
            if os.path.commonpath([root, target]) != root:
                continue
            archive.extract(member, root)


def collect_inputs(paths):
    files = []
    temporary = []
    seen = set()

    def add_file(path):
        absolute = os.path.abspath(path)
        if absolute in seen:
            return
        extension = Path(absolute).suffix.lower()
        if extension in SUPPORTED_EXTS:
            seen.add(absolute)
            files.append(absolute)

    def walk(path):
        if os.path.isdir(path):
            for root, dirs, names in os.walk(path):
                dirs[:] = [name for name in sorted(dirs) if name not in IGNORE_DIRS]
                for name in sorted(names):
                    child = os.path.join(root, name)
                    extension = Path(child).suffix.lower()
                    if extension in ARCHIVE_EXTS:
                        temp_dir = tempfile.mkdtemp(prefix="svgify_")
                        temporary.append(temp_dir)
                        try:
                            safe_extract_zip(child, temp_dir)
                            walk(temp_dir)
                        except Exception:
                            pass
                    else:
                        add_file(child)
        elif os.path.isfile(path):
            extension = Path(path).suffix.lower()
            if extension in ARCHIVE_EXTS:
                temp_dir = tempfile.mkdtemp(prefix="svgify_")
                temporary.append(temp_dir)
                safe_extract_zip(path, temp_dir)
                walk(temp_dir)
            else:
                add_file(path)

    for source in paths:
        walk(source)

    return files, temporary


def load_raw(path):
    try:
        import rawpy
    except Exception as exc:
        raise RuntimeError("RAW support requires rawpy") from exc
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
    except Exception as exc:
        raise RuntimeError("PDF support requires pymupdf") from exc
    document = fitz.open(path)
    if document.page_count < 1:
        document.close()
        raise RuntimeError("PDF has no pages")
    page = document.load_page(0)
    matrix = fitz.Matrix(3.0, 3.0)
    pixmap = page.get_pixmap(matrix=matrix, alpha=True)
    mode = "RGBA" if pixmap.alpha else "RGB"
    image = Image.frombytes(mode, (pixmap.width, pixmap.height), pixmap.samples)
    document.close()
    return image.convert("RGBA")


def load_svg_preview(path):
    try:
        import cairosvg
    except Exception as exc:
        raise RuntimeError("SVG raster preview requires cairosvg") from exc
    data = cairosvg.svg2png(url=path, output_width=2400, output_height=2400)
    from io import BytesIO
    return Image.open(BytesIO(data)).convert("RGBA")


def load_image(path):
    extension = Path(path).suffix.lower()
    if extension in RAW_EXTS:
        image = load_raw(path)
    elif extension == ".pdf":
        image = load_pdf(path)
    elif extension == ".svg":
        image = load_svg_preview(path)
    else:
        with Image.open(path) as source:
            try:
                source.seek(0)
            except Exception:
                pass
            image = ImageOps.exif_transpose(source).convert("RGBA")
    return image


def resize_for_processing(image, max_size):
    width, height = image.size
    longest = max(width, height)
    if longest <= max_size:
        return image, width, height
    ratio = max_size / float(longest)
    resized = image.resize(
        (max(1, round(width * ratio)), max(1, round(height * ratio))),
        Image.Resampling.LANCZOS
    )
    return resized, width, height


def remove_background_rembg(rgba):
    try:
        from rembg import remove
    except Exception:
        return None
    try:
        image = Image.fromarray(rgba, "RGBA")
        result = remove(image, alpha_matting=True)
        return np.array(result.convert("RGBA"), dtype=np.uint8)
    except Exception:
        return None


def border_pixels(rgb):
    height, width = rgb.shape[:2]
    border = max(1, min(height, width) // 50)
    return np.concatenate([
        rgb[:border].reshape(-1, 3),
        rgb[-border:].reshape(-1, 3),
        rgb[:, :border].reshape(-1, 3),
        rgb[:, -border:].reshape(-1, 3)
    ], axis=0)


def automatic_background_mask(rgb):
    height, width = rgb.shape[:2]
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.float32)
    samples = border_pixels(rgb)
    sample_lab = cv2.cvtColor(
        samples.reshape(-1, 1, 3),
        cv2.COLOR_RGB2LAB
    ).reshape(-1, 3).astype(np.float32)
    center = np.median(sample_lab, axis=0)
    spread = np.median(np.linalg.norm(sample_lab - center, axis=1))
    threshold = float(np.clip(spread * 2.8 + 10.0, 14.0, 48.0))
    distance = np.linalg.norm(lab - center, axis=2)
    candidate = (distance <= threshold).astype(np.uint8)
    flood_source = np.pad(candidate, 1, mode="constant")
    flood = np.zeros_like(flood_source, dtype=np.uint8)
    queue = []

    for x in range(1, width + 1):
        if flood_source[1, x]:
            queue.append((1, x))
        if flood_source[height, x]:
            queue.append((height, x))

    for y in range(1, height + 1):
        if flood_source[y, 1]:
            queue.append((y, 1))
        if flood_source[y, width]:
            queue.append((y, width))

    from collections import deque
    queue = deque(queue)

    while queue:
        y, x = queue.popleft()
        if flood[y, x] or not flood_source[y, x]:
            continue
        flood[y, x] = 1
        queue.append((y - 1, x))
        queue.append((y + 1, x))
        queue.append((y, x - 1))
        queue.append((y, x + 1))

    background = flood[1:-1, 1:-1]
    foreground = (1 - background) * 255
    kernel = np.ones((3, 3), np.uint8)
    foreground = cv2.morphologyEx(foreground, cv2.MORPH_CLOSE, kernel)
    foreground = cv2.GaussianBlur(foreground, (3, 3), 0)
    return foreground


def prepare_rgba(image, background_mode, denoise):
    rgba = np.array(image.convert("RGBA"), dtype=np.uint8)
    rgb = rgba[:, :, :3]
    alpha = rgba[:, :, 3]

    if denoise:
        rgb = cv2.fastNlMeansDenoisingColored(
            cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR),
            None,
            4,
            4,
            7,
            21
        )
        rgb = cv2.cvtColor(rgb, cv2.COLOR_BGR2RGB)

    if background_mode == "on":
        removed = remove_background_rembg(np.dstack([rgb, alpha]))
        if removed is not None:
            return removed
        alpha = np.minimum(alpha, automatic_background_mask(rgb))
    elif background_mode == "auto":
        transparent_ratio = float(np.mean(alpha < 245))
        if transparent_ratio < 0.01:
            removed = remove_background_rembg(np.dstack([rgb, alpha]))
            if removed is not None:
                result_alpha = removed[:, :, 3]
                visible = float(np.mean(result_alpha > 20))
                if 0.01 < visible < 0.98:
                    return removed
            alpha = np.minimum(alpha, automatic_background_mask(rgb))

    return np.dstack([rgb, alpha])


def quantize_colors(rgb, alpha, color_count):
    foreground = alpha > 20
    pixels = rgb[foreground]

    if pixels.size == 0:
        raise RuntimeError("No visible logo pixels detected")

    unique = np.unique(pixels.reshape(-1, 3), axis=0)
    count = max(1, min(color_count, len(unique)))

    if len(pixels) > 250000:
        rng = np.random.default_rng(42)
        sample_indices = rng.choice(len(pixels), 250000, replace=False)
        samples = pixels[sample_indices]
    else:
        samples = pixels

    samples_lab = cv2.cvtColor(
        samples.reshape(-1, 1, 3).astype(np.uint8),
        cv2.COLOR_RGB2LAB
    ).reshape(-1, 3).astype(np.float32)

    criteria = (
        cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
        80,
        0.25
    )

    _, _, centers_lab = cv2.kmeans(
        samples_lab,
        count,
        None,
        criteria,
        5,
        cv2.KMEANS_PP_CENTERS
    )

    centers_rgb = cv2.cvtColor(
        np.clip(centers_lab, 0, 255).astype(np.uint8).reshape(-1, 1, 3),
        cv2.COLOR_LAB2RGB
    ).reshape(-1, 3)

    all_pixels = rgb[foreground]
    labels = np.empty(len(all_pixels), dtype=np.int32)
    chunk_size = 150000

    for start in range(0, len(all_pixels), chunk_size):
        chunk = all_pixels[start:start + chunk_size]
        chunk_lab = cv2.cvtColor(
            chunk.reshape(-1, 1, 3).astype(np.uint8),
            cv2.COLOR_RGB2LAB
        ).reshape(-1, 3).astype(np.float32)
        distance = np.sum(
            (chunk_lab[:, None, :] - centers_lab[None, :, :]) ** 2,
            axis=2
        )
        labels[start:start + len(chunk)] = np.argmin(distance, axis=1)

    label_map = np.full(alpha.shape, -1, dtype=np.int32)
    label_map[foreground] = labels
    counts = np.bincount(labels, minlength=count)
    order = np.argsort(counts)[::-1]

    return label_map, centers_rgb, order, counts


def contour_path(contour, scale_x, scale_y, epsilon):
    perimeter = cv2.arcLength(contour, True)
    approximation = cv2.approxPolyDP(contour, max(0.15, perimeter * epsilon), True)
    points = approximation.reshape(-1, 2)

    if len(points) < 3:
        return ""

    commands = [
        f"M{points[0][0] * scale_x:.3f},{points[0][1] * scale_y:.3f}"
    ]

    for x, y in points[1:]:
        commands.append(f"L{x * scale_x:.3f},{y * scale_y:.3f}")

    commands.append("Z")
    return "".join(commands)


def mask_to_paths(mask, scale_x, scale_y, detail, min_area):
    contours, hierarchy = cv2.findContours(
        mask,
        cv2.RETR_CCOMP,
        cv2.CHAIN_APPROX_TC89_KCOS
    )

    if hierarchy is None:
        return []

    hierarchy = hierarchy[0]
    epsilon = 0.009 * (1.0 - detail / 100.0) + 0.00015
    paths = []

    for index, contour in enumerate(contours):
        if hierarchy[index][3] != -1:
            continue
        if abs(cv2.contourArea(contour)) < min_area:
            continue

        parts = [contour_path(contour, scale_x, scale_y, epsilon)]
        child = hierarchy[index][2]

        while child != -1:
            child_contour = contours[child]
            if abs(cv2.contourArea(child_contour)) >= min_area:
                parts.append(
                    contour_path(
                        child_contour,
                        scale_x,
                        scale_y,
                        epsilon
                    )
                )
            child = hierarchy[child][0]

        combined = "".join(part for part in parts if part)
        if combined:
            paths.append(combined)

    return paths


def rgb_hex(color):
    red, green, blue = [int(value) for value in color]
    return f"#{red:02x}{green:02x}{blue:02x}"


def build_svg(rgba, original_width, original_height, config, title):
    height, width = rgba.shape[:2]
    rgb = rgba[:, :, :3]
    alpha = rgba[:, :, 3]
    labels, centers, order, counts = quantize_colors(
        rgb,
        alpha,
        int(config["colors"])
    )

    scale_x = original_width / float(width)
    scale_y = original_height / float(height)
    min_area = max(1.0, float(config["min_area"]))
    shapes = []

    for label in order:
        if counts[label] < min_area:
            continue

        mask = np.where(
            (labels == int(label)) & (alpha > 20),
            255,
            0
        ).astype(np.uint8)

        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        paths = mask_to_paths(
            mask,
            scale_x,
            scale_y,
            float(config["detail"]),
            min_area
        )

        fill = rgb_hex(centers[label])

        for path in paths:
            shapes.append(
                f'<path d="{path}" fill="{fill}" fill-rule="evenodd"/>'
            )

    if not shapes:
        raise RuntimeError("No vector contours were generated")

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
    extension = Path(source).suffix.lower()
    base_name = Path(source).stem
    output_path = unique_output_path(
        os.path.join(output_dir, f"{base_name}.svg")
    )

    if extension == ".svg":
        shutil.copy2(source, output_path)
        return output_path

    image = load_image(source)
    processed, original_width, original_height = resize_for_processing(
        image,
        int(config["max_size"])
    )
    rgba = prepare_rgba(
        processed,
        config["background"],
        bool(config["denoise"])
    )
    svg = build_svg(
        rgba,
        original_width,
        original_height,
        config,
        base_name
    )

    with open(output_path, "w", encoding="utf-8", newline="\n") as file:
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
    t = T[lang]

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
        paths = [clean_path(path) for path in raw_paths if os.path.exists(clean_path(path))]

    if not paths:
        show_message(lang, t["failed"], t["not_found"], C_RED)
        return []

    temporary = []
    results = []
    failures = []

    try:
        files, temporary = collect_inputs(paths)

        if not files:
            show_message(lang, t["failed"], t["not_found"], C_RED)
            return []

        os.makedirs(config["output"], exist_ok=True)

        for index, source in enumerate(files, 1):
            draw_progress(lang, index, len(files), os.path.basename(source))
            try:
                results.append(
                    vectorize_file(source, config["output"], config)
                )
            except Exception as exc:
                failures.append((source, str(exc)))
            time.sleep(0.03)

    finally:
        for folder in temporary:
            shutil.rmtree(folder, ignore_errors=True)

    if raw_paths is None:
        clear_screen(16)
        draw_logo()
        _, width, margin = get_layout()
        draw_header(margin, width, t["success"])

        print(f"{margin}{C_GREEN}{t['success_msg']}{C_RESET}")
        print(f"\n{margin}{C_BLUE}{t['output_loc']}{C_RESET}")
        print_wrapped_text(config["output"], margin, width, C_WHITE)
        print(f"\n{margin}{C_WHITE}{len(results)} SVG{C_RESET}")

        if failures:
            print(f"{margin}{C_RED}{len(failures)} {t['failed'].lower()}{C_RESET}")
            for source, error in failures[:5]:
                text = f"{os.path.basename(source)}: {error}"
                print_wrapped_text(text, margin, width, C_GRAY)

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
        draw_menu_item(margin, "0", "Back")

        print()
        draw_sys_item(margin, width, t["output_path"], config["output"])
        draw_sys_item(margin, width, t["colors"], str(config["colors"]))
        draw_sys_item(margin, width, t["detail"], str(config["detail"]))
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
            config["background"] = modes[(current + 1) % len(modes)]

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
        draw_menu_item(margin, "0", "Exit")
        print()

        print(f"{margin}{C_BLUE}{t['system']}{C_RESET}")
        draw_sys_item(margin, width, t["output_path"], config["output"])
        draw_sys_item(margin, width, t["colors"], str(config["colors"]))
        draw_sys_item(margin, width, t["detail"], str(config["detail"]))
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
    parser.add_argument("--no-denoise", action="store_true")
    return parser.parse_args()


def apply_arguments(config, args):
    if args.output:
        config["output"] = clean_path(args.output)
    if args.colors is not None:
        config["colors"] = max(2, min(64, args.colors))
    if args.detail is not None:
        config["detail"] = max(1, min(100, args.detail))
    if args.background:
        config["background"] = args.background
    if args.max_size is not None:
        config["max_size"] = max(256, args.max_size)
    if args.min_area is not None:
        config["min_area"] = max(0.1, args.min_area)
    if args.no_denoise:
        config["denoise"] = 0
    return config


def main():
    enable_ansi()
    args = parse_arguments()
    config = apply_arguments(load_config(), args)

    if args.inputs:
        os.makedirs(config["output"], exist_ok=True)
        results = run_conversion(config, args.inputs)
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
