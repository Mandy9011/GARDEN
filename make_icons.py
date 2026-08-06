import struct, zlib, math

def write_png(path, w, h, rows):
    raw = bytearray()
    for row in rows:
        raw.append(0)          # filter type none
        raw.extend(row)
    comp = zlib.compress(bytes(raw), 9)
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)))  # RGBA
        f.write(chunk(b"IDAT", comp))
        f.write(chunk(b"IEND", b""))

def make_icon(size):
    cx = size // 2
    cy = int(size * 0.46)
    bg = (255, 228, 238)
    rows = []
    for y in range(size):
        row = bytearray()
        for x in range(size):
            r, g, b = bg
            dx = x - cx
            dy = y - cy
            d = math.hypot(dx, dy)
            ang = math.atan2(dy, dx)
            # 花瓣环（带波浪边，像雏菊）
            if 0.30 * size <= d <= 0.43 * size:
                if math.cos(ang * 12) > -0.25:
                    r, g, b = (255, 209, 102)
            # 花心
            if d < 0.27 * size:
                r, g, b = (214, 140, 60)
            if d < 0.13 * size:
                r, g, b = (255, 238, 175)
            # 茎
            if abs(dx) < 0.022 * size and 0 < dy < 0.40 * size:
                r, g, b = (120, 200, 120)
            # 两片叶子
            for sx in (-1, 1):
                lx = dx - sx * 0.13 * size
                ly = dy - 0.30 * size
                if (lx * lx) / ((0.11 * size) ** 2) + (ly * ly) / ((0.05 * size) ** 2) < 1:
                    r, g, b = (120, 200, 120)
            row += bytes((r, g, b, 255))
        rows.append(row)
    return rows

for s, name in [(180, "icon-180.png"), (192, "icon-192.png"), (512, "icon-512.png")]:
    write_png(name, s, s, make_icon(s))
    print("generated", name)
