# -*- coding: utf-8 -*-
import argparse
import os
import subprocess
import sys

# -*- coding: utf-8 -*-
UPPER_ORDER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
LOWER_ORDER = "abcdefghijklmnopqrstuvwxyz"
UPPER_REF = """▄▄▄▄     ▄▄▄▄▄▄▄      ▄▄▄▄▄▄▄   ▄▄▄▄▄▄      ▄▄▄▄▄▄▄    ▄▄▄▄▄▄▄    ▄▄▄▄▄▄▄    ▄▄▄   ▄▄▄   ▄▄▄▄▄        ▄▄▄   ▄▄▄   ▄▄▄   ▄▄▄        ▄▄▄      ▄▄▄   ▄▄▄    ▄▄▄     ▄▄▄▄▄     ▄▄▄▄▄▄▄       ▄▄▄▄▄     ▄▄▄▄▄▄▄      ▄▄▄▄▄▄▄   ▄▄▄▄▄▄▄▄▄   ▄▄▄  ▄▄▄   ▄▄▄▄  ▄▄▄▄   ▄▄▄▄  ▄▄▄  ▄▄▄▄   ▄▄▄   ▄▄▄   ▄▄▄   ▄▄▄   ▄▄▄▄▄▄▄▄▄
▄██▀▀██▄   ███▀▀███▄   ███▀▀▀▀▀   ███▀▀██▄   ███▀▀▀▀▀   ███▀▀▀▀▀   ███▀▀▀▀▀    ███   ███    ███         ███   ███ ▄███▀   ███        ████▄  ▄████   ████▄  ███   ▄███████▄   ███▀▀███▄   ▄███████▄   ███▀▀███▄   █████▀▀▀   ▀▀▀███▀▀▀   ███  ███   ▀███  ███▀   ▀███  ███  ███▀   ████▄████   ███   ███   ▀▀▀▀▀████
███  ███   ███▄▄███▀   ███        ███  ███   ███▄▄      ███▄▄      ███         █████████    ███         ███   ███████     ███        ███▀████▀███   ███▀██▄███   ███   ███   ███▄▄███▀   ███   ███   ███▄▄███▀    ▀████▄       ███      ███  ███    ███  ███     ███  ███  ███     ▀█████▀    ▀███▄███▀      ▄███▀
███▀▀███   ███  ███▄   ███        ███  ███   ███        ███▀▀      ███  ███▀   ███▀▀▀███    ███    ▄▄▄  ███   ███▀███▄    ███        ███  ▀▀  ███   ███  ▀████   ███▄▄▄███   ███▀▀▀▀     ███▄█▄███   ███▀▀██▄       ▀████      ███      ███▄▄███    ███▄▄███     ███▄▄███▄▄███    ▄███████▄     ▀███▀      ▄███▀
███  ███   ████████▀   ▀███████   ██████▀    ▀███████   ███        ▀██████▀    ███   ███   ▄███▄    ▀████▀    ███  ▀███   ████████   ███      ███   ███    ███    ▀█████▀    ███          ▀█████▀    ███  ▀███   ███████▀      ███      ▀██████▀     ▀████▀       ▀████▀████▀     ███▀ ▀███      ███      █████████"""
LOWER_REF = """▄▄                 ▄▄             ▄▄           ▄▄                            ▄▄
██                 ██            ██            ██      ▀▀      ▀▀   ▄▄       ██                                                               ██
▀▀█▄   ████▄   ▄████   ▄████   ▄█▀█▄   ▀██▀   ▄████   ████▄   ██      ██   ██ ▄█▀   ██   ███▄███▄   ████▄   ▄███▄   ████▄   ▄████   ████▄   ▄█▀▀▀   ▀██▀▀   ██ ██   ██ ██   ██   ██   ██ ██   ██ ██   ▀▀▀██
▄█▀██   ██ ██   ██      ██ ██   ██▄█▀    ██    ██ ██   ██ ██   ██     ▀██   ████     ██   ██ ██ ██   ██ ██   ██ ██   ██ ██   ██ ██   ██ ▀▀   ▀███▄    ██     ██ ██   ██▄██   ██ █ ██    ███    ██▄██     ▄█▀
▀█▄██   ████▀   ▀████   ▀████   ▀█▄▄▄    ██    ▀████   ██ ██   ██▄     ██   ██ ▀█▄   ██   ██ ██ ██   ██ ██   ▀███▀   ████▀   ▀████   ██      ▄▄▄█▀    ██     ▀██▀█    ▀█▀     ██▀██    ██ ██    ▀██▀   ▄██▄▄
██                   ██                                            ██         ██                                                               ██
▀▀▀                  ▀▀▀                                             ▀▀         ▀▀                                                             ▀▀▀"""

C_YELLOW = "\033[38;2;248;246;117m"
C_SHADOW_FG = "\033[38;2;90;90;40m"
C_SHADOW_BG = "\033[48;2;90;90;40m"
C_RESET = "\033[0m"
FULL, UP, LOW = "█", "▀", "▄"
GLYPH_ROWS = 7
LETTER_SPACING = 1
SPACE_WIDTH = 6


def _spans(ref, core_rows):
    lines = ref.splitlines()
    width = max(map(len, lines))
    grid = [line.ljust(width) for line in lines]
    def blank(c):
        return all(grid[r][c] == " " for r in core_rows)
    spans = []
    c = 0
    while c < width:
        while c < width and blank(c):
            c += 1
        if c >= width:
            break
        start = c
        while c < width and not blank(c):
            c += 1
        spans.append((start, c))
    return grid, spans


def _put(row, text, align):
    width = len(row)
    text = text[:width]
    if align == "left":
        start = 0
    elif align == "right":
        start = max(0, width - len(text))
    else:
        start = max(0, (width - len(text)) // 2)
    chars = list(row)
    for i, ch in enumerate(text):
        if start + i < width and ch != " ":
            chars[start + i] = ch
    return "".join(chars)


def _build_font():
    font = {}
    grid, spans = _spans(UPPER_REF, range(5))
    if len(spans) != 26:
        raise RuntimeError("Не удалось разобрать заглавный алфавит")
    for ch, (start, end) in zip(UPPER_ORDER, spans):
        font[ch] = [row[start:end] for row in grid[:5]] + [" " * (end-start)] * 2

    def place(row, width, left):
        content = row.strip()
        if not content:
            return " " * width
        left = max(0, min(left, width - len(content)))
        return " " * left + content + " " * (width - left - len(content))

    for ch in "AIMOPQTUVWXY":
        width = len(font[ch][0])
        font[ch][:5] = [place(row, width, (width - len(row.strip())) // 2) for row in font[ch][:5]]

    for ch in "BCDEFGHKLNPR":
        width = len(font[ch][0])
        font[ch][:5] = [place(row, width, 0) for row in font[ch][:5]]

    width = len(font["J"][0])
    font["J"][:5] = [place(row, width, width - len(row.strip())) for row in font["J"][:5]]

    width = len(font["S"][0])
    font["S"][:5] = [place(row, width, left) for row, left in zip(font["S"][:5], [1, 0, 1, 4, 0])]

    width = len(font["Z"][0])
    font["Z"][:5] = [place(row, width, left) for row, left in zip(font["Z"][:5], [0, 2, 4, 2, 0])]

    grid, spans = _spans(LOWER_REF, [2, 3, 4])
    if len(spans) != 26:
        raise RuntimeError("Не удалось разобрать строчный алфавит")
    for ch, (start, end) in zip(LOWER_ORDER, spans):
        width = end - start
        font[ch] = [" " * width, " " * width] + [grid[r][start:end] for r in [2, 3, 4]] + [" " * width, " " * width]

    top = {
        "b": (("▄▄", "left"), ("██", "left")),
        "d": (("▄▄", "right"), ("██", "right")),
        "f": (("▄▄", "center"), ("██", "center")),
        "h": (("▄▄", "left"), ("██", "left")),
        "i": (("", "center"), ("▀▀", "center")),
        "j": (("", "center"), ("▀▀", "center")),
        "k": (("▄▄", "left"), ("██", "left")),
        "l": (("▄▄", "left"), ("██", "left")),
        "t": (("", "center"), ("██", "center")),
    }
    for ch, rows in top.items():
        font[ch][0] = _put(font[ch][0], *rows[0])
        font[ch][1] = _put(font[ch][1], *rows[1])

    tails = {
        "g": (("██", "right"), ("▀▀▀", "right")),
        "j": (("██", "right"), ("▀▀▀", "right")),
        "p": (("██", "left"), ("▀▀", "left")),
        "q": (("██", "right"), ("▀▀", "right")),
        "y": (("██", "center"), ("▀▀▀", "center")),
    }
    for ch, rows in tails.items():
        font[ch][5] = _put(font[ch][5], *rows[0])
        font[ch][6] = _put(font[ch][6], *rows[1])

    for ch in UPPER_ORDER + LOWER_ORDER:
        rows = font[ch]
        width = max(map(len, rows))
        rows = [row.ljust(width) for row in rows]
        used = [x for x in range(width) if any(row[x] != " " for row in rows)]
        if used:
            left, right = min(used), max(used) + 1
            font[ch] = [row[left:right] for row in rows]

    font[" "] = [" " * SPACE_WIDTH for _ in range(GLYPH_ROWS)]
    return font


GLYPHS = _build_font()


def assemble(text, spacing=LETTER_SPACING):
    rows = [""] * GLYPH_ROWS
    for ch in text:
        glyph = GLYPHS.get(ch, GLYPHS[" "])
        width = max(map(len, glyph))
        for i in range(GLYPH_ROWS):
            rows[i] += glyph[i].ljust(width) + " " * max(0, spacing)
    return [row.rstrip() for row in rows]


def _rows_to_pixels(rows):
    width = max((len(row) for row in rows), default=0)
    pixels = []
    for row in rows:
        row = row.ljust(width)
        top, bottom = [], []
        for ch in row:
            if ch == FULL:
                top.append(1); bottom.append(1)
            elif ch == UP:
                top.append(1); bottom.append(0)
            elif ch == LOW:
                top.append(0); bottom.append(1)
            else:
                top.append(0); bottom.append(0)
        pixels.extend((top, bottom))
    return pixels, width


def _cell(mt, mb, st, sb):
    top = "M" if mt else ("S" if st else "E")
    bottom = "M" if mb else ("S" if sb else "E")
    table = {
        ("E", "E"): " ",
        ("M", "M"): C_YELLOW + FULL + C_RESET,
        ("S", "S"): C_SHADOW_FG + FULL + C_RESET,
        ("M", "E"): C_YELLOW + UP + C_RESET,
        ("E", "M"): C_YELLOW + LOW + C_RESET,
        ("S", "E"): C_SHADOW_FG + UP + C_RESET,
        ("E", "S"): C_SHADOW_FG + LOW + C_RESET,
        ("M", "S"): C_SHADOW_BG + C_YELLOW + UP + C_RESET,
        ("S", "M"): C_SHADOW_BG + C_YELLOW + LOW + C_RESET,
    }
    return table[(top, bottom)]


def render_colored(rows):
    pixels, width = _rows_to_pixels(rows)
    height = len(pixels)
    output = []
    for y in range(0, height + 1, 2):
        line = []
        for x in range(width):
            main_top = y < height and pixels[y][x]
            main_bottom = y + 1 < height and pixels[y + 1][x]
            shadow_top = y > 0 and pixels[y - 1][x]
            shadow_bottom = y < height and pixels[y][x]
            line.append(_cell(main_top, main_bottom, shadow_top, shadow_bottom))
        output.append("".join(line) + C_RESET)
    return "\n".join(output)


def render_plain(rows):
    result = list(rows)
    while result and not result[0].strip():
        result.pop(0)
    while result and not result[-1].strip():
        result.pop()
    return "\n".join(row.rstrip() for row in result)


def copy_windows(text):
    import ctypes
    import time
    from ctypes import wintypes
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    user32.OpenClipboard.argtypes = [wintypes.HWND]
    user32.OpenClipboard.restype = wintypes.BOOL
    user32.EmptyClipboard.restype = wintypes.BOOL
    user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
    user32.SetClipboardData.restype = wintypes.HANDLE
    user32.CloseClipboard.restype = wintypes.BOOL
    kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
    kernel32.GlobalAlloc.restype = wintypes.HGLOBAL
    kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalUnlock.restype = wintypes.BOOL
    CF_UNICODETEXT = 13
    GMEM_MOVEABLE = 0x0002
    opened = False
    for _ in range(20):
        if user32.OpenClipboard(None):
            opened = True
            break
        time.sleep(0.025)
    if not opened:
        return False
    handle = None
    try:
        if not user32.EmptyClipboard():
            return False
        data = text + "\0"
        size = len(data.encode("utf-16-le"))
        handle = kernel32.GlobalAlloc(GMEM_MOVEABLE, size)
        if not handle:
            return False
        pointer = kernel32.GlobalLock(handle)
        if not pointer:
            return False
        ctypes.memmove(pointer, data.encode("utf-16-le"), size)
        kernel32.GlobalUnlock(handle)
        if not user32.SetClipboardData(CF_UNICODETEXT, handle):
            return False
        handle = None
        return True
    finally:
        user32.CloseClipboard()
        if handle:
            kernel32.GlobalFree(handle)


def copy_to_clipboard(text):
    if sys.platform == "win32":
        try:
            return copy_windows(text)
        except Exception:
            return False
    try:
        if sys.platform == "darwin":
            subprocess.run(["pbcopy"], input=text, text=True, check=True)
            return True
        for command in (["wl-copy"], ["xclip", "-selection", "clipboard"], ["xsel", "--clipboard", "--input"]):
            try:
                subprocess.run(command, input=text, text=True, check=True)
                return True
            except FileNotFoundError:
                pass
    except Exception:
        pass
    return False


def make_banner(text, plain=False, spacing=LETTER_SPACING):
    rows = assemble(text, spacing)
    return render_plain(rows) if plain else render_colored(rows)


def main():
    if sys.platform == "win32":
        os.system("")
    parser = argparse.ArgumentParser()
    parser.add_argument("text", nargs="?")
    parser.add_argument("--plain", action="store_true")
    parser.add_argument("--spacing", type=int, default=LETTER_SPACING)
    parser.add_argument("--no-copy", action="store_true")
    args = parser.parse_args()

    def output(text):
        rows = assemble(text, args.spacing)
        print(render_plain(rows) if args.plain else render_colored(rows))
        if not args.no_copy:
            copied = copy_to_clipboard(render_plain(rows))
            print("(надпись скопирована в буфер обмена)" if copied else "(ошибка копирования в буфер обмена)")

    if args.text is not None:
        output(args.text)
        return
    while True:
        try:
            text = input("Введите текст: ")
        except (EOFError, KeyboardInterrupt):
            print(); break
        if not text or text.strip().lower() in ("q", "quit", "exit"):
            break
        output(text)
        try:
            again = input("Ещё раз? (Enter — да, 'q' — выход): ")
        except (EOFError, KeyboardInterrupt):
            print(); break
        if again.strip().lower() in ("q", "quit", "exit"):
            break


if __name__ == "__main__":
    main()
