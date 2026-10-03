"""
Gemini cloud engine — optional powerful fallback.
Kept fully compatible with the previous GeminiProvider.
"""

from typing import List, Optional
from PIL import Image
from io import BytesIO

from kent.ai.engine import Engine
from kent.config import GEMINI_API_KEY, GEMINI_MODEL, SYSTEM_PROMPT


class GeminiEngine(Engine):
    name = "gemini"

    def __init__(self):
        self._client = None
        self._types = None
        self.model = GEMINI_MODEL

        if GEMINI_API_KEY:
            try:
                from google import genai
                from google.genai import types
                self._client = genai.Client(api_key=GEMINI_API_KEY)
                self._types = types
            except Exception:
                self._client = None

    def is_available(self) -> bool:
        return bool(self._client and GEMINI_API_KEY)

    def supports_vision(self) -> bool:
        return True

    def chat(
        self,
        messages: List[dict],
        images: Optional[List[Image.Image]] = None,
    ) -> str:
        if not self.is_available():
            raise RuntimeError("Gemini is not configured. Add GEMINI_API_KEY to .env")

        contents = []
        for msg in messages:
            role = msg["role"]
            text = msg["content"]
            if role == "system":
                continue
            gem_role = "user" if role == "user" else "model"
            contents.append(
                self._types.Content(
                    role=gem_role,
                    parts=[self._types.Part.from_text(text=text)],
                )
            )

        if images and contents:
            last = contents[-1]
            new_parts = list(last.parts)
            for img in images:
                buf = BytesIO()
                img.save(buf, format="JPEG", quality=85)
                new_parts.append(
                    self._types.Part.from_bytes(
                        data=buf.getvalue(),
                        mime_type="image/jpeg",
                    )
                )
            contents[-1] = self._types.Content(role=last.role, parts=new_parts)

        try:
            response = self._client.models.generate_content(
                model=self.model,
                contents=contents,
                config=self._types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.55,
                    max_output_tokens=1024,
                ),
            )
            return (response.text or "").strip()
        except Exception as e:
            raise RuntimeError(f"Gemini error: {e}") from e
