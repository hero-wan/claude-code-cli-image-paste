# -*- coding: utf-8 -*-
"""生成项目图标 assets/icon.ico"""
from PIL import Image, ImageDraw


def create_icon(output_path):
    sizes = [16, 32, 48, 128, 256]
    images = []

    for size in sizes:
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        margin = max(1, size // 16)
        bg = (74, 144, 226, 255)

        # 圆角矩形背景（用普通矩形近似，小尺寸圆角意义不大）
        draw.rectangle([margin, margin, size - margin, size - margin], fill=bg)

        white = (255, 255, 255, 255)
        frame = size // 4
        thickness = max(1, size // 32)

        # 图片外框
        draw.rectangle(
            [frame, frame, size - frame, size - frame],
            outline=white,
            width=thickness,
        )

        # 山（三角形）
        base_y = size - frame - thickness
        peak_y = frame + (size - 2 * frame) // 3
        left_x = frame + (size - 2 * frame) // 5
        right_x = size - frame - (size - 2 * frame) // 5
        peak_x = (left_x + right_x) // 2 + (size - 2 * frame) // 8

        draw.polygon(
            [(left_x, base_y), (peak_x, peak_y), (right_x, base_y)],
            fill=white,
        )

        # 太阳（小圆）
        sun_r = max(1, size // 14)
        sun_x = size - frame - (size - 2 * frame) // 3
        sun_y = frame + (size - 2 * frame) // 4
        draw.ellipse(
            [sun_x - sun_r, sun_y - sun_r, sun_x + sun_r, sun_y + sun_r],
            fill=white,
        )

        images.append(img)

    images[0].save(output_path, format="ICO", sizes=[(s, s) for s in sizes])


if __name__ == "__main__":
    from pathlib import Path

    out = Path(__file__).resolve().parent.parent / "assets" / "icon.ico"
    out.parent.mkdir(parents=True, exist_ok=True)
    create_icon(str(out))
    print(f"图标已生成: {out}")
