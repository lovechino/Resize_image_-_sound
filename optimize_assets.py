import os
import subprocess
from PIL import Image
import shutil

# CẤU HÌNH CỰC ĐOAN
DEFAULT_INPUT_DIR = "assets_raw"
DEFAULT_OUTPUT_DIR = "assets_optimized"

# 1. THÔNG SỐ ẢNH (Mục tiêu: Tổng ảnh ~400KB)
MAX_WIDTH = 512         # Ép về 512px (Đủ nét cho game trẻ em 4-5 tuổi)
JPG_QUALITY = 30        # Nén JPG mức cao
PNG_COLORS = 16         # Ép PNG về 16 màu (Sẽ xử lý được file 570KB của bạn)

# 2. THÔNG SỐ ÂM THANH (Mục tiêu: Tổng nhạc ~300KB)
# Ép về Mono và Bitrate 32k là cách duy nhất để nhạc cực nhẹ
AUDIO_BITRATE = "32k"   
SAMPLE_RATE = "16000"   

def reset_output(output_dir):
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

def optimize_images(input_dir, output_dir):
    print(f"--- 📸 Đang ép dung lượng ảnh từ {input_dir} đến {output_dir} ---")
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            ext = file.lower().split('.')[-1]
            if ext not in ['jpg', 'jpeg', 'png']: continue

            input_path = os.path.join(root, file)
            rel_path = os.path.relpath(root, input_dir)
            out_dir_path = os.path.join(output_dir, rel_path)
            if not os.path.exists(out_dir_path): os.makedirs(out_dir_path)
            output_path = os.path.join(out_dir_path, file)

            try:
                with Image.open(input_path) as img:
                    # Resize để diệt file 570KB
                    if img.width > MAX_WIDTH:
                        ratio = MAX_WIDTH / float(img.width)
                        new_height = int(float(img.height) * ratio)
                        img = img.resize((MAX_WIDTH, new_height), Image.Resampling.LANCZOS)
                    
                    if ext in ['jpg', 'jpeg']:
                        img.convert("RGB").save(output_path, "JPEG", quality=JPG_QUALITY, optimize=True)
                    elif ext == 'png':
                        if img.mode != 'RGBA': img = img.convert('RGBA')
                        # Ép màu về Palette 16 màu - Cực nhẹ!
                        img_p = img.convert('P', palette=Image.ADAPTIVE, colors=PNG_COLORS)
                        img_p.save(output_path, "PNG", optimize=True)
                
                print(f"✅ Image: {file} -> {os.path.getsize(output_path)//1024}KB")
            except Exception as e:
                print(f"❌ Lỗi ảnh {file}: {e}")

def optimize_audio(input_dir, output_dir):
    print(f"\n--- 🎵 Đang nén MP3 về mức sàn từ {input_dir} đến {output_dir} ---")
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            file_lower = file.lower()
            if not file_lower.endswith('.mp3'): continue

            input_path = os.path.join(root, file)
            rel_path = os.path.relpath(root, input_dir)
            out_dir_path = os.path.join(output_dir, rel_path)
            if not os.path.exists(out_dir_path): os.makedirs(out_dir_path)
            output_path = os.path.join(out_dir_path, file)

            try:
                # Ép về Mono (-ac 1), Bitrate 32k, Sample rate 16k, Xóa metadata
                subprocess.run([
                    'ffmpeg', '-i', input_path,
                    '-codec:a', 'libmp3lame',
                    '-b:a', AUDIO_BITRATE,
                    '-ac', '1',
                    '-ar', SAMPLE_RATE,
                    '-map_metadata', '-1',
                    '-y', output_path
                ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
                print(f"✅ Audio: {file} -> {os.path.getsize(output_path)//1024}KB")
            except Exception as e:
                print(f"❌ Lỗi nhạc {file}: {e}. Đảm bảo đã cài FFmpeg.")

def main():
    reset_output(DEFAULT_OUTPUT_DIR)
    optimize_images(DEFAULT_INPUT_DIR, DEFAULT_OUTPUT_DIR)
    optimize_audio(DEFAULT_INPUT_DIR, DEFAULT_OUTPUT_DIR)
    
    total_size = sum(os.path.getsize(os.path.join(r, f)) for r, d, fs in os.walk(DEFAULT_OUTPUT_DIR) for f in fs)
    print(f"\n🚀 TỔNG DUNG LƯỢNG CUỐI CÙNG: {total_size / 1024:.2f} KB")

if __name__ == "__main__":
    main()