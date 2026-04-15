"""
AI Service — handles research, outline, and content generation
using OpenAI, Gemini, or Anthropic depending on the configured provider.
"""

import json
from bson import ObjectId
from app.database import ai_providers_col


async def _get_provider(provider_id: str = None):
    """Get an AI provider by ID, or the first available if no ID provided."""
    if provider_id:
        doc = await ai_providers_col.find_one({"_id": ObjectId(provider_id)})
        if not doc:
            raise Exception(f"AI provider not found: {provider_id}")
        return doc
    doc = await ai_providers_col.find_one()
    if not doc:
        raise Exception("No AI provider configured. Please add one in Settings.")
    return doc


async def _call_openai(
    api_key: str,
    prompt: str,
    system_prompt: str = "",
    base_url: str = None,
    model_name: str = "gpt-4o",
) -> tuple[str, int]:
    """Call OpenAI or OpenAI-compatible API."""
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=api_key, base_url=base_url or None)
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    response = await client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.7,
    )
    total_tokens = response.usage.total_tokens if response.usage else 0
    return response.choices[0].message.content, total_tokens


async def _call_gemini(
    api_key: str, prompt: str, system_prompt: str = ""
) -> tuple[str, int]:
    """Call Gemini API."""
    from google import genai

    client = genai.Client(api_key=api_key)
    full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=full_prompt,
    )
    tokens = 0
    if response.usage_metadata:
        tokens = (response.usage_metadata.prompt_token_count or 0) + (
            response.usage_metadata.candidates_token_count or 0
        )
    return response.text, tokens


async def _call_anthropic(
    api_key: str, prompt: str, system_prompt: str = ""
) -> tuple[str, int]:
    """Call Anthropic API."""
    from anthropic import AsyncAnthropic

    client = AsyncAnthropic(api_key=api_key)
    kwargs = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 8192,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system_prompt:
        kwargs["system"] = system_prompt
    response = await client.messages.create(**kwargs)
    total_tokens = response.usage.input_tokens + response.usage.output_tokens
    return response.content[0].text, total_tokens


async def verify_api_key(provider_type: str, api_key: str, api_url: str = "") -> dict:
    """Verify an API key by making a minimal test call.
    Returns {"ok": True} or {"ok": False, "error": "reason"}.
    """
    test_prompt = "Reply with exactly: OK"
    try:
        if provider_type == "openai":
            text, _ = await _call_openai(api_key, test_prompt)
        elif provider_type == "gemini":
            text, _ = await _call_gemini(api_key, test_prompt)
        elif provider_type == "anthropic":
            text, _ = await _call_anthropic(api_key, test_prompt)
        elif provider_type == "openai_compatible":
            text, _ = await _call_openai(api_key, test_prompt, base_url=api_url)
        else:
            return {"ok": False, "error": f"Unknown provider type: {provider_type}"}

        if not text or not text.strip():
            return {"ok": False, "error": "Received empty response from AI provider."}
        return {"ok": True}

    except Exception as e:
        error_msg = str(e).lower()

        if provider_type == "openai":
            if "incorrect_api_key" in error_msg or "invalid_api_key" in error_msg:
                return {
                    "ok": False,
                    "error": "Invalid OpenAI API key. Check your key and try again.",
                }
            elif "insufficient_quota" in error_msg:
                return {
                    "ok": False,
                    "error": "OpenAI API key is valid but account has insufficient quota.",
                }
            elif "rate_limit" in error_msg:
                return {
                    "ok": False,
                    "error": "OpenAI rate limit reached. Try again in a moment.",
                }
        elif provider_type == "gemini":
            if "api_key_not_valid" in error_msg or "api key not valid" in error_msg:
                return {
                    "ok": False,
                    "error": "Invalid Gemini API key. Check your key and try again.",
                }
            elif "quota" in error_msg:
                return {
                    "ok": False,
                    "error": "Gemini API key is valid but account has exceeded quota.",
                }
        elif provider_type == "anthropic":
            if "invalid_api_key" in error_msg or "authentication_error" in error_msg:
                return {
                    "ok": False,
                    "error": "Invalid Anthropic API key. Check your key and try again.",
                }
            elif "overloaded" in error_msg:
                return {
                    "ok": False,
                    "error": "Anthropic API is currently overloaded. Try again in a moment.",
                }
        elif provider_type == "openai_compatible":
            if (
                "invalid_api_key" in error_msg
                or "incorrect_api_key" in error_msg
                or "authentication_error" in error_msg
            ):
                return {
                    "ok": False,
                    "error": "Invalid API key for the configured endpoint.",
                }

        return {"ok": False, "error": f"Verification failed: {str(e)}"}


async def _call_ai(
    prompt: str,
    system_prompt: str = "",
    provider_id: str = None,
    model_name: str = None,
) -> tuple[str, int]:
    """Route to the appropriate AI provider."""
    provider = await _get_provider(provider_id)
    provider_type = provider["provider_type"]
    api_key = provider["api_key"]

    if provider_type == "openai":
        return await _call_openai(
            api_key, prompt, system_prompt, model_name=model_name or "gpt-4o"
        )
    elif provider_type == "gemini":
        return await _call_gemini(api_key, prompt, system_prompt)
    elif provider_type == "anthropic":
        return await _call_anthropic(api_key, prompt, system_prompt)
    elif provider_type == "openai_compatible":
        api_url = provider.get("api_url", "")
        return await _call_openai(
            api_key,
            prompt,
            system_prompt,
            base_url=api_url,
            model_name=model_name or provider.get("model_name", "gpt-4o"),
        )
    else:
        raise Exception(f"Unknown provider type: {provider_type}")


async def research_topic(
    topic: str,
    additional_requests: str = "",
    provider_id: str = None,
    model_name: str = None,
    language: str = "vietnamese",
) -> tuple[dict, int]:
    """Research a topic: audience, keywords, key points to mention."""
    system_prompt = (
        "You are an expert SEO content researcher. Respond only in valid JSON."
    )
    prompt = f"""Research the following topic for a WordPress blog post.

Topic: {topic}
{f"Additional requests: {additional_requests}" if additional_requests else ""}

Provide your research as JSON with these keys:
{{
    "target_audience": "description of the target audience",
    "keywords": ["list", "of", "seo", "keywords"],
    "key_points": ["point 1 to cover", "point 2 to cover", ...],
    "questions_to_answer": ["question 1", "question 2", ...],
    "competitors_angle": "what competitors typically cover on this topic"
}}"""

    text, total_tokens = await _call_ai(prompt, system_prompt, provider_id, model_name)
    # Parse JSON from response
    try:
        # Try to extract JSON from markdown code block if present
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        data = json.loads(text.strip())
    except json.JSONDecodeError:
        data = {"raw_research": text}
    return data, total_tokens


async def generate_outline(
    topic: str,
    research_data: dict,
    additional_requests: str = "",
    provider_id: str = None,
    model_name: str = None,
    target_section_count: int = None,
    language: str = "vietnamese",
) -> tuple[dict, int]:
    """Generate a post outline: SEO title, meta description, intro, sections."""
    system_prompt = (
        "You are an expert SEO content strategist. Respond only in valid JSON."
    )
    section_count_hint = (
        f"Create exactly {target_section_count} sections"
        if target_section_count
        else "Create 5-8 sections"
    )
    prompt = f"""Create a detailed blog post outline based on:

Topic: {topic}
Research data: {json.dumps(research_data)}
{f"Additional requests: {additional_requests}" if additional_requests else ""}

Create an outline as JSON:
{{
    "title": "SEO optimized title for the post",
    "meta_description": "compelling meta description under 160 chars",
    "introduction": {{
        "hook": "an engaging opening hook",
        "problem": "the problem the reader faces",
        "promise": "what the reader will learn/gain"
    }},
    "sections": [
        {{
            "title": "Section 1 Title",
            "key_points": ["point to cover", "another point"]
        }},
        ...more sections ({section_count_hint} for a comprehensive post)
    ]
}}"""

    text, total_tokens = await _call_ai(prompt, system_prompt, provider_id, model_name)
    try:
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        data = json.loads(text.strip())
    except json.JSONDecodeError:
        data = {"raw_outline": text}
    return data, total_tokens


async def generate_section_content(
    topic: str,
    section_title: str,
    key_points: list,
    outline: dict,
    additional_requests: str = "",
    provider_id: str = None,
    model_name: str = None,
    target_word_count: int = None,
) -> tuple[str, int]:
    """Generate content for a single section."""
    system_prompt = "You are an expert blog content writer. Write engaging, detailed, SEO-optimized content."
    word_count_hint = (
        f"Write approximately {target_word_count} words"
        if target_word_count
        else "Write 400-800 words"
    )
    prompt = f"""Write the content for a blog post section.

Blog post topic: {topic}
Blog post title: {outline.get("title", topic)}
Section title: {section_title}
Key points to cover: {json.dumps(key_points)}
{f"Additional requests: {additional_requests}" if additional_requests else ""}

{word_count_hint} of detailed, engaging content for this section.
Use subheadings (H3) where appropriate.
Include relevant examples and practical advice.
Do NOT include the section title itself — just the body content.
Format in HTML."""

    text, total_tokens = await _call_ai(prompt, system_prompt, provider_id, model_name)
    return text, total_tokens


async def generate_introduction(
    topic: str,
    outline: dict,
    additional_requests: str = "",
    provider_id: str = None,
    model_name: str = None,
) -> tuple[str, int]:
    """Generate the introduction based on hook/problem/promise."""
    intro = outline.get("introduction", {})
    system_prompt = (
        "You are an expert blog content writer. Write engaging introductions."
    )
    prompt = f"""Write the introduction for a blog post.

Topic: {topic}
Title: {outline.get("title", topic)}
Hook idea: {intro.get("hook", "")}
Problem to present: {intro.get("problem", "")}
Promise to make: {intro.get("promise", "")}
{f"Additional requests: {additional_requests}" if additional_requests else ""}

Write a compelling 150-300 word introduction that:
1. Opens with an engaging hook
2. Presents the problem
3. Promises what the reader will learn
Format in HTML."""

    text, total_tokens = await _call_ai(prompt, system_prompt, provider_id, model_name)
    return text, total_tokens


async def generate_full_content(
    topic: str,
    outline: dict,
    additional_requests: str = "",
    provider_id: str = None,
    model_name: str = None,
    target_word_count: int = None,
) -> tuple[str, list, int]:
    """Generate the full post content from an outline. Returns (full_html, sections_list, total_tokens)."""
    total_tokens = 0

    # Generate introduction
    intro_html, intro_tokens = await generate_introduction(
        topic, outline, additional_requests, provider_id, model_name
    )
    total_tokens += intro_tokens

    sections = []
    full_html = intro_html

    outline_sections = outline.get("sections", [])
    # Calculate target words per section if target_word_count is provided
    words_per_section = None
    if target_word_count and len(outline_sections) > 0:
        words_per_section = target_word_count // len(outline_sections)

    for sec in outline_sections:
        sec_title = sec.get("title", "")
        key_points = sec.get("key_points", [])
        sec_content, sec_tokens = await generate_section_content(
            topic,
            sec_title,
            key_points,
            outline,
            additional_requests,
            provider_id,
            model_name,
            words_per_section,
        )
        total_tokens += sec_tokens
        sections.append(
            {
                "title": sec_title,
                "content": sec_content,
                "image_url": None,
            }
        )
        full_html += f"\n<h2>{sec_title}</h2>\n{sec_content}"

    return full_html, sections, total_tokens
