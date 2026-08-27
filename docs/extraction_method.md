# Video extraction and OCR method

The clean extraction module reconstructs `notebooks_originales/videos_analisis.ipynb`. Videos are optionally normalized with ffmpeg (H.264/yuv420p/AAC). OpenCV samples approximately one frame per second. Each sampled grayscale frame is compared with the immediately preceding sampled frame using SSIM. A screenshot is stored when SSIM is below 0.90. Entry/exit timestamps define screenshot duration. Tesseract OCR is then applied in Spanish (`spa`) by default.

The historical notebook classified sites immediately after OCR. The clean pipeline deliberately separates extraction/OCR from classification: OCR produces evidence, while `config/sites.yaml` defines the classification rules. This permits rule changes without rerunning video processing.
