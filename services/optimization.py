import os
import shutil
import tempfile
import zipfile
from fastapi import UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from .asset_optimizer import optimize_images, optimize_audio

class OptimizationService:
    def __init__(self, background_tasks: BackgroundTasks):
        self.background_tasks = background_tasks
        self.temp_dir = tempfile.mkdtemp()
        self.input_dir = os.path.join(self.temp_dir, "input")
        self.optimized_dir = os.path.join(self.temp_dir, "optimized")
        
        # Ensure directories exist
        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.optimized_dir, exist_ok=True)
        
        # Schedule cleanup
        self.background_tasks.add_task(self._cleanup_temp_dir, self.temp_dir)

    def _cleanup_temp_dir(self, path: str):
        """Deletes the temporary directory and all its contents."""
        try:
            shutil.rmtree(path)
            print(f"Cleaned up temp dir: {path}")
        except Exception as e:
            print(f"Error cleaning up {path}: {e}")

    async def save_uploads(self, files: list[UploadFile]):
        """Save uploaded files to the input directory."""
        for file in files:
            file_path = os.path.join(self.input_dir, file.filename)
            # Security check
            if not os.path.abspath(file_path).startswith(os.path.abspath(self.input_dir)):
                 continue
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

    def process_assets(self, level: str, width: int | None):
        """Run optimization pipelines."""
        stats_img = optimize_images(self.input_dir, self.optimized_dir, level, width)
        stats_audio = optimize_audio(self.input_dir, self.optimized_dir, level)
        
        # Aggregate stats
        total_original = stats_img['original'] + stats_audio['original']
        total_optimized = stats_img['optimized'] + stats_audio['optimized']
        
        return {
            'original': total_original,
            'optimized': total_optimized
        }

    # ... get_results ...

    async def execute(self, files: list[UploadFile], level: str = "medium", width: int = None):
        """Main execution flow."""
        try:
            await self.save_uploads(files)
            stats = self.process_assets(level, width)
            return self.get_results(stats)
        except Exception as e:
            # If not already handled (like HTTPException), clean up and re-raise
            if not isinstance(e, HTTPException):
                self._cleanup_temp_dir(self.temp_dir)
                raise HTTPException(status_code=500, detail=str(e))
            raise e

    def get_results(self, stats):
        """Prepare and return the response."""
        optimized_files = []
        for root, _, filenames in os.walk(self.optimized_dir):
            for filename in filenames:
                optimized_files.append(os.path.join(root, filename))
        
        if not optimized_files:
             raise HTTPException(status_code=400, detail="No files were successfully optimized.")

        headers = {
            "X-Original-Size": str(stats['original']),
            "X-Optimized-Size": str(stats['optimized'])
        }

        if len(optimized_files) == 1:
            return self._return_single_file(optimized_files[0], headers)
        else:
            return self._return_zip_archive(headers)

    def _return_single_file(self, file_path: str, headers: dict):
        filename = os.path.basename(file_path)
        media_type = "application/octet-stream"
        
        lower_name = filename.lower()
        if lower_name.endswith(('.jpg', '.jpeg')):
            media_type = "image/jpeg"
        elif lower_name.endswith('.png'):
            media_type = "image/png"
        elif lower_name.endswith('.mp3'):
            media_type = "audio/mpeg"
            
        return FileResponse(file_path, filename=filename, media_type=media_type, headers=headers)

    def _return_zip_archive(self, headers: dict):
        shutil.make_archive(self.optimized_dir, 'zip', self.optimized_dir)
        final_zip_path = self.optimized_dir + ".zip"
        return FileResponse(final_zip_path, filename="optimized_assets.zip", media_type="application/zip", headers=headers)
