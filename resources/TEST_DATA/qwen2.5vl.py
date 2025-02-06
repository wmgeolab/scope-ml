from PIL import Image
import requests
import torch
from torchvision import io
from typing import Dict
from transformers.image_utils import load_images, load_video
from transformers import (
    Qwen2_5_VLForConditionalGeneration,
    AutoTokenizer,
    AutoProcessor,
)
from qwen_vl_utils import process_vision_info

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# PROMPT = "Trans"
IMAGE_PATH = "p10051_doc4__10051-2018-05-18-145457-GEFReviewSheetGEF61/p10051_doc4__10051-2018-05-18-145457-GEFReviewSheetGEF61_4.jpg"
IMAGE_PATH2 = "p10051_doc4__10051-2018-05-18-145457-GEFReviewSheetGEF61/p10051_doc4__10051-2018-05-18-145457-GEFReviewSheetGEF61_2.jpg"
# MODEL = "unsloth/Qwen2.5-VL-7B-Instruct-unsloth-bnb-4bit"
# MODEL = "OpenGVLab/InternVL2_5-8B-MPO-AWQ"
MODEL = "leon-se/Qwen2.5-VL-7B-Instruct-FP8-Dynamic"

PROMPT = """Please convert this image into a JSON format following these specific requirements:

1. Structure:
   - Use a single root object
   - Group related fields into nested objects
   - Use consistent naming conventions
   - Maintain clear parent-child relationships

2. Data Organization:
   - Project metadata should be in a "project_details" object
   - Review sections should be in a "pif_review" object
   - Questions and responses should be paired together in objects

3. Array Handling:
   - Use arrays for multiple related items
   - Each array item should be a complete object with all relevant fields
   - Maintain consistent object structure within arrays

4. Field Names:
   - Use lowercase with underscores
   - Be consistent with naming patterns
   - Preserve original field names where appropriate

Example structure:
{
  "document_title": "...",
  "project_details": {
    "gef_id": "...",
    ...
  },
  "pif_review": {
    "review_sections": {
      "section_name": {
        "questions": [
          {
            "number": "1",
            "text": "...",
            "secretariat_comment": {
              "date": "...",
              "comment": "..."
            }
          }
        ]
      }
    }
  }
}"""


def get_image() -> Image.Image:
    return Image.open(IMAGE_PATH)


def get_model_and_processor():
    min_pixels = 256 * 28 * 28
    max_pixels = 1280 * 28 * 28

    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        MODEL,
        device_map="cuda:0",
        # torch_dtype=torch.bfloat16,
        # attn_implementation="flash_attention_2",
    )
    processor = AutoProcessor.from_pretrained(
        MODEL, min_pixels=min_pixels, max_pixels=max_pixels
    )

    return model, processor


def main():
    model, processor = get_model_and_processor()

    conversation = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                },
                {
                    "type": "text",
                    # "text": "Transcribe the text in the image into a structured json format that retains all of the original information.",
                    "text": PROMPT,
                },
                {
                    "type": "text",
                    "text": "Keep in mind that the tables may have irregular formatting, sometimes having additional fields defined in inner columns or rows. Follow the intended information flow and transcribe the text accordingly.",
                },
                # {
                #     "type": "text",
                #     "text": "There is some information that you keep leaving out from previous versions of the transcription. If you had to guess, what do you think got left out and why?",
                # },
            ],
        }
    ]

    text_prompt = processor.apply_chat_template(
        conversation, add_generation_prompt=True
    )

    image = get_image()

    inputs = processor(
        text=[text_prompt], images=[image], return_tensors="pt", padding=True
    )
    inputs = inputs.to("cuda")

    output_ids = model.generate(**inputs, max_new_tokens=1440)
    generated_ids = [
        output_ids[len(input_ids) :]
        for input_ids, output_ids in zip(inputs.input_ids, output_ids)
    ]

    output_text = processor.batch_decode(
        generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True
    )

    print(f"Model output: \n{output_text[0]}")


if __name__ == "__main__":
    main()
