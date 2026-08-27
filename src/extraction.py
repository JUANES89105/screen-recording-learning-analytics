"""Video extraction and OCR reconstructed from the historical notebook."""
from __future__ import annotations
from pathlib import Path
import shutil, subprocess
import cv2
import pandas as pd
import pytesseract
from PIL import Image
from skimage.metrics import structural_similarity as ssim

VIDEO_EXTENSIONS={".mp4",".mov",".avi",".mkv",".webm"}

def convert_video(input_path, output_path, overwrite=False):
    input_path,output_path=Path(input_path),Path(output_path); output_path.parent.mkdir(parents=True,exist_ok=True)
    if output_path.exists() and not overwrite: return output_path
    if shutil.which("ffmpeg") is None: raise RuntimeError("ffmpeg was not found on PATH")
    cmd=["ffmpeg","-y" if overwrite else "-n","-i",str(input_path),"-vcodec","libx264","-pix_fmt","yuv420p","-acodec","aac",str(output_path)]
    r=subprocess.run(cmd,capture_output=True,text=True)
    if r.returncode: raise RuntimeError(f"ffmpeg failed for {input_path.name}: {r.stderr[-2000:]}")
    return output_path

def extract_screenshots(video_path, output_dir, frame_step_seconds=1.0, ssim_threshold=0.90):
    video_path,output_dir=Path(video_path),Path(output_dir); output_dir.mkdir(parents=True,exist_ok=True)
    cap=cv2.VideoCapture(str(video_path))
    if not cap.isOpened(): raise RuntimeError(f"Could not open video: {video_path}")
    fps=cap.get(cv2.CAP_PROP_FPS) or 30.0; frame_count=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); interval=max(1,int(round(fps*frame_step_seconds))); total=frame_count/fps
    ok,prev=cap.read()
    if not ok: cap.release(); raise RuntimeError(f"Could not read first frame: {video_path}")
    prev_gray=cv2.cvtColor(prev,cv2.COLOR_BGR2GRAY); first="000_t0.00.png"; cv2.imwrite(str(output_dir/first),prev)
    rows=[{"entrada":0.0,"salida":None,"tiempo":None,"captura":first,"ssim_cambio":None}]; saved=1; idx=interval
    while idx<frame_count:
        cap.set(cv2.CAP_PROP_POS_FRAMES,idx); ok,frame=cap.read()
        if not ok: break
        gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY); similarity=float(ssim(prev_gray,gray)); prev_gray=gray
        if similarity<ssim_threshold:
            t=idx/fps; rows[-1]["salida"]=round(t,2); rows[-1]["tiempo"]=round(t-rows[-1]["entrada"],2)
            name=f"{saved:03d}_t{t:.2f}.png"; cv2.imwrite(str(output_dir/name),frame)
            rows.append({"entrada":round(t,2),"salida":None,"tiempo":None,"captura":name,"ssim_cambio":round(similarity,6)}); saved+=1
        idx+=interval
    cap.release(); rows[-1]["salida"]=round(total,2); rows[-1]["tiempo"]=round(total-rows[-1]["entrada"],2)
    return pd.DataFrame(rows)

def run_ocr(captures_dir, language="spa"):
    rows = []

    for p in sorted(Path(captures_dir).iterdir()):

        if p.suffix.lower() not in {
            ".png", ".jpg", ".jpeg", ".bmp", ".tiff"
        }:
            continue

        try:
            with Image.open(p) as im:

                # Primary OCR:
                # PSM 6 assumes one main block of text and performed
                # substantially better on browser screenshots in testing.
                text = pytesseract.image_to_string(
                    im,
                    lang=language,
                    config="--psm 6"
                )

                ocr_mode = "psm6"

                # Fallback for sparse OCR results.
                # PSM 11 searches for sparse text across the screen.
                if len(text.strip()) < 40:

                    text_fallback = pytesseract.image_to_string(
                        im,
                        lang=language,
                        config="--psm 11"
                    )

                    if len(text_fallback.strip()) > len(text.strip()):
                        text = text_fallback
                        ocr_mode = "psm11_fallback"

            error = ""

        except Exception as exc:
            text = ""
            error = str(exc)
            ocr_mode = "error"

        rows.append({
            "captura": p.name,
            "texto": text,
            "ocr_mode": ocr_mode,
            "ocr_error": error
        })

    return pd.DataFrame(rows)


def process_video(video_path, output_dir, frame_step_seconds=1.0, ssim_threshold=0.90, ocr_language="spa"):
    a=extract_screenshots(video_path,output_dir,frame_step_seconds,ssim_threshold); b=run_ocr(output_dir,ocr_language); df=a.merge(b,on="captura",how="left")
    df["archivo"]=Path(video_path).name; df["origen"]=str(Path(video_path)); return df

def process_video_directory(input_dir, converted_dir, results_dir, convert=True, frame_step_seconds=1.0, ssim_threshold=0.90, ocr_language="spa"):
    input_dir,converted_dir,results_dir=map(Path,(input_dir,converted_dir,results_dir)); converted_dir.mkdir(parents=True,exist_ok=True); results_dir.mkdir(parents=True,exist_ok=True)
    outputs=[]
    for video in sorted(p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() in VIDEO_EXTENSIONS):
        target=converted_dir/f"{video.stem}.mp4"
        if convert: target=convert_video(video,target)
        else: target=video
        out=results_dir/video.stem; out.mkdir(parents=True,exist_ok=True); df=process_video(target,out,frame_step_seconds,ssim_threshold,ocr_language)
        x=out/f"registro_navegacion_{video.stem}.xlsx"; df.to_excel(x,index=False); outputs.append(x)
    return outputs
