import os
import shutil
from .config import ProfileFactory, OptimizerConfig
from .optimizers.image_opt import ImageOptimizer
from .optimizers.audio_opt import AudioOptimizer

class AssetPipeline:
    def __init__(self, config: OptimizerConfig = None):
        # Default to medium if no config provided
        if config is None:
            config = ProfileFactory.get_profile("medium")
            
        self.config = config
        self.img_optimizer = ImageOptimizer(config)
        self.audio_optimizer = AudioOptimizer(config)
        self.stats = {'original': 0, 'optimized': 0}

    def process_directory(self, input_dir, output_dir, file_types):
        print(f"--- 🚀 Starting asset optimization for {file_types} (Width: {self.config.max_width}px) ---")
        
        for root, _, files in os.walk(input_dir):
            for file in files:
                input_path = os.path.join(root, file)
                
                # Calculate relative path to maintain structure
                rel_path = os.path.relpath(root, input_dir)
                dest_folder = os.path.join(output_dir, rel_path)
                
                if not os.path.exists(dest_folder):
                    os.makedirs(dest_folder)
                
                output_path = os.path.join(dest_folder, file) 
                
                ext = file.lower().split('.')[-1]
                success = False

                if ext in ['jpg', 'jpeg', 'png'] and 'image' in file_types:
                    success = self.img_optimizer.optimize(input_path, output_path)
                elif ext in ['mp3', 'wav', 'ogg', 'm4a', 'flac', 'aac'] and 'audio' in file_types:
                    output_path = os.path.splitext(output_path)[0] + '.mp3'
                    success = self.audio_optimizer.optimize(input_path, output_path)
                
                if success:
                    self._update_stats(input_path, output_path)

        self._print_summary()
        return self.stats

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

        print(f"\n📊 SUMMARY")
        print(f"🔹 Original : {org_kb:.2f} KB")
        print(f"🔹 Optimized : {opt_kb:.2f} KB")
        print(f"🔻 Reduced: {percent:.2f}%")

def optimize_images(input_dir: str, output_dir: str, level: str = "medium", width: int = None):
    config = ProfileFactory.get_profile(level)
    if width:
        config.max_width = width
    pipeline = AssetPipeline(config)
    return pipeline.process_directory(input_dir, output_dir, file_types=['image'])

def optimize_audio(input_dir: str, output_dir: str, level: str = "medium"):
    # Audio usually doesn't need width override, but keeps consistent signature or uses just level
    config = ProfileFactory.get_profile(level)
    pipeline = AssetPipeline(config)
    return pipeline.process_directory(input_dir, output_dir, file_types=['audio'])
