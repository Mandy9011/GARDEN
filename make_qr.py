#!/usr/bin/env python3
# 把指定网址生成二维码 PNG（用于微信扫码打开）
import sys
import qrcode

URL = sys.argv[1] if len(sys.argv) > 1 else 'https://example.com'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'qr.png'

qr = qrcode.QRCode(
    version=None,            # 自动选版本
    error_correction=qrcode.constants.ERROR_CORRECTION_M,
    box_size=12,
    border=4,
)
qr.add_data(URL)
qr.make(fit=True)
img = qr.make_image(fill_color='#5a3a45', back_color='white')
img.save(OUT)
print('二维码已生成:', OUT, '->', URL)
