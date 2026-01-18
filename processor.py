from PIL import Image

def process_image_multi(photo_paths, frame_config, output_path):
    # 1. Load Frame PNG
    frame_file = f"assets/{frame_config['file']}"
    try:
        frame_img = Image.open(frame_file).convert("RGBA")
    except:
        print(f"Error: Aset {frame_file} tidak ditemukan!")
        return

    # 2. Buat Kanvas Putih
    canvas = Image.new("RGBA", frame_img.size, (255, 255, 255))
    
    # 3. Tempel Foto User ke Slot
    slots = frame_config['slots']
    
    # Zip akan berhenti pada list terpendek (Handling slot kosong otomatis)
    for photo_path, slot in zip(photo_paths, slots):
        try:
            user_img = Image.open(photo_path).convert("RGBA")
            # Resize
            user_img = user_img.resize((slot['width'], slot['height']), Image.LANCZOS)
            # Tempel
            canvas.paste(user_img, (slot['x'], slot['y']))
        except Exception as e:
            print(f"Gagal proses foto: {e}")
            continue

    # 4. Tempel Frame Overlay
    canvas.paste(frame_img, (0, 0), frame_img)
    
    # 5. Simpan JPG
    canvas.convert("RGB").save(output_path, quality=95)