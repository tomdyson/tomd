#!/bin/bash
# Download Tailwind CLI if not present
if [ ! -f ./tailwindcss ]; then
    curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64
    chmod +x tailwindcss-linux-x64
    mv tailwindcss-linux-x64 tailwindcss
fi

# Build Tailwind CSS
./tailwindcss -i ./tomd/static/css/input.css -o ./tomd/static/css/tailwind.css --minify
