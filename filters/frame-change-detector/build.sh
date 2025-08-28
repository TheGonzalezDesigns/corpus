#!/bin/bash

echo "Building frame-change-detector Rust filter..."

# Check if Rust is installed
if ! command -v cargo &> /dev/null; then
    echo "Error: Rust not installed. Install with:"
    echo "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
    exit 1
fi

# Check if maturin is installed
if ! command -v maturin &> /dev/null; then
    echo "Installing maturin..."
    pip install maturin
fi

# Build the Rust extension
echo "Building Rust extension..."
maturin develop --release

if [ $? -eq 0 ]; then
    echo "✅ Filter built successfully!"
    echo "Ready to use in Python:"
    echo "  from frame_change_detector import FrameChangeDetector"
else
    echo "❌ Build failed!"
    exit 1
fi