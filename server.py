from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import shutil
import os
import zipfile
import tempfile
from optimize_assets import optimize_images, optimize_audio

app = FastAPI()

# Mount static directory
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    return RedirectResponse(url="/static/index.html")

def cleanup_temp_dir(path: str):
    """Deletes the temporary directory and all its contents."""
    try:
        shutil.rmtree(path)
        print(f"Cleaned up temp dir: {path}")
    except Exception as e:
        print(f"Error cleaning up {path}: {e}")

@app.post("/optimize")
async def optimize_endpoint(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only ZIP files are allowed")

    # Create a unique temporary directory for this request using tempfile
    # This prevents collisions and handles cleanup more reliably
    temp_dir = tempfile.mkdtemp()
    
    # Define paths within the temp directory
    input_zip_path = os.path.join(temp_dir, "input.zip")
    extract_dir = os.path.join(temp_dir, "extracted")
    optimized_dir = os.path.join(temp_dir, "optimized")
    
    # We'll schedule the cleanup of the ENTIRE temp_dir after the response
    background_tasks.add_task(cleanup_temp_dir, temp_dir)

    try:
        # Save uploaded ZIP
        with open(input_zip_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract ZIP
        with zipfile.ZipFile(input_zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        # Create output directory
        os.makedirs(optimized_dir, exist_ok=True)

        # Process Assets
        optimize_images(extract_dir, optimized_dir)
        optimize_audio(extract_dir, optimized_dir)

        # Zip optimized assets
        # shutil.make_archive creates the zip file at base_name + .zip
        shutil.make_archive(optimized_dir, 'zip', optimized_dir)
        final_zip_path = optimized_dir + ".zip"
        
        # Return the file. The cleanup task will run after the response is sent.
        return FileResponse(final_zip_path, filename="optimized_assets.zip", media_type="application/zip")

    except Exception as e:
        # If an error occurs, we should verify cleanup happens.
        # BackgroundTasks might not run if an exception is raised before return,
        # so we clean up immediately here.
        cleanup_temp_dir(temp_dir)
        raise HTTPException(status_code=500, detail=str(e))
