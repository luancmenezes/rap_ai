#!/usr/bin/env python
"""Simple CLI entry point for running the RAP pipeline."""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Download, transcribe, analyze and generate HTML from a YouTube URL."
    )
    parser.add_argument(
        "url",
        help="YouTube video URL to process",
    )
    args = parser.parse_args()

    # Import lazily so we only touch project modules after argument parsing succeeds.
    from src.pipeline import Pipeline
    """Mantém compatibilidade com a antiga API baseada em função."""
    path = "/Users/luanmenezes/Documents/personal_projects/rap_llm/data/transcripts/BARRETO_VS_JAPA_-__FINAL__-_DUELO_DE_MCS_NACIONAL_2025__GRANDE_FINAL__-_23112025.txt"

    Pipeline(url=args.url, transcript_path=path)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)

