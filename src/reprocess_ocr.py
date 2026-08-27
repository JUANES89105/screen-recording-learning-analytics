from __future__ import annotations

import argparse
from pathlib import Path
from zipfile import ZipFile
from io import BytesIO

import pandas as pd
import pytesseract
from PIL import Image


# ============================================================
# OCR
# ============================================================

def ocr_image_bytes(
    data: bytes,
    language: str = "spa",
):
    try:
        with Image.open(BytesIO(data)) as im:

            text = pytesseract.image_to_string(
                im,
                lang=language,
                config="--psm 6",
            )

            mode = "psm6"

            # Fallback para capturas con poco texto
            if len(text.strip()) < 40:

                fallback = pytesseract.image_to_string(
                    im,
                    lang=language,
                    config="--psm 11",
                )

                if len(fallback.strip()) > len(text.strip()):
                    text = fallback
                    mode = "psm11_fallback"

        return text, mode, ""

    except Exception as exc:
        return "", "error", str(exc)


# ============================================================
# ARGUMENTOS
# ============================================================

def parse_args():

    parser = argparse.ArgumentParser(
        description=(
            "Reprocess OCR for the screen-recording corpus "
            "using PSM 6 with PSM 11 fallback."
        )
    )

    parser.add_argument(
        "--master",
        type=Path,
        required=True,
        help="Master Excel file containing the segment metadata.",
    )

    parser.add_argument(
        "--zip-first",
        type=Path,
        required=True,
        help="ZIP file corresponding to 'Primer grupo'.",
    )

    parser.add_argument(
        "--zip-second",
        type=Path,
        required=True,
        help="ZIP file corresponding to 'Segundo grupo'.",
    )

    parser.add_argument(
        "--zip-third",
        type=Path,
        required=True,
        help="ZIP file corresponding to 'Tercer grupo'.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output Excel file.",
    )

    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=Path(
            "data/intermediate/ocr_checkpoint.csv"
        ),
        help="Checkpoint CSV file.",
    )

    parser.add_argument(
        "--language",
        default="spa",
        help="Tesseract OCR language. Default: spa",
    )

    parser.add_argument(
        "--checkpoint-every",
        type=int,
        default=100,
        help="Save checkpoint every N newly processed segments.",
    )

    return parser.parse_args()


# ============================================================
# MAIN
# ============================================================

def main():

    args = parse_args()

    zips = {
        "Primer grupo": args.zip_first,
        "Segundo grupo": args.zip_second,
        "Tercer grupo": args.zip_third,
    }

    # --------------------------------------------------------
    # Validaciones iniciales
    # --------------------------------------------------------

    if not args.master.exists():
        raise FileNotFoundError(
            f"Master file not found: {args.master}"
        )

    for grupo, zip_path in zips.items():
        if not zip_path.exists():
            raise FileNotFoundError(
                f"ZIP file not found for {grupo}: {zip_path}"
            )

    args.output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    args.checkpoint.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Cargar maestro
    # --------------------------------------------------------

    df = pd.read_excel(args.master)

    required_columns = {
        "video_id",
        "Captura",
        "grupo_zip",
        "carpeta_video",
    }

    missing_columns = (
        required_columns
        - set(df.columns)
    )

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(
                sorted(missing_columns)
            )
        )

    print("=" * 100)
    print("REPROCESAMIENTO OCR")
    print("=" * 100)
    print(f"Maestro:       {args.master}")
    print(f"Videos:        {df['video_id'].nunique()}")
    print(f"Segmentos:     {len(df)}")
    print(f"Idioma OCR:    {args.language}")
    print()

    # --------------------------------------------------------
    # Clave única
    # --------------------------------------------------------

    df["segment_key"] = (
        df["video_id"].astype(str)
        + "::"
        + df["Captura"].astype(str)
    )

    if df["segment_key"].duplicated().any():
        raise ValueError(
            "segment_key is not unique. "
            "Check video_id and Captura."
        )

    # --------------------------------------------------------
    # Checkpoint
    # --------------------------------------------------------

    if args.checkpoint.exists():

        checkpoint = pd.read_csv(
            args.checkpoint,
            dtype={"segment_key": str},
        )

        done = set(
            checkpoint["segment_key"]
        )

        print(
            f"Checkpoint encontrado: "
            f"{len(done)} segmentos ya procesados."
        )

    else:

        checkpoint = pd.DataFrame(
            columns=[
                "segment_key",
                "texto_ocr_nuevo",
                "ocr_mode_nuevo",
                "ocr_error_nuevo",
            ]
        )

        done = set()

        print(
            "Sin checkpoint previo. "
            "Inicio desde cero."
        )

    rows = checkpoint.to_dict(
        "records"
    )

    total = len(df)
    procesados_ahora = 0

    # --------------------------------------------------------
    # Procesamiento
    # --------------------------------------------------------

    for grupo, zip_path in zips.items():

        subset = df[
            df["grupo_zip"].eq(grupo)
        ]

        print()
        print("=" * 100)
        print(grupo)
        print("=" * 100)

        with ZipFile(zip_path) as z:

            names = set(
                z.namelist()
            )

            for _, r in subset.iterrows():

                key = r["segment_key"]

                if key in done:
                    continue

                carpeta = str(
                    r["carpeta_video"]
                )

                captura = str(
                    r["Captura"]
                )

                image_path = (
                    f"{carpeta}/{captura}"
                )

                if image_path not in names:

                    rows.append({
                        "segment_key": key,
                        "texto_ocr_nuevo": "",
                        "ocr_mode_nuevo": "missing",
                        "ocr_error_nuevo": (
                            "Image not found: "
                            f"{image_path}"
                        ),
                    })

                else:

                    data = z.read(
                        image_path
                    )

                    text, mode, error = (
                        ocr_image_bytes(
                            data,
                            language=args.language,
                        )
                    )

                    rows.append({
                        "segment_key": key,
                        "texto_ocr_nuevo": text,
                        "ocr_mode_nuevo": mode,
                        "ocr_error_nuevo": error,
                    })

                done.add(key)
                procesados_ahora += 1

                if (
                    procesados_ahora
                    % args.checkpoint_every
                    == 0
                ):

                    pd.DataFrame(
                        rows
                    ).to_csv(
                        args.checkpoint,
                        index=False,
                        encoding="utf-8",
                    )

                    print(
                        f"Procesados: "
                        f"{len(done):,}/{total:,} "
                        f"({len(done)/total*100:.1f}%)"
                    )

    # --------------------------------------------------------
    # Guardar checkpoint final
    # --------------------------------------------------------

    checkpoint_final = (
        pd.DataFrame(rows)
        .drop_duplicates(
            subset="segment_key",
            keep="last",
        )
    )

    checkpoint_final.to_csv(
        args.checkpoint,
        index=False,
        encoding="utf-8",
    )

    # --------------------------------------------------------
    # Unir OCR con maestro
    # --------------------------------------------------------

    resultado = df.merge(
        checkpoint_final,
        on="segment_key",
        how="left",
        validate="one_to_one",
    )

    resultado = resultado.drop(
        columns=["segment_key"]
    )

    # --------------------------------------------------------
    # Controles
    # --------------------------------------------------------

    print()
    print("=" * 100)
    print("CONTROL FINAL")
    print("=" * 100)

    print(
        "Filas:",
        len(resultado),
    )

    print(
        "Videos:",
        resultado["video_id"].nunique(),
    )

    print(
        "OCR correcto:",
        resultado["ocr_error_nuevo"]
        .fillna("")
        .eq("")
        .sum(),
    )

    print(
        "Errores OCR:",
        resultado["ocr_error_nuevo"]
        .fillna("")
        .ne("")
        .sum(),
    )

    print(
        "PSM 6:",
        (
            resultado["ocr_mode_nuevo"]
            == "psm6"
        ).sum(),
    )

    print(
        "PSM 11 fallback:",
        (
            resultado["ocr_mode_nuevo"]
            == "psm11_fallback"
        ).sum(),
    )

    print(
        "Missing:",
        (
            resultado["ocr_mode_nuevo"]
            == "missing"
        ).sum(),
    )

    # --------------------------------------------------------
    # Salida
    # --------------------------------------------------------

    resultado.to_excel(
        args.output,
        index=False,
    )

    print()
    print("=" * 100)
    print("FINALIZADO")
    print("=" * 100)
    print(args.output)


if __name__ == "__main__":
    main()
