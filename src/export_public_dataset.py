"""Historical first-version export utility.

This script is retained for provenance. It exports a historical intermediate
workbook and does not generate the authoritative final public dataset. Use
``src.reproduce_final_classification`` for final-label reproduction and
``src.compute_digital_activity_indicators`` for manuscript indicators.
"""

from pathlib import Path
import re
import pandas as pd


# ============================================================
# CONFIGURACIÓN
# ============================================================

INPUT_FILE = Path("data/intermediate/corpus_100_videos.xlsx")
OUTPUT_DIR = Path("data/processed")
OUTPUT_FILE = OUTPUT_DIR / "corpus_100_videos_public.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# CARGA
# ============================================================

df = pd.read_excel(INPUT_FILE)

print("=" * 90)
print("EXPORTACIÓN DEL DATASET PÚBLICO")
print("=" * 90)

print(f"\nArchivo maestro: {INPUT_FILE}")
print(f"Filas:           {len(df)}")
print(f"Videos:          {df['video_id'].nunique()}")


# ============================================================
# 1. CREAR IDENTIFICADORES PÚBLICOS DE VIDEO
# ============================================================

videos_originales = list(df["video_id"].drop_duplicates())

mapa_videos = {
    video: f"V{i:03d}"
    for i, video in enumerate(videos_originales, start=1)
}

df["video_id_public"] = df["video_id"].map(mapa_videos)


# ============================================================
# 2. CREAR IDENTIFICADOR DE SEGMENTO
# ============================================================

df["segment_id"] = (
    df.groupby("video_id_public").cumcount() + 1
)

df["segment_id"] = df.apply(
    lambda x: f"{x['video_id_public']}_S{int(x['segment_id']):04d}",
    axis=1
)


# ============================================================
# 3. CREAR IDENTIFICADOR ANÓNIMO DE GRUPO
# ============================================================

grupos = list(df["grupo_zip"].drop_duplicates())

mapa_grupos = {
    grupo: f"G{i:02d}"
    for i, grupo in enumerate(grupos, start=1)
}

df["group_id"] = df["grupo_zip"].map(mapa_grupos)


# ============================================================
# 4. NORMALIZAR VARIABLES TEMPORALES
# ============================================================

df["start_time_s"] = pd.to_numeric(
    df["Segundo entrada"],
    errors="coerce"
)

df["end_time_s"] = pd.to_numeric(
    df["Segundo salida"],
    errors="coerce"
)

df["duration_s"] = pd.to_numeric(
    df["Tiempo en página (s)"],
    errors="coerce"
)


# ============================================================
# 5. NO PUBLICAR OCR EN ESTA PRIMERA VERSIÓN
# ============================================================
#
# texto_extraido puede contener nombres, correos electrónicos,
# cuentas, búsquedas u otra información identificable.
#
# Por tanto, NO se exporta automáticamente.
# ============================================================


# ============================================================
# 6. VARIABLES PÚBLICAS
# ============================================================

columnas_publicas = [
    "video_id_public",
    "group_id",
    "segment_id",
    "start_time_s",
    "end_time_s",
    "duration_s",
]

# Añadimos clasificación solamente si existe en el maestro.
for columna in [
    "palabra_detectada",
    "palabra_base",
]:
    if columna in df.columns:
        columnas_publicas.append(columna)


public_df = df[columnas_publicas].copy()


# ============================================================
# 7. RENOMBRAR VARIABLES DE CLASIFICACIÓN
# ============================================================

rename = {
    "video_id_public": "video_id",
    "palabra_detectada": "detected_category",
    "palabra_base": "category",
}

public_df = public_df.rename(columns=rename)


# ============================================================
# 8. CONTROL DE POSIBLES DATOS IDENTIFICABLES
# ============================================================

columnas_prohibidas = {
    "carpeta_video",
    "excel_origen",
    "texto_extraido",
    "Captura",
    "archivo",
    "grupo_zip",
}

filtradas = columnas_prohibidas.intersection(public_df.columns)

if filtradas:
    raise RuntimeError(
        f"ERROR: variables privadas presentes en el dataset público: {filtradas}"
    )


# ============================================================
# 9. COMPROBACIONES DE INTEGRIDAD
# ============================================================

assert len(public_df) == len(df), (
    "El número de segmentos cambió durante la anonimización."
)

assert public_df["video_id"].nunique() == df["video_id"].nunique(), (
    "El número de videos cambió durante la anonimización."
)

assert public_df["segment_id"].is_unique, (
    "Los identificadores de segmento no son únicos."
)


# ============================================================
# 10. EXPORTAR
# ============================================================

public_df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8"
)


# ============================================================
# REPORTE
# ============================================================

print("\n" + "=" * 90)
print("DATASET PÚBLICO GENERADO")
print("=" * 90)

print(f"\nVideos:       {public_df['video_id'].nunique()}")
print(f"Segmentos:    {len(public_df)}")
print(f"Columnas:     {len(public_df.columns)}")

print("\nColumnas públicas:")

for i, columna in enumerate(public_df.columns, start=1):
    print(f"{i:02d}. {columna}")

print("\n" + "=" * 90)
print("VARIABLES PRIVADAS EXCLUIDAS")
print("=" * 90)

print("""
- carpeta_video
- excel_origen
- texto_extraido
- Captura
- archivo
- grupo_zip
""")

print("=" * 90)
print("ARCHIVO")
print("=" * 90)

print(OUTPUT_FILE)
print(f"Tamaño: {OUTPUT_FILE.stat().st_size / 1024 / 1024:.2f} MB")
