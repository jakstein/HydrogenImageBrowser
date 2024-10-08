# Hydrogen

Hydrogen is a simple PySide6 application that displays an image and allows you to zoom and rotate it using a slider and a dial.

## Features

- Display an image
- Zoom in and out using a vertical slider or scroll wheel
- Rotate the image using a dial (or scroll wheel over the dial)
- Move the image by dragging it around
- Reset move, zoom, rotation by just right-clicking on the element responsible for each
- More to come

## Requirements

- Python 3.x
- PySide6
- Pillow
- pillow-avif
- pillow-jxl

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/jakstein/HydrogenImageBrowser
    cd HydrogenImageBrowser
    ```

2. Install the required packages:
    ```sh
    pip install PySide6 Pillow pillow-avif pillow-jxl
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