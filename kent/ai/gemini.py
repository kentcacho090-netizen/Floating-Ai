"""
Gemini implementation using the official google-genai SDK.
Supports vision (screenshot crops).
"""

from typing import List, Optional
from PIL import Image
from io import BytesIO

from kent.ai.provider import AIProvider
from kent.config import GEMINI_API_KEY, GEMINI_MODEL, SYSTEM_PROMPT


class GeminiProvider(AIProvider):
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is missing. "
                "Copy .env.example to .env and add your key."
            )

        from google import genai
        from google.genai import types

        self._client = genai.Client(api_key=GEMINI_API_KEY)
        self._types = types
        self.model = GEMINI_MODEL

    def chat(
        self,
        messages: List[dict],
        images: Optional[List[Image.Image]] = None,
    ) -> str:
        # Build content parts
        parts = []

        # System instruction is passed separately in newer SDK,
        # but we also put it in the first message for safety.
        contents = []

        for msg in messages:
            role = msg["role"]
            text = msg["content"]
            if role == "system":
                continue  # handled via system_instruction
            # Gemini uses "user" and "model"
            gem_role = "user" if role == "user" else "model"
            contents.append(
                self._types.Content(
                    role=gem_role,
                    parts=[self._types.Part.from_text(text=text)],
                )
            )

        # Attach images to the *last user message*
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
