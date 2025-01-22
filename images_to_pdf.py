import os
from pathlib import Path
from PIL import Image
import img2pdf
import logging
from typing import List, Tuple
import argparse


class ImageToPdfConverter:
    """Class to handle conversion of images to PDF."""

    SUPPORTED_FORMATS = {".png", ".jpg", ".jpeg", ".tiff", ".bmp"}

    def __init__(self, input_dir: str, output_file: str, sort_by: str = "name"):
        """
        Initialize the converter.

        Args:
            input_dir (str): Directory containing the images
            output_file (str): Path for the output PDF file
            sort_by (str): How to sort images - 'name' or 'date'
        """
        self.input_dir = Path(input_dir)
        self.output_file = Path(output_file)
        self.sort_by = sort_by
        self.setup_logging()

    def setup_logging(self):
        """Configure logging."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(), logging.FileHandler("pdf_creation.log")],
        )

    def get_image_files(self) -> List[Path]:
        """
        Get all image files from the input directory.

        Returns:
            List[Path]: List of paths to image files
        """
        image_files = []
        for ext in self.SUPPORTED_FORMATS:
            image_files.extend(self.input_dir.glob(f"*{ext}"))
            image_files.extend(self.input_dir.glob(f"*{ext.upper()}"))

        if not image_files:
            raise ValueError(f"No image files found in {self.input_dir}")

        # Sort files
        if self.sort_by == "date":
            image_files.sort(key=lambda x: x.stat().st_mtime)
        else:  # sort by name
            image_files.sort()

        logging.info(f"Found {len(image_files)} image files")
        return image_files

    def convert_images(self, image_files: List[Path]) -> List[bytes]:
        """
        Convert images to PDF-compatible format.

        Args:
            image_files (List[Path]): List of image file paths

        Returns:
            List[bytes]: List of converted images in bytes format
        """
        converted_images = []
        for img_path in image_files:
            try:
                # Convert to RGB if necessary (for RGBA images)
                with Image.open(img_path) as img:
                    if img.mode in ("RGBA", "LA"):
                        rgb_img = Image.new("RGB", img.size, (255, 255, 255))
                        rgb_img.paste(img, mask=img.split()[-1])

                        # Save temporarily and read as bytes
                        temp_path = img_path.parent / f"temp_{img_path.name}"
                        rgb_img.save(temp_path, "PNG")
                        with open(temp_path, "rb") as f:
                            converted_images.append(f.read())
                        temp_path.unlink()  # Remove temporary file
                    else:
                        with open(img_path, "rb") as f:
                            converted_images.append(f.read())

                logging.info(f"Successfully converted {img_path.name}")
            except Exception as e:
                logging.error(f"Error converting {img_path.name}: {str(e)}")
                raise

        return converted_images

    def create_pdf(self):
        """Create PDF from images in the input directory."""
        try:
            # Get image files
            image_files = self.get_image_files()

            # Convert images
            converted_images = self.convert_images(image_files)

            # Create PDF
            with open(self.output_file, "wb") as f:
                f.write(img2pdf.convert(converted_images))

            logging.info(f"Successfully created PDF: {self.output_file}")

        except Exception as e:
            logging.error(f"Error creating PDF: {str(e)}")
            raise


def main():
    """Main function to handle command line arguments and run the converter."""
    parser = argparse.ArgumentParser(description="Convert images in a folder to PDF")
    parser.add_argument("input_dir", help="Directory containing the images")
    parser.add_argument("output_file", help="Output PDF file path")
    parser.add_argument(
        "--sort-by",
        choices=["name", "date"],
        default="name",
        help="Sort images by name or modification date (default: name)",
    )

    args = parser.parse_args()

    # Ensure output file has .pdf extension
    output_file = args.output_file
    if not output_file.lower().endswith(".pdf"):
        output_file += ".pdf"

    # Create converter and run
    converter = ImageToPdfConverter(args.input_dir, output_file, args.sort_by)
    converter.create_pdf()


if __name__ == "__main__":
    main()
