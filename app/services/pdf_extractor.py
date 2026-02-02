"""PDF text extraction service."""

import fitz  # PyMuPDF
from pathlib import Path


class PDFExtractor:
    """Extract text content from PDF files."""

    @staticmethod
    def extract_text(file_path: str | Path) -> str:
        """
        Extract text from a PDF file.

        Args:
            file_path: Path to the PDF file.

        Returns:
            Extracted text content.

        Raises:
            ValueError: If the file cannot be read or is not a valid PDF.
        """
        try:
            doc = fitz.open(file_path)
            text_parts = []

            for page_num in range(doc.page_count):
                page = doc[page_num]
                text_parts.append(page.get_text())

            doc.close()
            return "\n".join(text_parts)

        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")

    @staticmethod
    def extract_text_from_bytes(pdf_bytes: bytes) -> str:
        """
        Extract text from PDF bytes.

        Args:
            pdf_bytes: PDF file content as bytes.

        Returns:
            Extracted text content.

        Raises:
            ValueError: If the content is not a valid PDF.
        """
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            text_parts = []

            for page_num in range(doc.page_count):
                page = doc[page_num]
                text_parts.append(page.get_text())

            doc.close()
            return "\n".join(text_parts)

        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
