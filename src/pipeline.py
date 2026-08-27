from __future__ import annotations

import argparse
from pathlib import Path



def print_header():
    print()
    print("=" * 60)
    print("SCREEN RECORDING LEARNING ANALYTICS")
    print("=" * 60)
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Screen Recording Learning Analytics pipeline"
    )

    sub = parser.add_subparsers(
        dest="command",
        required=True
    )

    # ---------------------------------------------------------
    # EXTRACT
    # ---------------------------------------------------------

    extract = sub.add_parser(
        "extract",
        help="Extract screenshots and OCR text from screen recordings"
    )

    extract.add_argument(
        "--input-dir",
        type=Path,
        default=Path("data/videos_raw")
    )

    extract.add_argument(
        "--converted-dir",
        type=Path,
        default=Path("data/videos_converted")
    )

    extract.add_argument(
        "--results-dir",
        type=Path,
        default=Path("data/raw")
    )

    extract.add_argument(
        "--frame-step",
        type=float,
        default=1.0
    )

    extract.add_argument(
        "--ssim-threshold",
        type=float,
        default=0.90
    )

    extract.add_argument(
        "--ocr-language",
        default="spa"
    )

    extract.add_argument(
        "--skip-conversion",
        action="store_true"
    )

    # ---------------------------------------------------------
    # MERGE
    # ---------------------------------------------------------

    merge = sub.add_parser(
        "merge",
        help="Merge per-video Excel files into one dataset"
    )

    merge.add_argument(
        "--input-dir",
        type=Path,
        default=Path("data/raw")
    )

    merge.add_argument(
        "--output",
        type=Path,
        default=Path("data/intermediate/all_videos.xlsx")
    )

    # ---------------------------------------------------------
    # CLASSIFY
    # ---------------------------------------------------------

    classify = sub.add_parser(
        "classify",
        help="Classify screenshots using the YAML site dictionary"
    )

    classify.add_argument(
        "--input",
        type=Path,
        default=Path("data/intermediate/all_videos.xlsx")
    )

    classify.add_argument(
        "--config",
        type=Path,
        default=Path("config/sites.yaml")
    )

    classify.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs")
    )

    # ---------------------------------------------------------
    # RUN COMPLETE PIPELINE
    # ---------------------------------------------------------

    run = sub.add_parser(
        "run",
        help="Run extraction, merge and classification"
    )

    run.add_argument(
        "--videos-dir",
        type=Path,
        default=Path("data/videos_raw")
    )

    run.add_argument(
        "--converted-dir",
        type=Path,
        default=Path("data/videos_converted")
    )

    run.add_argument(
        "--raw-dir",
        type=Path,
        default=Path("data/raw")
    )

    run.add_argument(
        "--merged",
        type=Path,
        default=Path("data/intermediate/all_videos.xlsx")
    )

    run.add_argument(
        "--config",
        type=Path,
        default=Path("config/sites.yaml")
    )

    run.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs")
    )

    run.add_argument(
        "--frame-step",
        type=float,
        default=1.0
    )

    run.add_argument(
        "--ssim-threshold",
        type=float,
        default=0.90
    )

    run.add_argument(
        "--ocr-language",
        default="spa"
    )

    run.add_argument(
        "--skip-conversion",
        action="store_true"
    )

    args = parser.parse_args()

    # ---------------------------------------------------------
    # EXECUTION
    # ---------------------------------------------------------

    if args.command == "extract":

        from .extraction import process_video_directory

        print_header()

        print("[1/1] Extracting screenshots and OCR...")
        print(f"      Input: {args.input_dir}")

        process_video_directory(
            args.input_dir,
            args.converted_dir,
            args.results_dir,
            not args.skip_conversion,
            args.frame_step,
            args.ssim_threshold,
            args.ocr_language
        )

        print("      ✓ Extraction completed.")
        print()

    elif args.command == "merge":

        from .merge_excels import merge_excels

        print_header()

        print("[1/1] Merging video records...")

        merge_excels(
            args.input_dir,
            args.output
        )

        print(f"      ✓ Dataset created: {args.output}")
        print()

    elif args.command == "classify":

        from .classifier import classify_excel

        print_header()

        print("[1/1] Classifying screenshots...")

        classify_excel(
            args.input,
            args.config,
            args.output_dir
        )

        print("      ✓ Classification completed.")
        print(f"      Results: {args.output_dir}")
        print()

    elif args.command == "run":

        from .extraction import process_video_directory
        from .merge_excels import merge_excels
        from .classifier import classify_excel

        print_header()

        print("[1/3] Extracting screenshots and OCR...")
        print(f"      Videos directory: {args.videos_dir}")

        process_video_directory(
            args.videos_dir,
            args.converted_dir,
            args.raw_dir,
            not args.skip_conversion,
            args.frame_step,
            args.ssim_threshold,
            args.ocr_language
        )

        print("      ✓ Extraction completed.")
        print()

        print("[2/3] Merging video records...")

        merge_excels(
            args.raw_dir,
            args.merged
        )

        print(f"      ✓ Dataset created: {args.merged}")
        print()

        print("[3/3] Classifying screenshots...")

        classify_excel(
            args.merged,
            args.config,
            args.output_dir
        )

        print("      ✓ Classification completed.")
        print()

        print("=" * 60)
        print("PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print()
        print(f"Classified records: {args.output_dir / 'classification_results.xlsx'}")
        print(f"Category summary:   {args.output_dir / 'category_summary.xlsx'}")
        print(f"Review file:        {args.output_dir / 'otro_sitio_review.xlsx'}")
        print()


if __name__ == "__main__":
    main()
