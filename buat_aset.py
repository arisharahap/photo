import os
from PIL import Image, ImageDraw

# Pastikan folder assets ada
if not os.path.exists('assets'):
    os.makedirs('assets')

def create_dummy_frame(filename, width, height, slots, color):
    # Buat kanvas transparan
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Gambar Border Luar
    draw.rectangle([(0,0), (width-1, height-1)], outline=color, width=20)
    
    # Gambar Slot (Bolong)
    for slot in slots:
        # Gambar kotak outline di area foto agar kelihatan batasnya
        x, y, w, h = slot['x'], slot['y'], slot['width'], slot['height']
        draw.rectangle([(x, y), (x+w, y+h)], outline=color, width=10)
        # Tulis nomor slot (opsional, biar tau posisi)
    
    path = f"assets/{filename}"
    img.save(path)
    print(f"✅ Berhasil membuat: {path}")

# 1. Single Frame (1 Foto)
create_dummy_frame("frame_single.png", 1200, 1800, [
    {"x": 100, "y": 100, "width": 1000, "height": 1600}
], 'red')

# 2. Strip Frame (3 Foto)
create_dummy_frame("frame_strip.png", 1200, 1800, [
    {"x": 50, "y": 50, "width": 1100, "height": 500},
    {"x": 50, "y": 600, "width": 1100, "height": 500},
    {"x": 50, "y": 1150, "width": 1100, "height": 500}
], 'blue')

# 3. Collage Frame (4 Foto)
create_dummy_frame("frame_collage.png", 1200, 1800, [
    {"x": 50, "y": 50, "width": 525, "height": 825},
    {"x": 625, "y": 50, "width": 525, "height": 825},
    {"x": 50, "y": 925, "width": 525, "height": 825},
    {"x": 625, "y": 925, "width": 525, "height": 825}
], 'green')