from pathlib import Path
import re
import unicodedata

import pandas as pd


# ============================================================
# CONFIGURACIÓN
# ============================================================

INPUT_FILE = Path(
    "data/intermediate/corpus_100_videos_ocr_new.xlsx"
)

OUTPUT_DIR = Path(
    "outputs/refined_9_categories"
)

OUTPUT_FILE = OUTPUT_DIR / "classification_9_categories.xlsx"
REVIEW_FILE = OUTPUT_DIR / "manual_review.xlsx"
SUMMARY_FILE = OUTPUT_DIR / "category_summary.xlsx"


# ============================================================
# CATEGORÍAS FINALES DEL PAPER METODOLÓGICO
# ============================================================

FINAL_CATEGORIES = [
    "GeoGebra",
    "Google",
    "Google (Mat)",
    "Juegos",
    "Otro sitio",
    "Quinan",
    "Screen Recorder",
    "Wikipedia",
    "YouTube",
]


# ============================================================
# NORMALIZACIÓN
# ============================================================

def normalize_text(value):
    """
    Normaliza texto OCR:
    - convierte a minúsculas
    - elimina tildes
    - compacta espacios
    """

    if pd.isna(value):
        return ""

    text = str(value).lower()

    text = unicodedata.normalize(
        "NFKD",
        text
    )

    text = "".join(
        c for c in text
        if not unicodedata.combining(c)
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def contains_any(text, patterns):
    return any(
        pattern in text
        for pattern in patterns
    )


# ============================================================
# EVIDENCIA FUERTE
# ============================================================

WIKIPEDIA_PATTERNS = [
    "wikipedia.org",
    "es.wikipedia.org",
    "eswikipedia.org",
    "esavikipedia.org",
    "esmikipedia.org",
    "eswvikipedia.org",
    "jeswikipedia.org",
    "wikipedia, la enciclopedia",
    "la enciclopedia libre",
]


YOUTUBE_PATTERNS = [
    "youtube.com/watch",
    "youtube.com/shorts",
    "youtube.com/?",
    "youtube.com/results",
    "youtu.be/",
]


JUEGOS_PATTERNS = [
    "poki.com",
    "friv.com",
    "friv.co",
    "minijuegos.com",
    "crazygames.com",
    "coolmathgames.com",
    "es.y8.com",
    "esy8.com",
    "y8.com",
    "amogus.io",
    "classic.minecraft.net",
]


SCREEN_RECORDER_PATTERNS = [
    "recorder.easeus.com/es/grabador-de-pantalla",
    "recorder.caseus.com/es/grabador-de-pantalla",
    "recorder.esseus.com/es/grabador-de-pantalla",
    "recorder.aseus.com/es/grabador-de-pantalla",
    "grabador de pantalla gratis online",
    "free online screen recorder",
    "online-screen-recorder-brand",
]


GEOGEBRA_PATTERNS = [
    "geogebra.org",
    "geogebra classic",
    "graphing calculator geogebra",
]


QUINAN_PATTERNS = [
    "aulavirtual.quinan.cl",
    "aulavirtualquinan.cl",
    "mod/quiz/attempt.php",
    "mod/quiz/review.php",
    "mod/quiz/summary.php",
]


# ============================================================
# VOCABULARIO MATEMÁTICO PARA GOOGLE (MAT)
#
# No se usa de manera aislada.
# Solo sirve para subdividir registros que ya pertenecían
# históricamente a Google.
# ============================================================

MATH_TERMS = [
    "funcion",
    "funciones",
    "funcion lineal",
    "funcion afin",
    "funcion cuadratica",
    "lineal",
    "lineales",
    "afin",
    "afines",
    "cuadratica",
    "ecuacion",
    "ecuaciones",
    "sistema de ecuaciones",
    "sistemas de ecuaciones",
    "geometria",
    "triangulo",
    "triangulo equilatero",
    "cuadrado",
    "rectangulo",
    "area",
    "perimetro",
    "pendiente",
    "vertice",
    "parabola",
    "grafica",
    "grafico",
    "graficar",
    "dominio",
    "recorrido",
    "variable independiente",
    "variable dependiente",
    "matematica",
    "matematicas",
    "calcular",
    "calculator",
]


def math_evidence(text):
    """
    Devuelve los términos matemáticos detectados.
    """

    hits = []

    for term in MATH_TERMS:
        if term in text:
            hits.append(term)

    return hits


# ============================================================
# CLASIFICACIÓN REFINADA
# ============================================================

def refine_row(row):

    text = row["_normalized_text"]

    historical = normalize_text(
        row.get("palabra_base", "")
    )

    # --------------------------------------------------------
    # 1. Categorías históricas de alta confianza
    # --------------------------------------------------------

    if historical == "quinan":
        return (
            "Quinan",
            "historical_base",
            False,
            ""
        )

    if historical == "geogebra":
        return (
            "GeoGebra",
            "historical_base",
            False,
            ""
        )

    # --------------------------------------------------------
    # 2. GOOGLE -> Google / Google (Mat)
    #
    # Este es exactamente el grupo que el paper indica que
    # fue subdividido según el carácter matemático de la
    # búsqueda.
    # --------------------------------------------------------

    if historical == "google":

        math_hits = math_evidence(text)

        if math_hits:
            return (
                "Google (Mat)",
                "historical_google + math_terms: "
                + "; ".join(math_hits[:10]),
                False,
                ""
            )

        return (
            "Google",
            "historical_google_without_math_evidence",
            False,
            ""
        )

    # --------------------------------------------------------
    # 3. Refinamiento de OTRO SITIO
    #
    # Usamos primero evidencia fuerte de página activa.
    # --------------------------------------------------------

    if historical == "otro sitio":

        # Wikipedia
        if contains_any(
            text,
            WIKIPEDIA_PATTERNS
        ):
            return (
                "Wikipedia",
                "strong_wikipedia_evidence",
                False,
                ""
            )

        # YouTube
        if contains_any(
            text,
            YOUTUBE_PATTERNS
        ):
            return (
                "YouTube",
                "strong_youtube_evidence",
                False,
                ""
            )

        # Juegos
        if contains_any(
            text,
            JUEGOS_PATTERNS
        ):
            return (
                "Juegos",
                "strong_game_domain",
                False,
                ""
            )

        # GeoGebra recuperado por nuevo OCR
        if contains_any(
            text,
            GEOGEBRA_PATTERNS
        ):
            return (
                "GeoGebra",
                "strong_geogebra_evidence",
                False,
                ""
            )

        # Quinan recuperado por nuevo OCR.
        #
        # Lo dejamos marcado para revisión porque Quinan
        # puede aparecer en pestañas mientras otro sitio
        # permanece activo.
        if contains_any(
            text,
            QUINAN_PATTERNS
        ):
            return (
                "Otro sitio",
                "possible_quinan",
                True,
                "Quinan detectado en OCR nuevo dentro de "
                "un segmento históricamente Otro sitio"
            )

        # Screen Recorder:
        #
        # Solo se asigna si encontramos evidencia fuerte
        # de que la página activa es el grabador.
        if contains_any(
            text,
            SCREEN_RECORDER_PATTERNS
        ):
            return (
                "Screen Recorder",
                "strong_screen_recorder_page",
                False,
                ""
            )

        return (
            "Otro sitio",
            "residual",
            True,
            "Sin evidencia fuerte para las categorías refinadas"
        )

    # --------------------------------------------------------
    # 4. ChatGPT histórico
    #
    # No pertenece a las nueve categorías finales del
    # primer paper metodológico.
    #
    # No inventamos una reasignación automática:
    # queda como Otro sitio y pasa a revisión.
    # --------------------------------------------------------

    if historical == "chatgpt":
        return (
            "Otro sitio",
            "historical_chatgpt",
            True,
            "ChatGPT estaba en la clasificación inicial, "
            "pero no pertenece al esquema final de 9 categorías"
        )

    # --------------------------------------------------------
    # 5. Cualquier caso inesperado
    # --------------------------------------------------------

    return (
        "Otro sitio",
        "unrecognized_historical_label",
        True,
        f"Etiqueta histórica no reconocida: {historical}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 100)
    print("REFINAMIENTO A 9 CATEGORÍAS")
    print("=" * 100)

    print("\nArchivo de entrada:")
    print(INPUT_FILE)

    df = pd.read_excel(
        INPUT_FILE
    )

    print("\nFilas:", len(df))
    print(
        "Videos:",
        df["video_id"].nunique()
    )

    # --------------------------------------------------------
    # Validaciones mínimas
    # --------------------------------------------------------

    required = [
        "video_id",
        "palabra_base",
        "texto_ocr_nuevo",
    ]

    missing = [
        c for c in required
        if c not in df.columns
    ]

    if missing:
        raise ValueError(
            "Faltan columnas requeridas: "
            + ", ".join(missing)
        )

    # --------------------------------------------------------
    # Normalización
    # --------------------------------------------------------

    df["_normalized_text"] = (
        df["texto_ocr_nuevo"]
        .apply(normalize_text)
    )

    # --------------------------------------------------------
    # Refinamiento
    # --------------------------------------------------------

    results = df.apply(
        refine_row,
        axis=1,
        result_type="expand"
    )

    results.columns = [
        "categoria_refinada_auto",
        "evidencia_refinamiento",
        "requiere_revision_manual",
        "motivo_revision",
    ]

    df = pd.concat(
        [
            df,
            results
        ],
        axis=1
    )

    # --------------------------------------------------------
    # Verificar categorías
    # --------------------------------------------------------

    unexpected = sorted(
        set(
            df["categoria_refinada_auto"]
            .dropna()
            .unique()
        )
        - set(FINAL_CATEGORIES)
    )

    if unexpected:
        raise ValueError(
            "Se generaron categorías inesperadas: "
            + str(unexpected)
        )

    # --------------------------------------------------------
    # RESUMEN
    # --------------------------------------------------------

    summary = (
        df["categoria_refinada_auto"]
        .value_counts()
        .rename_axis("categoria")
        .reset_index(name="n")
    )

    summary["porcentaje"] = (
        summary["n"]
        / len(df)
        * 100
    ).round(2)

    summary["tiempo_s"] = summary[
        "categoria"
    ].map(
        df.groupby(
            "categoria_refinada_auto"
        )["Tiempo en página (s)"]
        .sum()
        if "Tiempo en página (s)" in df.columns
        else {}
    )

    if "tiempo_s" in summary.columns:
        summary["tiempo_h"] = (
            summary["tiempo_s"]
            / 3600
        ).round(4)

    # --------------------------------------------------------
    # REVISIÓN MANUAL
    # --------------------------------------------------------

    review = df[
        df["requiere_revision_manual"]
    ].copy()

    # --------------------------------------------------------
    # LIMPIAR COLUMNA AUXILIAR
    # --------------------------------------------------------

    df.drop(
        columns=["_normalized_text"],
        inplace=True
    )

    review.drop(
        columns=["_normalized_text"],
        inplace=True,
        errors="ignore"
    )

    # --------------------------------------------------------
    # EXPORTAR
    # --------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_excel(
        OUTPUT_FILE,
        index=False
    )

    review.to_excel(
        REVIEW_FILE,
        index=False
    )

    summary.to_excel(
        SUMMARY_FILE,
        index=False
    )

    # --------------------------------------------------------
    # CONTROL FINAL
    # --------------------------------------------------------

    print("\n" + "=" * 100)
    print("DISTRIBUCIÓN AUTOMÁTICA")
    print("=" * 100)

    print(
        summary.to_string(
            index=False
        )
    )

    print("\n" + "=" * 100)
    print("REVISIÓN MANUAL")
    print("=" * 100)

    print(
        "Segmentos para revisión:",
        len(review)
    )

    print(
        "Porcentaje:",
        f"{len(review)/len(df)*100:.2f}%"
    )

    print(
        "Videos implicados:",
        review["video_id"].nunique()
        if len(review)
        else 0
    )

    if len(review):

        print("\nMotivos:")

        print(
            review["motivo_revision"]
            .value_counts()
            .to_string()
        )

    print("\n" + "=" * 100)
    print("CONTROL")
    print("=" * 100)

    print(
        "¿18.829 filas?:",
        len(df) == 18829
    )

    print(
        "¿100 videos?:",
        df["video_id"].nunique() == 100
    )

    print(
        "Categorías generadas:",
        sorted(
            df["categoria_refinada_auto"]
            .unique()
        )
    )

    print("\n" + "=" * 100)
    print("ARCHIVOS GENERADOS")
    print("=" * 100)

    print(OUTPUT_FILE)
    print(REVIEW_FILE)
    print(SUMMARY_FILE)


if __name__ == "__main__":
    main()
