from pathlib import Path
import subprocess

from PIL import Image, ImageDraw


ROOT = Path("/Users/jaysen/Desktop/cb")
SRC_SVG = ROOT / "logo.svg"
WORK_DIR = ROOT / "twopixel-v2" / ".tmp_icon_build"
RAW_PNG = WORK_DIR / "logo_raw_1024.png"
ICONS_DIR = ROOT / "twopixel-v2" / "dashboard" / "src-tauri" / "icons"
ASSETS_DIR = ROOT / "twopixel-v2" / "dashboard" / "src" / "assets" / "images"
PUBLIC_DIR = ROOT / "twopixel-v2" / "dashboard" / "public"


def build_icon(base_logo: Image.Image, size: int) -> Image.Image:
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    bg = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    margin = int(size * 0.08)
    bg_size = size - margin * 2
    ImageDraw.Draw(bg).rounded_rectangle(
        (margin, margin, margin + bg_size, margin + bg_size),
        radius=int(bg_size * 0.24),
        fill=(15, 15, 17, 255),
    )
    canvas.alpha_composite(bg)
    content = int(bg_size * 0.85)
    mark = base_logo.resize((content, content), Image.Resampling.LANCZOS)
    canvas.alpha_composite(mark, dest=((size - content) // 2, (size - content) // 2))
    return canvas


def main() -> None:
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "/opt/homebrew/bin/rsvg-convert",
            "-w",
            "1024",
            "-h",
            "1024",
            "-o",
            str(RAW_PNG),
            str(SRC_SVG),
        ],
        check=True,
    )

    logo = Image.open(RAW_PNG).convert("RGBA")
    png_targets = {
        "32x32.png": 32,
        "128x128.png": 128,
        "128x128@2x.png": 256,
        "Square30x30Logo.png": 30,
        "Square44x44Logo.png": 44,
        "Square71x71Logo.png": 71,
        "Square89x89Logo.png": 89,
        "Square107x107Logo.png": 107,
        "Square142x142Logo.png": 142,
        "Square150x150Logo.png": 150,
        "Square284x284Logo.png": 284,
        "Square310x310Logo.png": 310,
        "StoreLogo.png": 50,
        "icon.png": 512,
    }
    for name, size in png_targets.items():
        build_icon(logo, size).save(ICONS_DIR / name, format="PNG")

    build_icon(logo, 256).save(
        ICONS_DIR / "icon.ico",
        format="ICO",
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    build_icon(logo, 1024).save(ICONS_DIR / "icon.icns", format="ICNS")
    build_icon(logo, 220).save(ASSETS_DIR / "astrbot_logo_mini.webp", format="WEBP", quality=95)
    build_icon(logo, 120).save(ASSETS_DIR / "plugin_icon.png", format="PNG")
    build_icon(logo, 256).save(PUBLIC_DIR / "favicon.png", format="PNG")


if __name__ == "__main__":
    main()
