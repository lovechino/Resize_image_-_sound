from PIL import Image
from .base import BaseOptimizer
import os

class ImageOptimizer(BaseOptimizer):
    def optimize(self, input_path: str, output_path: str) -> bool:
        try:
            self.ensure_dir(output_path)
            ext = input_path.lower().split('.')[-1]

            with Image.open(input_path) as img:
                # 1. Resize based on config - DISABLED to keep original size
                # if img.width > self.config.max_width:
                #     ratio = self.config.max_width / float(img.width)
                #     new_height = int((float(img.height) * float(ratio)))
                #     img = img.resize((self.config.max_width, new_height), Image.Resampling.LANCZOS)


                # 2. Convert format
                if ext in ['jpg', 'jpeg']:
                    if img.mode != 'RGB': 
                        img = img.convert('RGB')
                    img.save(output_path, "JPEG", 
                             quality=self.config.jpg_quality, 
                             optimize=True, progressive=True)

                elif ext == 'png':
                    if img.mode != 'RGBA': 
                        img = img.convert('RGBA')
                    # Quantize based on config
                    img_p = img.quantize(colors=self.config.png_colors, method=2)
                    img_p.save(output_path, "PNG", optimize=True)
            
            return True
        except Exception as e:
            # Print error for debug
            print(f"❌ [IMG ERROR] {os.path.basename(input_path)} -> {e}")
            return False
