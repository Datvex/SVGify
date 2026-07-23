# SVGify

🌐 **English** | [Русский](README_ru.md)

SVGify converts raster images into clean, colored SVG files directly from the terminal. It is made primarily for logos, icons, emblems, lettering, and other artwork with clear shapes and a limited palette.

The project uses its own tracing engine written in Python. It does not use VTracer, OpenCV, NumPy, external command-line programs, or online services. Pillow is the only third-party Python dependency.

The program can process a single image, several files, a directory, or a ZIP archive. It includes an interactive terminal interface and can also be used entirely through command-line arguments.

> Vectorization cannot restore detail that is missing from the source image. Clean images with clear edges, good contrast, and a simple background give the best results.

## How the tracing engine works

SVGify first examines the image and builds a compact palette. Similar shades caused by JPEG compression and antialiasing are grouped together, which helps keep logo edges clean instead of creating hundreds of tiny color layers.

The engine then detects the background, finds the boundaries of each visible color region, follows closed contours, keeps inner holes, removes small artifacts, and simplifies the resulting geometry. Sharp corners are preserved while unnecessary pixel steps are removed.

The final SVG uses standard paths, compound contours, `fill-rule="evenodd"`, the original image dimensions, and a matching `viewBox`. The output does not contain an embedded raster image.

## Requirements

SVGify requires Python 3.10 or newer.

The project has one Python dependency:

```text
Pillow>=10.0.0,<13.0.0
```

This version range is valid for `requirements.txt`. It allows Pillow 10, 11, and 12 while preventing an automatic upgrade to a future major release that has not yet been tested.

## Installation

### Windows

Open PowerShell and install Git and Python if they are not already available:

```powershell
winget install --id Git.Git -e
winget install --id Python.Python.3.12 -e
```

Restart PowerShell after installation, then run:

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

If the `py` command is unavailable, use `python` instead.

### macOS

Install Python and Git with Homebrew:

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

Homebrew can be installed with:

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

Use the current Termux release from F-Droid or GitHub. The Google Play version is outdated.

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

Pillow may be compiled locally when a prebuilt wheel is not available for the current Android architecture.

## Usage

Start the interactive interface:

```bash
python SVGify.py
```

Convert one image without opening the menu:

```bash
python SVGify.py logo.png
```

Process several files, directories, and ZIP archives together:

```bash
python SVGify.py logo.png ./brand-assets icons.zip
```

Choose another output directory:

```bash
python SVGify.py logo.png --output ./output
```

Configure the palette, contour detail, and background mode:

```bash
python SVGify.py logo.png --colors 8 --detail 75 --background auto
```

Preserve the original background:

```bash
python SVGify.py logo.jpg --background off
```

## Command-line reference

| Argument | Description |
| --- | --- |
| `inputs` | Images, directories, or ZIP archives |
| `-o`, `--output PATH` | Output directory |
| `-c`, `--colors NUMBER` | Palette complexity from 2 to 64 |
| `-d`, `--detail NUMBER` | Contour detail from 1 to 100 |
| `-b`, `--background MODE` | Background mode: `auto`, `on`, or `off` |
| `--max-size NUMBER` | Maximum image dimension used during tracing |
| `--min-area NUMBER` | Minimum contour area kept in the SVG |
| `--background-tolerance NUMBER` | Background color tolerance from 1 to 255 |

In `auto` mode, SVGify removes a sufficiently uniform background detected along the image edges. Existing transparency is preserved. The `on` mode requests background removal, while `off` keeps the original background as part of the SVG.

Background detection is intended for solid or nearly solid backgrounds. It does not perform semantic object segmentation and does not use a machine-learning model.

## Supported input

| Category | Formats |
| --- | --- |
| Standard images | PNG, JPG, JPEG, JFIF, WebP, BMP, DIB, GIF, TIFF, ICO, TGA |
| Portable maps | PPM, PGM, PBM, PNM |
| Archives | ZIP |

Directories are scanned recursively. The first frame of an animated image is used. ZIP archives are extracted to a temporary directory and removed after processing.

Support for an image format depends on the codecs enabled in the installed Pillow build.

## Choosing settings

A flat logo normally works well with a small palette and the default detail level:

```bash
python SVGify.py logo.png --colors 8 --detail 75 --background auto
```

Artwork with more colors can use a larger palette:

```bash
python SVGify.py artwork.png --colors 24 --detail 85 --background off
```

A lower detail value produces fewer path segments and a smaller SVG. A higher value follows small changes in the source more closely:

```bash
python SVGify.py logo.png --detail 60
python SVGify.py logo.png --detail 90
```

Increase `--min-area` when compression noise or isolated pixels create unwanted fragments:

```bash
python SVGify.py logo.jpg --min-area 12
```

The `--colors` value is a maximum palette complexity, not a promise that the SVG will contain exactly that number of colors. SVGify can automatically use fewer colors when the image is recognized as simple artwork.

## Output and configuration

Results are saved to `Downloads/SVGify` by default. Existing files are not overwritten. SVGify adds a suffix such as `_2` or `_3` when the output name already exists.

Interactive settings are stored in:

```text
~/.svgify_memory.json
```

Delete this file to restore the default settings.

## Troubleshooting

If Pillow cannot be imported, activate the project environment and reinstall the dependency:

```bash
python -m pip install --upgrade -r requirements.txt
```

If an image format cannot be opened, check whether the current Pillow build includes the required codec. Converting the source to PNG is usually the simplest workaround.

If the SVG contains small unwanted fragments, increase `--min-area`. If the contours look too simplified, increase `--detail`. Lowering `--max-size` reduces memory use and processing time for very large images.

If `auto` mode keeps the background, try `--background on`. For gradients, shadows, or detailed scenery, prepare a transparent PNG before vectorization.

## License

SVGify is free software distributed under the [GNU General Public License v3.0](LICENSE).

You may use, study, modify, and redistribute the project under the terms of that license.