import os
import shutil
import subprocess
import argparse
from PIL import Image
from abc import ABC, abstractmethod
from dataclasses import dataclass

# ==========================================
# 1. CONFIGURATION MANAGEMENT (Quản lý cấu hình)
# ==========================================

@dataclass
class OptimizerConfig:
    """Class lưu trữ cấu hình, không còn là static cứng nhắc"""
    max_width: int
    jpg_quality: int
    png_colors: int
    audio_bitrate: str
    audio_sample_rate: str

class ProfileFactory:
    """Factory Pattern: Tạo cấu hình dựa trên mức độ mong muốn"""
    @staticmethod
    def get_profile(level: str):
        level = level.lower()
        if level == "high":
            # Dành cho PC/Console: Giữ nét căng, chỉ nén nhẹ
            return OptimizerConfig(
                max_width=4096, jpg_quality=85, png_colors=256, 
                audio_bitrate="192k", audio_sample_rate="44100"
            )
        elif level == "medium":
            # Dành cho Mobile tiêu chuẩn (Default)
            return OptimizerConfig(
                max_width=2048, jpg_quality=70, png_colors=64, 
                audio_bitrate="128k", audio_sample_rate="44100"
            )
        elif level == "low":
            # Dành cho Web Game / Máy yếu: Ép dung lượng cực mạnh
            return OptimizerConfig(
                max_width=1024, jpg_quality=50, png_colors=32, 
                audio_bitrate="32k", audio_sample_rate="16000"
            )
        else:
            raise ValueError("Level không hợp lệ. Chọn: low, medium, high")

# ==========================================
# 2. OPTIMIZERS (Bộ xử lý)
# ==========================================
class BaseOptimizer(ABC):
    def __init__(self, config: OptimizerConfig):
        self.config = config # Dependency Injection: Tiêm cấu hình vào

    @abstractmethod
    def optimize(self, input_path: str, output_path: str) -> bool:
        ...

    def ensure_dir(self, file_path: str):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

class ImageOptimizer(BaseOptimizer):
    def optimize(self, input_path: str, output_path: str) -> bool:
        try:
            self.ensure_dir(output_path)
            ext = input_path.lower().split('.')[-1]
            
            with Image.open(input_path) as img:
                # 1. Bỏ qua việc resize theo Config - giữ nguyên Size ảnh gốc
                # if img.width > self.config.max_width:
                #     ratio = self.config.max_width / float(img.width)
                #     new_height = int((float(img.height) * float(ratio)))
                #     img = img.resize((self.config.max_width, new_height), Image.Resampling.LANCZOS)


                # 2. Xử lý nén
                if ext in ['jpg', 'jpeg']:
                    if img.mode != 'RGB': img = img.convert('RGB')
                    img.save(output_path, "JPEG", 
                             quality=self.config.jpg_quality, 
                             optimize=True, progressive=True)

                elif ext == 'png':
                    if img.mode != 'RGBA': img = img.convert('RGBA')
                    # Quantize theo số màu trong Config
                    img_p = img.quantize(colors=self.config.png_colors, method=2)
                    img_p.save(output_path, "PNG", optimize=True)
            return True
        except Exception as e:
            print(f"❌ [IMG ERROR] {os.path.basename(input_path)}: {e}")
            return False

class AudioOptimizer(BaseOptimizer):
    def optimize(self, input_path: str, output_path: str) -> bool:
        if shutil.which("ffmpeg") is None:
            return False
        try:
            self.ensure_dir(output_path)
            cmd = [
                'ffmpeg', '-i', input_path,
                '-codec:a', 'libmp3lame',
                '-b:a', self.config.audio_bitrate,      # Bitrate động
                '-ar', self.config.audio_sample_rate,   # Sample rate động
                '-ac', '1',                             # Vẫn giữ Mono cho game nhẹ
                '-map_metadata', '-1',
                '-y', output_path
            ]
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()  # type: ignore[attr-defined]
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # type: ignore[attr-defined]
            
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, startupinfo=startupinfo)
            return True
        except Exception as e:
            print(f"❌ [AUDIO ERROR] {os.path.basename(input_path)}: {e}")
            return False

# ==========================================
# 3. PIPELINE MANAGER
# ==========================================
class AssetPipeline:
    def __init__(self, input_dir, output_dir, config: OptimizerConfig):
        self.input_dir = input_dir
        self.output_dir = output_dir
        # Khởi tạo các bộ xử lý với Config được chọn
        self.img_optimizer = ImageOptimizer(config)
        self.audio_optimizer = AudioOptimizer(config)
        self.stats = {'original': 0, 'optimized': 0}

    def run(self):
        print(f"--- 🚀 Bắt đầu tối ưu hóa (Width: {self.img_optimizer.config.max_width}px) ---")
        
        # Reset output dir
        if os.path.exists(self.output_dir):
            try: shutil.rmtree(self.output_dir)
            except: pass
        
        for root, _, files in os.walk(self.input_dir):
            for file in files:
                input_path = os.path.join(root, file)
                rel_path = os.path.relpath(root, self.input_dir)
                dest_folder = os.path.join(self.output_dir, rel_path)
                
                if not os.path.exists(dest_folder): os.makedirs(dest_folder)
                output_path = os.path.join(dest_folder, file)

                ext = file.lower().split('.')[-1]
                success = False

                if ext in ['jpg', 'jpeg', 'png']:
                    success = self.img_optimizer.optimize(input_path, output_path)
                elif ext == 'mp3':
                    success = self.audio_optimizer.optimize(input_path, output_path)
                
                if success:
                    self._update_stats(input_path, output_path)

        self._print_summary()

    def _update_stats(self, input_path, output_path):
        org = os.path.getsize(input_path)
        opt = os.path.getsize(output_path)
        self.stats['original'] += org
        self.stats['optimized'] += opt
        print(f"✅ {os.path.basename(input_path)}: {org//1024}KB -> {opt//1024}KB")

    def _print_summary(self):
        org_kb = self.stats['original'] / 1024
        opt_kb = self.stats['optimized'] / 1024
        percent = 100 - (opt_kb / org_kb * 100) if org_kb > 0 else 0
        print("\n" + "="*40)
        print(f"📊 TỔNG KẾT: Giảm {percent:.2f}% ({org_kb:.0f}KB -> {opt_kb:.0f}KB)")
        print("="*40)

# ==========================================
# 4. ENTRY POINT (Giao diện dòng lệnh)
# ==========================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tool tối ưu hóa Assets Game (Clean Code)")
    
    # Các tham số người dùng có thể nhập
    parser.add_argument("--input", default="assets_raw", help="Thư mục đầu vào")
    parser.add_argument("--output", default="assets_optimized", help="Thư mục đầu ra")
    parser.add_argument("--level", choices=["low", "medium", "high"], default="medium", 
                        help="Mức độ nén (Low: Siêu nhẹ, High: Siêu nét)")
    
    # Cho phép ghi đè thông số cụ thể nếu muốn (Advanced)
    parser.add_argument("--width", type=int, help="Ghi đè chiều rộng tối đa (VD: 1920)")

    args = parser.parse_args()

    # 1. Lấy cấu hình chuẩn từ Level
    config = ProfileFactory.get_profile(args.level)
    
    # 2. Nếu người dùng nhập --width, ghi đè vào cấu hình
    if args.width:
        config.max_width = args.width
        print(f"⚠️  Override: Đã đổi chiều rộng tối đa thành {args.width}px")

    # 3. Kiểm tra input
    if not os.path.exists(args.input):
        os.makedirs(args.input)
        print(f"⚠️  Đã tạo thư mục '{args.input}'. Hãy chép file vào rồi chạy lại!")
    else:
        # 4. Chạy Pipeline
        pipeline = AssetPipeline(args.input, args.output, config)
        pipeline.run()