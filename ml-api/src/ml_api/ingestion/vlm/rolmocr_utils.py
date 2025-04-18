import base64
import io
from pathlib import Path

import pdf2image
from ml_api.config import settings
from openai import OpenAI


def document_to_base64_images(document_path: Path):
    """
    Given a document path, convert it to a list of base64 encoded strings, each representing a page in the document.

    Currently, only PDF documents are supported.

    Args:
        document_path (Path): The path to the document.

    Returns:
        List[str]: A list of base64 encoded strings, each representing a page in the document.

    Raises:
        ValueError: If the document type is not supported.
    """
    match document_path.suffix.lower():
        case ".pdf":
            return pdf_to_base64_images(document_path)
        case _:
            raise ValueError(f"Unsupported file type: {document_path.suffix}")


def pdf_to_base64_images(pdf_path: Path) -> list[str]:
    """
    Given a PDF path, convert it to a list of base64 encoded strings, each representing a page in the document.

    Args:
        pdf_path (Path): The path to the PDF document.

    Returns:
        List[str]: A list of base64 encoded strings, each representing a page in the document.
    """
    page_images = pdf2image.convert_from_path(pdf_path, dpi=settings.PDF_2_PNG_DPI)
    base64_images: list[str] = []

    for image in page_images:
        tmp_image_file = io.BytesIO()
        image.save(tmp_image_file, "PNG")
        tmp_image_file.seek(0)
        image_bytes = tmp_image_file.read()

        base64_images.append(base64.b64encode(image_bytes).decode("utf-8"))

    return base64_images


def do_ocr_on_image(img_png_base64: str, client: OpenAI) -> str | None:
    """
    Given an image as a base64 encoded string, performs OCR on the image using the VLLM model.

    Args:
        img_png_base64 (str): The base64 encoded PNG image.
        client (OpenAI): The OpenAI client used to make the request.

    Returns:
        str | None: The plain text representation of the document, or None if the request failed.
    """
    response = client.chat.completions.create(
        model=settings.VLLM_VLM_MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{img_png_base64}"},
                    },
                    {
                        "type": "text",
                        "text": "Return the plain text representation of this document as if you were reading it naturally.\n",
                    },
                ],
            }
        ],
    )

    return response.choices[0].message.content


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
