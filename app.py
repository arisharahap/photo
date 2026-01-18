from flask import Flask, render_template, request, jsonify, send_from_directory, session
import base64
import time
import os
import json
from processor import process_image_multi
from printer_module import print_photo
import socket  # Kita butuh ini untuk mencari IP Laptop
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
app.secret_key = 'SELFBOOTH_SECRET_KEY_123' # Wajib untuk session

# --- KONFIGURASI EMAIL ---
EMAIL_PENGIRIM = "photobooth.cafe.project@gmail.com"  # GANTI DENGAN EMAIL ANDA
PASSWORD_APP   = "ryzf ybjp fgeb exyz"   # GANTI DENGAN 16 DIGIT APP PASSWORD TADI

# --- KONFIGURASI ---
HARGA_SATUAN = 35000
FOLDER_HASIL = 'results'
FILE_VOUCHER = 'vouchers.json'
FILE_FRAMES = 'frames.json'

if not os.path.exists(FOLDER_HASIL): os.makedirs(FOLDER_HASIL)

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Tidak perlu konek internet beneran, cuma pancingan
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

# --- FUNGSI BANTUAN ---
def load_json(filename):
    if not os.path.exists(filename): return {}
    with open(filename, 'r') as f: return json.load(f)

def save_json(filename, data):
    with open(filename, 'w') as f: json.dump(data, f, indent=2)

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('index.html', harga_satuan=HARGA_SATUAN)

# API: Request QR Code (Simulasi)
@app.route('/get_qrcode')
def get_qrcode():
    qty = int(request.args.get('qty', 1))
    session['print_qty'] = qty  # Simpan qty di session
    
    total = qty * HARGA_SATUAN
    order_id = f"ORDER-{int(time.time())}"
    
    # URL QR Code Google Chart (Simulasi)
    # Nanti ganti logika ini dengan Midtrans Snap API
    fake_qr = f"https://chart.googleapis.com/chart?chs=300x300&cht=qr&chl=Tagihan Rp{total}"
    
    return jsonify({"status": "success", "qr_url": fake_qr, "order_id": order_id, "total": total})

# API: Redeem Voucher
@app.route('/redeem_voucher', methods=['POST'])
def redeem_voucher():
    code = request.json.get('code', '').strip().upper()
    qty = int(request.json.get('qty', 1))
    
    vouchers = load_json(FILE_VOUCHER)
    
    if code in vouchers and vouchers[code] > 0:
        vouchers[code] -= 1  # Kurangi kuota
        save_json(FILE_VOUCHER, vouchers)
        
        session['print_qty'] = qty # Set session
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error", "message": "Kode Invalid / Habis"})

# Halaman Pilih Frame
@app.route('/select_frame')
def select_frame():
    frames = load_json(FILE_FRAMES)
    return render_template('select_frame.html', frames=frames)

# Halaman Kamera
@app.route('/camera')
def camera():
    frame_key = request.args.get('frame_key')
    frames = load_json(FILE_FRAMES)
    # Kirim config frame spesifik ke HTML
    return render_template('camera.html', frame_config=frames.get(frame_key), frame_key=frame_key)

# API: Proses Foto Final
@app.route('/process_photo', methods=['POST'])
def process_photo_route():
    data = request.json
    images_base64 = data['images'] # Array foto dari frontend
    frame_key = data['frame_key']
    
    frames = load_json(FILE_FRAMES)
    frame_config = frames.get(frame_key)
    
    # 1. Decode Base64 ke File Temp
    temp_paths = []
    for i, img_str in enumerate(images_base64):
        header, encoded = img_str.split(",", 1)
        data = base64.b64decode(encoded)
        path = f"temp_{int(time.time())}_{i}.jpg"
        with open(path, "wb") as f: f.write(data)
        temp_paths.append(path)
        
    # 2. Gabungkan Foto + Frame
    final_filename = f"final_{int(time.time())}.jpg"
    final_path = os.path.join(FOLDER_HASIL, final_filename)
    
    # Panggil Logic Processor
    process_image_multi(temp_paths, frame_config, final_path)
    
    # 3. Print Sesuai Jumlah Bayar
    qty_print = session.get('print_qty', 1)
    print(f"Mencetak file {final_filename} sebanyak {qty_print} kali.")
    
    for _ in range(qty_print):
        # Uncomment baris bawah jika printer sudah siap
        # print_photo(final_path)
        pass
        
    # 4. Hapus File Temp
    for p in temp_paths:
        if os.path.exists(p): os.remove(p)
        
    return jsonify({"status": "success", "filename": final_filename})

@app.route('/upload_and_print')
def upload_and_print_route():
    filename = request.args.get('file')
    qty = session.get('print_qty', 1)

    # 1. Dapatkan IP Laptop (Contoh: 192.168.1.10)
    my_ip = get_ip_address()

    # 2. Buat Link Lokal untuk QR Code
    # HP user harus satu WiFi dengan laptop untuk bisa buka link ini
    local_link = f"http://{my_ip}:5000/results/{filename}"

    # 3. Kirim Link Lokal ke Browser
    return jsonify({
        "status": "success",
        "link": local_link
    })

# Halaman Hasil
@app.route('/result')
def result():
    filename = request.args.get('file')
    return render_template('result.html', filename=filename)

# Serve File Hasil
@app.route('/results/<filename>')
def serve_result(filename):
    return send_from_directory(FOLDER_HASIL, filename)

# Route khusus untuk menampilkan gambar dari folder 'assets' ke browser
@app.route('/assets_image/<path:filename>')
def serve_assets_image(filename):
    # Tentukan lokasi folder assets
    assets_folder = os.path.join(app.root_path, 'assets')
    # Kirim file gambar yang diminta
    return send_from_directory(assets_folder, filename)

@app.route('/print_now')
def print_now():
    filename = request.args.get('file')
    qty = session.get('print_qty', 1)
    
    final_path = os.path.join(FOLDER_HASIL, filename)
    
    print(f"=== SYSTEM: MENCETAK {filename} SEBANYAK {qty} KALI ===")
    
    for _ in range(qty):
        # print_photo(final_path) # Panggil modul printer Anda
        pass # Pass dulu untuk simulasi
        
    return jsonify({"status": "printed", "qty": qty})

@app.route('/send_email', methods=['POST'])
def send_email_route():
    target_email = request.json.get('email')
    filename = request.json.get('filename')
    file_path = os.path.join(FOLDER_HASIL, filename)

    if not target_email:
        return jsonify({"status": "error", "message": "Email kosong!"})

    try:
        # 1. Siapkan Email
        msg = EmailMessage()
        msg['Subject'] = "Terima Kasih! Ini Foto SelfBooth Kamu 📸"
        msg['From'] = EMAIL_PENGIRIM
        msg['To'] = target_email
        msg.set_content("Halo!\n\nTerima kasih sudah berfoto di SelfBooth kami.\nTerlampir adalah file foto digital kamu.\n\nJangan lupa tag kami ya!\n\nSalam,\nAdmin SelfBooth")

        # 2. Lampirkan Foto
        with open(file_path, 'rb') as f:
            file_data = f.read()
            file_name = os.path.basename(file_path)

        msg.add_attachment(file_data, maintype='image', subtype='jpeg', filename=file_name)

        # 3. Kirim via Server Google
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_PENGIRIM, PASSWORD_APP)
            smtp.send_message(msg)

        return jsonify({"status": "success"})

    except Exception as e:
        print(f"Error Email: {e}")
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    # Host 0.0.0.0 wajib aktif agar bisa diakses dari HP
    app.run(debug=True, port=5000, host='0.0.0.0')