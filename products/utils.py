import os
from django.conf import settings
import barcode
from barcode.writer import ImageWriter


def generate_barcode_image(barcode_number):
    """🎯 توليد صورة باركود وحفظها في media/barcodes"""
    if not barcode_number:
        return None

    # إنشاء المجلد لو مش موجود
    output_dir = os.path.join(settings.MEDIA_ROOT, 'barcodes')
    os.makedirs(output_dir, exist_ok=True)

    # المسار الكامل
    filename = os.path.join(output_dir, f"{barcode_number}.png")

    # توليد الباركود
    ean = barcode.get('code128', str(barcode_number), writer=ImageWriter())
    ean.save(filename.replace('.png', ''))  # المكتبة بتضيف .png تلقائياً

    return f"media/barcodes/{barcode_number}.png"
