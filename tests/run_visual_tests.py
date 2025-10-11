#!/usr/bin/env python3
"""
Helper script to run and debug meteogram visual tests.

This script provides an easy way to run the visual regression tests
and examine the results, including generated images and comparison reports.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Optional

from PIL import Image


def run_visual_tests(
    test_name: Optional[str] = None, verbose: bool = False, show_images: bool = False
) -> int:
    """Run the visual tests and optionally display results."""

    # Change to project root
    project_root = Path(__file__).parent.parent

    # Build pytest command
    cmd = [sys.executable, "-m", "pytest"]

    if test_name:
        cmd.append(f"tests/test_meteogram_visual.py::{test_name}")
    else:
        cmd.append("tests/test_meteogram_visual.py")

    if verbose:
        cmd.extend(["-v", "-s"])

    # Run tests
    print(f"Running command: {' '.join(cmd)}")
    print("-" * 60)

    result = subprocess.run(cmd, cwd=project_root, capture_output=False)

    print("-" * 60)
    print(f"Tests completed with exit code: {result.returncode}")

    # Show results if requested
    if show_images and result.returncode == 0:
        show_test_results()

    return result.returncode


def show_test_results() -> None:
    """Display the test results including generated images and reports."""
    output_dir = Path(__file__).parent / "output"

    if not output_dir.exists():
        print("❌ No test output directory found. Run tests first.")
        return

    print("\n📊 Test Results Summary:")
    print("=" * 50)

    # Show comparison report if it exists
    report_file = output_dir / "comparison_report.txt"
    if report_file.exists():
        print("\n📋 Comparison Report:")
        with open(report_file, "r", encoding="utf-8") as f:
            print(f.read())

    # List generated files
    print("\n📁 Generated Files:")
    for file_path in sorted(output_dir.glob("*.png")):
        size_kb = file_path.stat().st_size / 1024
        print(f"  - {file_path.name} ({size_kb:.1f} KB)")

    # Offer to open images
    if output_dir.glob("*.png"):
        try:
            response = input("\n🖼️  Open generated images? (y/n): ").lower().strip()
            if response in ["y", "yes"]:
                for img_path in sorted(output_dir.glob("*.png")):
                    print(f"Opening {img_path.name}...")
                    if sys.platform == "darwin":  # macOS
                        subprocess.run(["open", str(img_path)])
                    elif sys.platform == "win32":  # Windows
                        subprocess.run(["start", str(img_path)], shell=True)
                    else:  # Linux
                        subprocess.run(["xdg-open", str(img_path)])
        except KeyboardInterrupt:
            print("\nSkipping image display.")


def compare_images() -> None:
    """Compare reference and generated images side by side."""
    output_dir = Path(__file__).parent / "output"
    reference_dir = Path(__file__).parent / "reference_images"

    reference_path = reference_dir / "diagram.png"
    generated_path = output_dir / "generated_meteogram.png"

    if not reference_path.exists():
        print(f"❌ Reference image not found: {reference_path}")
        return

    if not generated_path.exists():
        print(f"❌ Generated image not found: {generated_path}")
        print("Run the visual tests first to generate comparison images.")
        return

    try:
        # Load images
        ref_img = Image.open(reference_path)
        gen_img = Image.open(generated_path)

        print(f"📏 Reference image size: {ref_img.size}")
        print(f"📏 Generated image size: {gen_img.size}")

        # Create side-by-side comparison
        if ref_img.size != gen_img.size:
            print(
                "⚠️  Images have different sizes. Resizing generated to match reference."
            )
            gen_img = gen_img.resize(ref_img.size, Image.Resampling.LANCZOS)

        # Create comparison image
        comparison_width = ref_img.width * 2 + 10  # Small gap between images
        comparison_height = ref_img.height

        comparison_img = Image.new(
            "RGB", (comparison_width, comparison_height), "white"
        )
        comparison_img.paste(ref_img, (0, 0))
        comparison_img.paste(gen_img, (ref_img.width + 10, 0))

        # Save comparison
        comparison_path = output_dir / "side_by_side_comparison.png"
        comparison_img.save(comparison_path)

        print(f"✅ Side-by-side comparison saved to: {comparison_path}")

        # Open comparison
        if sys.platform == "darwin":  # macOS
            subprocess.run(["open", str(comparison_path)])
        elif sys.platform == "win32":  # Windows
            subprocess.run(["start", str(comparison_path)], shell=True)
        else:  # Linux
            subprocess.run(["xdg-open", str(comparison_path)])

    except Exception as e:
        print(f"❌ Error creating comparison: {e}")


def clean_test_outputs() -> None:
    """Clean up test output files."""
    output_dir = Path(__file__).parent / "output"

    if not output_dir.exists():
        print("No output directory to clean.")
        return

    files_removed = 0
    for file_path in output_dir.glob("*"):
        if file_path.is_file():
            file_path.unlink()
            files_removed += 1

    print(f"🧹 Cleaned {files_removed} files from test output directory.")


def main() -> int:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Run and debug meteogram visual tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_visual_tests.py                    # Run all visual tests
  python run_visual_tests.py --verbose          # Run with verbose output
  python run_visual_tests.py --show-images      # Run tests and show results
  python run_visual_tests.py --compare          # Compare reference vs generated
  python run_visual_tests.py --clean            # Clean test outputs
  python run_visual_tests.py --test TestMeteogramVisual::test_meteogram_matches_reference
        """,
    )

    parser.add_argument(
        "--test",
        "-t",
        help="Specific test to run (e.g., TestMeteogramVisual::test_meteogram_matches_reference)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Run tests with verbose output"
    )
    parser.add_argument(
        "--show-images",
        "-s",
        action="store_true",
        help="Show test results and open generated images",
    )
    parser.add_argument(
        "--compare",
        "-c",
        action="store_true",
        help="Create and show side-by-side image comparison",
    )
    parser.add_argument("--clean", action="store_true", help="Clean test output files")

    args = parser.parse_args()

    if args.clean:
        clean_test_outputs()
        return 0

    if args.compare:
        compare_images()
        return 0

    # Run tests
    exit_code = run_visual_tests(
        test_name=args.test, verbose=args.verbose, show_images=args.show_images
    )

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
