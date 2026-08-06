#!/usr/bin/env python3
# 生成「花园生长状态图」示例 PNG（仅做演示，用户可直接删除替换成自己的图）
# 用 Python 标准库绘制：透明背景 + 一只随生长值变大/开花的小花
import zlib, struct, math, os

SIZE = 152
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')

SEEDS = [
    ('sakura',      (255, 214, 231)),
    ('lotus',       (200, 238, 240)),
    ('jasmine',     (255, 243, 196)),
    ('sunflower',   (255, 224, 138)),
    ('lilyofvalley',(214, 240, 255)),
    ('tulip',       (255, 198, 224)),
    ('wintersweet', (255, 240, 168)),
    ('rose',        (255, 192, 204)),
    ('peony',       (255, 179, 200)),
    ('clover',      (200, 240, 192)),
]

GREEN = (110, 200, 120)
BROWN = (150, 110, 70)
YELLOW = (255, 214, 90)
GRAY = (170, 165, 160)

# 透明 RGBA 画布
def new_canvas():
    return [[(0, 0, 0, 0) for _ in range(SIZE)] for _ in range(SIZE)]

def blend(canvas, x, y, r, g, b, a):
    if x < 0 or y < 0 or x >= SIZE or y >= SIZE or a <= 0:
        return
    br, bg, bb, ba = canvas[y][x]
    # 简单 alpha 合成（canvas 底色透明）
    na = ba + a * (255 - ba) / 255.0
    if na <= 0:
        return
    nr = (br * ba + r * a * (255 - ba) / 255.0) / na
    ng = (bg * ba + g * a * (255 - ba) / 255.0) / na
    nb = (bb * ba + b * a * (255 - ba) / 255.0) / na
    canvas[y][x] = (int(nr), int(ng), int(nb), int(na))

def fill_circle(canvas, cx, cy, rad, rgb, a=255):
    for y in range(int(cy - rad) - 1, int(cy + rad) + 2):
        for x in range(int(cx - rad) - 1, int(cx + rad) + 2):
            if (x - cx) ** 2 + (y - cy) ** 2 <= rad * rad:
                blend(canvas, x, y, rgb[0], rgb[1], rgb[2], a)

def fill_ellipse(canvas, cx, cy, rx, ry, rgb, a=255):
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1:
                blend(canvas, x, y, rgb[0], rgb[1], rgb[2], a)

def line(canvas, x0, y0, x1, y1, rgb, thick=3, a=255):
    steps = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
    for i in range(steps + 1):
        t = i / steps
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * t
        fill_circle(canvas, x, y, thick, rgb, a)

def draw_flower(canvas, color, growth):
    cx = SIZE // 2
    base_y = SIZE - 16
    if growth <= 0:
        # 种子
        fill_ellipse(canvas, cx, base_y - 4, 9, 12, BROWN, 255)
        return
    t = growth / 10.0
    stem_h = 30 + int(70 * t)
    top_y = base_y - stem_h
    # 茎
    line(canvas, cx, base_y, cx, top_y, GREEN, 4)
    # 叶子
    leaf_y = base_y - stem_h * 0.45
    fill_ellipse(canvas, cx - 16, leaf_y, 14, 7, GREEN, 235)
    fill_ellipse(canvas, cx + 16, leaf_y, 14, 7, GREEN, 235)
    if growth < 4:
        # 嫩芽（小绿点）
        fill_circle(canvas, cx, top_y, 6 + 2 * t, GREEN, 255)
        return
    # 开花：花瓣数量固定，大小随生长增大
    petal_r = 8 + 14 * (growth - 3) / 7.0
    n = 6
    for k in range(n):
        ang = 2 * math.pi * k / n - math.pi / 2
        px = cx + math.cos(ang) * petal_r * 0.9
        py = top_y + math.sin(ang) * petal_r * 0.9
        fill_circle(canvas, px, py, petal_r, color, 250)
    # 花心
    fill_circle(canvas, cx, top_y, 7 + 3 * t, YELLOW, 255)

def draw_withered(canvas):
    cx = SIZE // 2
    base_y = SIZE - 16
    # 垂头枯茎
    line(canvas, cx, base_y, cx - 10, base_y - 40, GRAY, 4)
    fill_circle(canvas, cx - 14, base_y - 46, 10, GRAY, 230)
    fill_ellipse(canvas, cx - 26, base_y - 30, 12, 6, GRAY, 200)
    fill_ellipse(canvas, cx + 22, base_y - 30, 12, 6, GRAY, 200)

def draw_disappeared(canvas):
    # 空花盆 + 淡淡的 X
    cx = SIZE // 2
    base_y = SIZE - 20
    fill_ellipse(canvas, cx, base_y, 30, 18, (210, 205, 200), 200)
    # X
    for d in range(-14, 15):
        blend(canvas, cx + d, base_y - 30 + d, 150, 150, 150, 120)
        blend(canvas, cx + d, base_y - 30 - d, 150, 150, 150, 120)

def write_png(path, canvas):
    raw = bytearray()
    for y in range(SIZE):
        raw.append(0)  # filter type 0
        for x in range(SIZE):
            r, g, b, a = canvas[y][x]
            raw += bytes((r, g, b, a))
    comp = zlib.compress(bytes(raw), 9)
    def chunk(typ, data):
        c = struct.pack('>I', len(data)) + typ + data
        crc = zlib.crc32(typ + data) & 0xffffffff
        return c + struct.pack('>I', crc)
    ihdr = struct.pack('>IIBBBBB', SIZE, SIZE, 8, 6, 0, 0, 0)  # 8-bit RGBA
    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n')
        f.write(chunk(b'IHDR', ihdr))
        f.write(chunk(b'IDAT', comp))
        f.write(chunk(b'IEND', b''))

def main():
    os.makedirs(OUT, exist_ok=True)
    for key, color in SEEDS:
        # 生长阶段 0..10
        for g in range(0, 11):
            c = new_canvas()
            draw_flower(c, color, g)
            write_png(os.path.join(OUT, f'{key}_g{g}.png'), c)
        # 枯萎 / 消失
        c = new_canvas(); draw_withered(c)
        write_png(os.path.join(OUT, f'{key}_withered.png'), c)
        c = new_canvas(); draw_disappeared(c)
        write_png(os.path.join(OUT, f'{key}_disappeared.png'), c)
    print('示例图已生成到', OUT)

if __name__ == '__main__':
    main()
