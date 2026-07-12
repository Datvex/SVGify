# SVGify

🌐 **English** | [Русский](README_ru.md)

SVGify converts raster logos and photographs into colored SVG graphics directly from the terminal. Its tracing engine is powered by VTracer, so the project does not depend on OpenCV.

The program accepts individual images, directories, PDF files, existing SVG files, and ZIP archives. Background removal, color complexity, contour detail, and output filtering can be configured through either the interactive interface or command-line arguments.

> Vectorization cannot reconstruct details that are absent from the source. Sharp images with even lighting, clear edges, and a simple background produce the best results.

## Installation

SVGify requires Python 3.10 or newer. The commands below clone the repository, create an isolated environment, install the dependencies from `requirements.txt`, and start `SVGify.py`.

### Windows

Open PowerShell:

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

Restart PowerShell after installing Git or Python if their commands are not immediately available. If `py` is unavailable, replace it with `python`.

### macOS

Install the required tools with Homebrew:

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

Homebrew itself can be installed with:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Ubuntu and Debian

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

### Arch Linux and Manjaro

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

Use the current Termux release from F-Droid or GitHub. The Google Play version is outdated.

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

Some Python packages do not provide official Android wheels. On unsupported Termux architectures, pip may need to compile VTracer, Pillow HEIF, RawPy, or PyMuPDF locally.

## Usage

Start the interactive interface:

```bash
python SVGify.py
```

Convert one image without opening the menu:

```bash
python SVGify.py logo.png
```

Multiple files, directories, and ZIP archives can be processed together:

```bash
python SVGify.py logo.png ./brand-assets icons.zip
```

Choose another output directory:

```bash
python SVGify.py logo.png --output ./output
```

Configure color complexity, contour detail, and background removal:

```bash
python SVGify.py logo.png --colors 16 --detail 85 --background auto
```

A photograph with a complex background may require forced background removal:

```bash
python SVGify.py photo.jpg --background on --background-tolerance 38
```

## Command-line reference

| Argument | Description |
| --- | --- |
| `inputs` | Images, PDF files, SVG files, directories, or ZIP archives |
| `-o`, `--output PATH` | Output directory |
| `-c`, `--colors NUMBER` | Color complexity from 2 to 64 |
| `-d`, `--detail NUMBER` | Contour detail from 1 to 100 |
| `-b`, `--background MODE` | Background mode: `auto`, `on`, or `off` |
| `--max-size NUMBER` | Maximum image dimension used during processing |
| `--min-area NUMBER` | VTracer speckle-filtering level |
| `--background-tolerance NUMBER` | Background color tolerance from 1 to 255 |

`auto` preserves existing transparency and removes only a sufficiently uniform edge-connected background. `on` always attempts removal, while `off` passes the original background to VTracer.

Background removal is designed for solid or nearly solid backgrounds. It deliberately avoids a large machine-learning dependency and does not attempt semantic object segmentation.

## Supported input

| Category | Formats |
| --- | --- |
| Standard images | PNG, JPG, JPEG, JFIF, WebP, BMP, GIF, TIFF, ICO, TGA |
| Portable maps | PPM, PGM, PBM, PNM |
| Modern images | HEIC, HEIF, AVIF |
| Camera RAW | RAW, DNG, CR2, CR3, NEF, ARW, ORF, RW2, RAF, PEF, SRW |
| Documents and vectors | PDF, SVG |
| Archives | ZIP |

SVG files are copied without rasterizing them again. SVGify processes the first page of a PDF and the first frame of an animated image. Directories are scanned recursively.

Support for a particular image format also depends on the codecs available to Pillow on the current platform.

## Choosing settings

A flat logo usually works well with a low color level and medium-to-high detail:

```bash
python SVGify.py logo.png --colors 8 --detail 75 --background auto
```

Detailed artwork can use a higher color level:

```bash
python SVGify.py artwork.png --colors 32 --detail 90 --background off
```

For a cleaner and smaller SVG, lower the detail and increase the speckle filter:

```bash
python SVGify.py logo.png --colors 8 --detail 60 --min-area 12
```

`--colors` controls VTracer's color precision rather than enforcing an exact palette size. The final SVG may therefore contain a different number of colors.

## Output and configuration

Results are written to `Downloads/SVGify` by default. Existing files are never overwritten; a suffix such as `_2` or `_3` is added when necessary.

Interactive settings are stored in:

```text
~/.svgify_memory.json
```

Remove this file to restore the defaults.

## Troubleshooting

Reinstall all project dependencies inside the active environment if an import is missing:

```bash
python -m pip install --upgrade -r requirements.txt
```

If a RAW, HEIC, or PDF file cannot be opened, verify that `rawpy`, `pillow-heif`, and `PyMuPDF` were installed successfully.

A background that contains shadows, gradients, or many edge colors may not be removed in `auto` mode. Use `--background on`, adjust `--background-tolerance`, or provide an image with an already transparent background.

If the output contains too many tiny paths, increase `--min-area`. If curves are too simplified, increase `--detail`. Lowering `--max-size` reduces memory use and processing time.

## License

SVGify is free software distributed under the [GNU General Public License v3.0](LICENSE).

You may use, study, modify, and redistribute the project under the terms of that license.
