# ==============================================================================
# LabSaathi One-Click Development Launcher (Windows PowerShell)
# Starts the FastAPI Backend (http://127.0.0.1:8000) and React Frontend (http://localhost:5173)
# ==============================================================================

$ErrorActionPreference = "Stop"
$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "Starting LabSaathi Backend (FastAPI + OpenCV + PyMuPDF) on http://127.0.0.1:8000 ..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$RootDir'; .\.venv\Scripts\uvicorn.exe backend.main:app --host 127.0.0.1 --port 8000 --reload"

Write-Host "Starting LabSaathi Frontend (React + Vite + Tailwind CSS) on http://localhost:5173 ..." -ForegroundColor Teal
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$RootDir\frontend'; npm.cmd run dev"

Write-Host "LabSaathi is launching! Open http://localhost:5173 in your browser." -ForegroundColor Green
