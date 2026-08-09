"""Output handling for transcription results."""

from pathlib import Path


class OutputHandler:
    """Handle transcription output formatting and saving."""

    @staticmethod
    def format_transcription(transcription: dict, include_timestamps: bool = True) -> str:
        """Format transcription for output.

        Args:
            transcription: Transcription dictionary with text and optional timestamps
            include_timestamps: Whether to include timestamp information

        Returns:
            Formatted transcription string
        """
        lines = []

        # Add main transcription text
        lines.append("Transcription:")
        lines.append("=" * 50)
        lines.append(transcription["text"])
        lines.append("")

        # Add timestamps if requested and available
        if include_timestamps and "timestamps" in transcription:
            lines.append("Timestamps:")
            lines.append("-" * 50)

            # Add word-level timestamps
            if "word" in transcription["timestamps"]:
                lines.append("\nWord-level:")
                for item in transcription["timestamps"]["word"]:
                    lines.append(f"  {item['start']:.2f}s - {item['end']:.2f}s: {item['word']}")

            # Add segment-level timestamps
            if "segment" in transcription["timestamps"]:
                lines.append("\nSegment-level:")
                for item in transcription["timestamps"]["segment"]:
                    lines.append(f"  {item['start']:.2f}s - {item['end']:.2f}s: {item['segment']}")

        return "\n".join(lines)

    def save_transcription(
        self,
        transcription: dict,
        output_path: Path,
        include_timestamps: bool = True,
    ) -> None:
        """Save transcription to file.

        Args:
            transcription: Transcription dictionary
            output_path: Path to output file
            include_timestamps: Whether to include timestamps
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        formatted = self.format_transcription(transcription, include_timestamps)
        output_path.write_text(formatted)

    @staticmethod
    def generate_output_filename(input_path: Path, output_dir: Path) -> Path:
        """Generate output filename based on input.

        Args:
            input_path: Input audio file path
            output_dir: Output directory

        Returns:
            Generated output file path
        """
        stem = input_path.stem
        return output_dir / f"{stem}.txt"
