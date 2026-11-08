#!/bin/bash
set -e

TAILWIND_VERSION=v4.3.5

# Download Tailwind CLI if not present
if [ ! -f ./tailwindcss ]; then
    case "$(uname -s)-$(uname -m)" in
        Linux-x86_64) target=linux-x64 ;;
        Linux-aarch64) target=linux-arm64 ;;
        Darwin-arm64) target=macos-arm64 ;;
        Darwin-x86_64) target=macos-x64 ;;
        *) echo "No Tailwind CLI for $(uname -s)-$(uname -m)" >&2; exit 1 ;;
    esac
    curl -fsSL -o tailwindcss "https://github.com/tailwindlabs/tailwindcss/releases/download/$TAILWIND_VERSION/tailwindcss-$target"
    chmod +x tailwindcss
fi

# Build Tailwind CSS
./tailwindcss -i ./tomd/tailwind/input.css -o ./tomd/static/css/tailwind.css --minify
