import logging
import os
import uuid
import asyncio
import io
import time

from PIL import Image
from huggingface_hub import InferenceClient

logger = logging.getLogger(__name__)

HF_TOKEN    = os.getenv("HF_TOKEN", "")
OUTPUTS_DIR = os.getenv("OUTPUTS_DIR", "outputs")


def build_prompt(color: str, coating: str) -> str:
    return (
f"""
Step 1: Identify the car's main painted body panels (metal body only).
Detect and separate:
- factory painted metal body (main car color)
from
- unpainted or non-painted parts such as:
black plastic bumpers, trims, grilles, tires, wheels, glass, lights, badges, mirrors, chrome accents.

Step 2: Determine the base paint color of ONLY the metal body panels.

Step 3: Replace ONLY that detected base body paint color with {color} and apply {coating} finish.

STRICT RULES:
- Do NOT modify black plastic bumpers or any plastic trims.
- Do NOT modify wheels, tires, brakes, glass, lights, mirrors, chrome parts.
- Do NOT recolor shadows, reflections, or environment.
- Keep car geometry, structure, and materials unchanged.

COLOR TRANSFORMATION RULE:
Only the detected factory-painted metal body color must be changed from original color → {color}.

VISUAL REQUIREMENTS:
Maintain:
- realistic lighting
- reflections on car paint only
- original shadows
- original camera angle and perspective

Output must be photorealistic automotive editing quality.
"""
    )


def _run(image_path: str, color: str, coating: str) -> str:
    """Синхронный вызов HuggingFace InferenceClient → fal-ai flux-kontext-dev."""

    prompt = build_prompt(color, coating)
    logger.info(f"HF flux-kontext-dev: {color} + {coating}")

    client = InferenceClient(
        provider="fal-ai",
        api_key=HF_TOKEN,
    )

    with open(image_path, "rb") as f:
        input_image = f.read()

    for attempt in range(3):
        try:
            result: Image.Image = client.image_to_image(
                input_image,
                prompt=prompt,
                model="black-forest-labs/FLUX.1-Kontext-dev",
            )

            # Сохраняем результат
            os.makedirs(OUTPUTS_DIR, exist_ok=True)
            filename = f"{uuid.uuid4().hex}.jpg"
            out_path = os.path.join(OUTPUTS_DIR, filename)

            result.convert("RGB").save(out_path, format="JPEG", quality=95)
            logger.info(f"Сохранено: {out_path}")
            return out_path

        except Exception as e:
            logger.error(f"Попытка {attempt + 1}/3: {e}")
            time.sleep(4)
            if attempt == 2:
                raise RuntimeError(f"HF flux-kontext-dev недоступен: {e}")

    raise RuntimeError("Не удалось получить результат")


async def generate(image_path: str, color: str, coating: str) -> str:
    """Асинхронная обёртка — запускает синхронный вызов в отдельном потоке."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _run, image_path, color, coating)