import base64
import io
from pathlib import Path

import pdf2image
from ml_api.config import settings
from openai import OpenAI


def document_to_base64_images(document_path: Path):
    match document_path.suffix.lower():
        case ".pdf":
            return pdf_to_base64_images(document_path)
        case _:
            raise ValueError(f"Unsupported file type: {document_path.suffix}")


def pdf_to_base64_images(pdf_path: Path):
    page_images = pdf2image.convert_from_path(pdf_path, dpi=settings.PDF_2_PNG_DPI)
    base64_images = []

    for image in page_images:
        tmp_image_file = io.BytesIO()
        image.save(tmp_image_file, "PNG")
        tmp_image_file.seek(0)
        image_bytes = tmp_image_file.read()

        base64_images.append(base64.b64encode(image_bytes).decode("utf-8"))

    return base64_images


def do_ocr_on_image(img_png_base64, client: OpenAI):
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
