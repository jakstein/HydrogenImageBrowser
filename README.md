# Hydrogen

Hydrogen is a simple PySide6-based image browser.

## Features

- Display an image
- Zoom in and out using a vertical slider or scroll wheel
- Rotate the image using a dial (or scroll wheel over the dial)
- Move the image by dragging it around
- Reset move, zoom, rotation by just right-clicking on the element responsible for each
- Navigate between images within a folder, sorted with natsort
- More to come

## Shortcuts
- R: flip image horizontally
- Shift + R: flip image vertically
- Ctrl + R: reset flip
- F: fit image to window

- Right click on image: reset image position
- Right click on rotation dial: reset rotation
- Right click on zoom slider: reset zoom
- Right click on next/prev button: go to first/last image

## Requirements

- Python 3.x
- PySide6
- Pillow
- pillow-avif
- pillow-jxl
- natsort

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/jakstein/HydrogenImageBrowser
    cd HydrogenImageBrowser
    ```

2. Install the required packages:
    ```sh
    pip install PySide6 Pillow pillow-avif pillow-jxl natsort
    ```

## Usage

Run the application:
```sh
python Hydrogen.pyw
```
You can also open an image directly by passing the image path as a command-line argument:
```sh
python Hydrogen.pyw path/to/image.png
```