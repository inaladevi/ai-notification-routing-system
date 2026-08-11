import json
import os
import re
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

from prompts import SYSTEM_PROMPT, build_user_prompt

class Router:
    def __init__(self, model_name="gemini-3.1-flash-lite"):
        print(">>> USING MODEL:", model_name)
        load_dotenv()

        print("Current working directory:", os.getcwd())
        print("ENV loaded:", os.getenv("GEMINI_API_KEY") is not None)


        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")

        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.max_retries = 8
        self.request_interval_seconds = 6.0
        self.retry_base_delay_seconds = 60.0

    def route(self, context):
        system_prompt = SYSTEM_PROMPT
        user_prompt = build_user_prompt(context)

        start = time.time()

        print(f"Prompt length: {len(user_prompt)} characters")

        last_error = None
        for attempt in range(self.max_retries):
            if attempt > 0:
                delay = self._get_retry_delay_seconds(last_error, attempt)
                print(f"Quota hit, retrying in {delay:.1f}s ({attempt + 1}/{self.max_retries})")
                time.sleep(delay)
            else:
                time.sleep(self.request_interval_seconds)

            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.1,
                        response_mime_type="application/json",
                        max_output_tokens=1024,
                    ),
                )
                break
            except Exception as exc:
                last_error = exc
                if not self._is_quota_error(exc):
                    raise
                if attempt == self.max_retries - 1:
                    raise
                continue

        print(f"Gemini call took {time.time() - start:.2f} seconds")

        if response.text:
            try:
                return json.loads(response.text)
            except json.JSONDecodeError:
                return self._extract_json(response.text)

        print("RAW RESPONSE:")
        print(repr(response.text))

        raise ValueError("Gemini returned no usable JSON.") from last_error

    def _is_quota_error(self, exc):
        code = getattr(exc, "code", None)
        status_code = getattr(exc, "status_code", None)
        if code == 429 or status_code == 429:
            return True

        text = str(exc).lower()
        return "resource_exhausted" in text or "quota exceeded" in text or "retry in" in text

    def _get_retry_delay_seconds(self, exc, attempt):
        if exc is None:
            return self.retry_base_delay_seconds * (attempt + 1)

        match = re.search(r"retry in\s+([0-9.]+)s", str(exc), re.IGNORECASE)
        if match:
            return max(float(match.group(1)), 1.0)

        return self.retry_base_delay_seconds * (attempt + 1)

    def _extract_json(self, text):
        if not text:
            raise ValueError("Empty response from Gemini.")

        text = text.strip()

        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1:
            print("RAW RESPONSE:")
            print(text)
            raise ValueError("No JSON object found.")

        return json.loads(text[start:end + 1])