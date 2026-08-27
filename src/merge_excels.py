from pathlib import Path
import pandas as pd


def merge_excels(input_dir: str | Path, output_file: str | Path) -> pd.DataFrame:
    """Merge per-video Excel files and add `archivo_origen`."""
    input_dir = Path(input_dir)
    output_file = Path(output_file)

    files = sorted(
        path for path in input_dir.rglob("*.xlsx")
        if not path.name.startswith("~$") and path.resolve() != output_file.resolve()
    )
    if not files:
        raise FileNotFoundError(f"No .xlsx files found in {input_dir}")

    frames = []
    for path in files:
        df = pd.read_excel(path)
        df["archivo_origen"] = path.name
        frames.append(df)

    merged = pd.concat(frames, ignore_index=True)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    merged.to_excel(output_file, index=False)
    return merged
