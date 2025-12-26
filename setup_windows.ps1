# Windows PowerShell Setup Script for IndexTTS2 API
# Sets up environment variables for Windows PowerShell

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "IndexTTS2 API Windows Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set Hugging Face Token
# Replace YOUR_HF_TOKEN_HERE with your actual Hugging Face token
$env:HF_TOKEN = "YOUR_HF_TOKEN_HERE"
$env:HUGGINGFACE_HUB_TOKEN = "YOUR_HF_TOKEN_HERE"

Write-Host "✅ Hugging Face token set" -ForegroundColor Green
Write-Host ""

# Activate virtual environment (adjust path as needed)
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
    Write-Host "✅ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "⚠️  Virtual environment not found" -ForegroundColor Yellow
    Write-Host "   Create with: python -m venv venv" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now run:" -ForegroundColor Green
Write-Host '  python run_emotion_generations.py --voice "path\to\voice.wav" --text "Your text"' -ForegroundColor White
Write-Host ""

