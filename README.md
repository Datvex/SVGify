# SVGify

🌐 **Language:** [English](Readme.md) | [Русский](Readme_ru.md)

SVGify is a command-line tool for converting logos from raster images and other supported sources into colored SVG vector graphics.

It supports interactive and command-line modes, batch processing, folders, ZIP archives, background removal, color quantization, contour smoothing, and a multilingual interface.

## Supported formats

- Images: PNG, JPG, JPEG, JFIF, WebP, BMP, GIF, TIFF, ICO, PPM, PGM, PBM, PNM, TGA
- Modern image formats: HEIC, HEIF, AVIF
- RAW formats: RAW, DNG, CR2, CR3, NEF, ARW, ORF, RW2, RAF, PEF, SRW
- Documents and vectors: PDF, SVG
- Archives: ZIP
- Folders containing supported files

Only the first page of a PDF and the first frame of an animated image are processed.

## Features

- Colored SVG output
- Automatic or forced background removal
- Adjustable number of colors
- Adjustable contour detail
- Image denoising
- Batch conversion
- Recursive folder processing
- ZIP archive processing
- Preservation of existing SVG files
- English, Russian, and Chinese interface
- Windows, Linux, and macOS support
- Interactive terminal interface
- Command-line interface

## Important limitation

Automatic image tracing cannot restore hidden details or guarantee a mathematically identical copy of every logo.

The result depends on:

- Image resolution
- Lighting
- Compression artifacts
- Camera angle and perspective
- Shadows
- Reflections
- Background complexity
- Original logo complexity

For the best result, use a high-resolution image with sharp edges, even lighting, minimal compression, a simple background, and no perspective distortion.

## Requirements

- Python 3.10 or newer
- pip
- Cairo system libraries may be required for CairoSVG

## Installation

Download or clone the project, open its directory, and create a virtual environment.

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Linux and macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Ubuntu or Debian

CairoSVG may require additional system packages:

```bash
sudo apt update
sudo apt install libcairo2 libffi-dev
```

### macOS with Homebrew

```bash
brew install cairo libffi
```

## Interactive mode

Run SVGify without arguments:

```bash
python svgify.py
```

The interactive menu lets you configure:

- Output directory
- Number of colors
- Contour detail
- Background removal mode
- Interface language

Paths can be entered manually or dragged into a compatible terminal window.

## Command-line mode

Convert one image:

```bash
python svgify.py logo.png
```

Convert multiple files:

```bash
python svgify.py logo.png brand.jpg icon.webp
```

Process a folder recursively:

```bash
python svgify.py ./logos
```

Process a ZIP archive:

```bash
python svgify.py logos.zip
```

Choose an output directory:

```bash
python svgify.py logo.png --output ./svg
```

Configure vectorization:

```bash
python svgify.py logo.png --colors 16 --detail 85 --background auto
```

Disable denoising:

```bash
python svgify.py logo.png --no-denoise
```

Process large images at a higher internal resolution:

```bash
python svgify.py logo.png --max-size 4000
```

Remove smaller contour fragments:

```bash
python svgify.py logo.png --min-area 12
```

## Command-line options

```text
inputs                  Files, folders, or ZIP archives
-o, --output PATH       Output directory
-c, --colors NUMBER     Number of colors from 2 to 64
-d, --detail NUMBER     Contour detail from 1 to 100
-b, --background MODE   Background mode: auto, on, or off
--max-size NUMBER       Maximum internal image dimension
--min-area NUMBER       Minimum contour area
--no-denoise            Disable image denoising
```

## Background modes

### `auto`

Removes the background only when needed. Transparent images normally keep their existing alpha channel.

```bash
python svgify.py logo.png --background auto
```

### `on`

Always attempts to remove the background.

```bash
python svgify.py photo.jpg --background on
```

### `off`

Preserves the original background.

```bash
python svgify.py image.png --background off
```

## Recommended settings

### Simple flat logo

```bash
python svgify.py logo.png --colors 6 --detail 80 --background auto
```

### Detailed multicolor logo

```bash
python svgify.py logo.png --colors 24 --detail 90 --background auto
```

### Logo on a complex photograph

```bash
python svgify.py photo.jpg --colors 16 --detail 85 --background on
```

### Cleaner and smaller SVG

```bash
python svgify.py logo.png --colors 8 --detail 60 --min-area 15
```

## Output

SVG files are saved in the configured output directory.

Default directories:

- Windows: `Downloads\SVGify`
- Linux and macOS: `~/Downloads/SVGify`
- Android-compatible environments: `/storage/emulated/0/Download/SVGify`

Existing files are not overwritten. SVGify adds a numeric suffix such as `_2` or `_3`.

## Configuration

Interactive settings are stored in:

```text
~/.svgify_memory.json
```

Delete this file to restore the default settings.

## Troubleshooting

### RAW files do not open

Make sure `rawpy` is installed:

```bash
pip install --upgrade rawpy
```

### HEIC or HEIF files do not open

Install or update Pillow HEIF:

```bash
pip install --upgrade pillow-heif
```

### PDF files do not open

Install or update PyMuPDF:

```bash
pip install --upgrade pymupdf
```

### SVG input cannot be rendered

Install CairoSVG and the required Cairo system libraries:

```bash
pip install --upgrade cairosvg
```

### Background removal is unavailable

Install or update the background-removal packages:

```bash
pip install --upgrade rembg onnxruntime
```

### The output contains too many small shapes

Reduce contour detail or increase the minimum contour area:

```bash
python svgify.py logo.png --detail 60 --min-area 15
```

### The output colors look too simplified

Increase the number of colors:

```bash
python svgify.py logo.png --colors 24
```

### Processing is slow

Reduce the internal image size:

```bash
python svgify.py logo.png --max-size 1600
```

## License

MIT
