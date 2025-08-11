#!/usr/bin/env python3
import openai
import requests

def openai_api(api_key, content, model="gpt-3.5-turbo", strong_prompts="", proprietary="", timeout=180, temperature=0.1, top_p=0.1, prev_original_text=None, prev_translated_text=None):
    if not api_key:
        raise ValueError("OpenAI API key is required.")

    client = openai.OpenAI(api_key=api_key)

    messages = [
        {
            "role": "system",
            "content": f"""You are a Japanese light novel translator. Your task is to translate the provided Japanese text into fluent, natural-sounding Traditional Chinese, as if it were published by a Taiwanese publisher.

Key instructions:
-   **Style and Tone:** Maintain the original author's writing style and tone.
-   **Formatting:** Preserve the original formatting, including line breaks and spacing.
-   **Character Voice:** Faithfully translate character-specific verbal tics or unique speech patterns (e.g.,尾語).
-   **Terminology:** Use the provided list of proprietary nouns and terms consistently.
-   **Accuracy:** Accurately convey the meaning of idioms, metaphors, proverbs, and descriptive language. For Japanese kanji, interpret their meaning from a Chinese perspective within the given context.
-   **Fluency:** Ensure the translation is grammatically correct and natural in Traditional Chinese. Adjust sentence structure where necessary to improve readability without altering the original meaning.
-   **Completeness:** Provide a complete translation of the text. Do not omit any part of the original text.
-   **Output Language:** The final output must be in Traditional Chinese.
{strong_prompts}
"""
        }
    ]

    if proprietary:
        messages.append({"role": "system", "content": f"Here is a list of proprietary nouns and their translations. Please use them consistently:\n{proprietary}"})

    if prev_original_text and prev_translated_text:
        messages.append({"role": "user", "content": f"Here is the previous chapter for context:\n\n**Original Japanese:**\n{prev_original_text}\n\n**Chinese Translation:**\n{prev_translated_text}"})

    messages.append({"role": "user", "content": f"Please translate the following Japanese light novel text into Traditional Chinese:\n\n{content}"})

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            timeout=timeout,
        )
        return response.choices[0].message.content
    except Exception as e:
        return {'error': str(e)}


def memo_openai_api(api_key, content, model="gpt-3.5-turbo", timeout=60):
    if not api_key:
        raise ValueError("OpenAI API key is required.")

    client = openai.OpenAI(api_key=api_key)

    messages = [
        {
            "role": "system",
            "content": """You are an expert in identifying and translating special terms from Japanese text. Your task is to extract all names, special nouns, place names, skill names, and katakana words from the provided Japanese text and translate them into Traditional Chinese.

Follow these rules:
1.  **Format:** Present the results in a Markdown table with two columns: "日文原文" (Original Japanese) and "繁體中文" (Traditional Chinese).
2.  **Content:** Only list the identified special terms. Do not include common nouns or full sentences.
3.  **Accuracy:** Ensure the translations are accurate and in Traditional Chinese.
"""
        },
        {
            "role": "user",
            "content": f"""Please extract and translate the special terms from the following Japanese text:

{content}
"""
        }
    ]

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            timeout=timeout,
        )
        return response.choices[0].message.content
    except Exception as e:
        return {'error': str(e)}

# Wrapper for backwards compatibility
def api(API_KEY, content="", is_translated="", proprietary='', timeout=180, temperature=0.1, topK=1, topP=0.1):
    # This is a temporary wrapper. It will be replaced with direct calls to openai_api.
    # The topK parameter is not used in the OpenAI API, so it will be ignored.
    return openai_api(
        api_key=API_KEY,
        content=content,
        proprietary=proprietary,
        timeout=timeout,
        temperature=temperature,
        top_p=topP,
        prev_original_text=None, # No context in the old `api` function
        prev_translated_text=is_translated
    )

def memo_api(API_KEY, content, timeout=60):
    # This is a temporary wrapper. It will be replaced with direct calls to memo_openai_api.
    return memo_openai_api(
        api_key=API_KEY,
        content=content,
        timeout=timeout
    )
