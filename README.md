# SVGify

🌐 **English** | [Русский](README_ru.md)

Convert logos and raster images into clean, colored SVG graphics directly from the terminal.

SVGify processes individual images, entire directories, and ZIP archives. It can remove backgrounds, reduce the color palette, smooth contours, and export each result as an editable SVG file.

> Automatic tracing cannot reconstruct details that are missing from the source image. Sharp, high-resolution images with even lighting and a simple background produce the best results.

## Quick start

```bash
git clone https://github.com/Datvex/SVGify.git
cd SVGify
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python SVGify.py
```

Windows users should follow the PowerShell instructions below.

## Platform installation

SVGify requires Python 3.10 or newer. Every installation below clones the repository, creates an isolated Python environment, installs all Python dependencies from `requirements.txt`, and starts the application.

### Windows

Open PowerShell and run:

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

If the `py` command is unavailable, replace `py` with `python`. Git and Python can be installed through `winget`:

```powershell
winget install --id Git.Git -e
winget install --id Python.Python.3.12 -e
```

Restart PowerShell after installation, then run the main installation commands.

### macOS

Install the required system packages with Homebrew:

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

Install Homebrew first if it is not already available:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Ubuntu and Debian

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

### Arch Linux and Manjaro

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

Install Termux from F-Droid or GitHub rather than the outdated Google Play release.

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

Some machine-learning packages do not publish official Android wheels. If `onnxruntime` or `rembg` cannot be installed in Termux, background removal through those packages will be unavailable even though SVGify's built-in processing can still be used.

## Usage

Start the interactive interface:

```bash
python SVGify.py
```

Convert a single image without opening the menu:

```bash
python SVGify.py logo.png
```

Files, directories, and ZIP archives can be passed together:

```bash
python SVGify.py logo.png ./brand-assets icons.zip
```

Choose another output directory:

```bash
python SVGify.py logo.png --output ./output
```

Fine-tune the result:

```bash
python SVGify.py logo.png --colors 16 --detail 85 --background auto
```

## Command-line reference

| Argument | Description |
| --- | --- |
| `inputs` | Images, directories, or ZIP archives |
| `-o`, `--output PATH` | Output directory |
| `-c`, `--colors NUMBER` | Number of colors, from 2 to 64 |
| `-d`, `--detail NUMBER` | Contour detail, from 1 to 100 |
| `-b`, `--background MODE` | Background mode: `auto`, `on`, or `off` |
| `--max-size NUMBER` | Maximum image dimension used during processing |
| `--min-area NUMBER` | Minimum contour area retained in the SVG |
| `--no-denoise` | Disable image denoising |

The `auto` background mode removes a background only when necessary. Use `on` for a logo photographed against a complex surface, or `off` when the background must remain part of the output.

## Formats

| Category | Formats |
| --- | --- |
| Standard images | PNG, JPG, JPEG, JFIF, WebP, BMP, GIF, TIFF, ICO, TGA |
| Portable maps | PPM, PGM, PBM, PNM |
| Modern images | HEIC, HEIF, AVIF |
| Camera RAW | RAW, DNG, CR2, CR3, NEF, ARW, ORF, RW2, RAF, PEF, SRW |
| Documents and vectors | PDF, SVG |
| Archives | ZIP |

SVGify processes the first page of a PDF and the first frame of an animated image. Directories are scanned recursively.

## Choosing settings

A flat logo usually needs only 4 to 8 colors. Detailed artwork can benefit from 16 to 32 colors, but larger palettes produce heavier SVG files.

```bash
python SVGify.py logo.png --colors 8 --detail 75 --background auto
```

For a logo photographed on a complex background:

```bash
python SVGify.py photo.jpg --colors 16 --detail 85 --background on
```

For a smaller and cleaner SVG, lower the detail and discard tiny contours:

```bash
python SVGify.py logo.png --colors 8 --detail 60 --min-area 15
```

## Output and configuration

Results are written to `Downloads/SVGify` by default. Existing files are never overwritten; SVGify adds a suffix such as `_2` or `_3` when necessary.

Interactive settings are stored in:

```text
~/.svgify_memory.json
```

Remove this file to restore the defaults.

## Troubleshooting

If RAW, HEIC, PDF, or SVG input cannot be opened, first reinstall the project dependencies inside the active virtual environment:

```bash
python -m pip install --upgrade -r requirements.txt
```

CairoSVG may also require the Cairo system library. The platform instructions above install it where necessary.

If the generated SVG contains too many fragments, increase `--min-area` or reduce `--detail`. If colors look oversimplified, increase `--colors`. Lowering `--max-size` reduces memory use and processing time.

## License

SVGify is free software distributed under the [GNU General Public License v3.0](LICENSE).

You may use, study, modify, and redistribute the project under the terms of that license.
