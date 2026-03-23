from fastapi import FastAPI, File, UploadFile, BackgroundTasks, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from services.optimization import OptimizationService
import os

app = FastAPI()

# Mount static directory
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    return RedirectResponse(url="/static/index.html")

@app.post("/optimize")
async def optimize_endpoint(
    background_tasks: BackgroundTasks, 
    files: list[UploadFile] = File(...),
    level: str = Form("medium"),
    width: int = Form(None)
):
    service = OptimizationService(background_tasks)
    return await service.execute(files, level, width)
