"""
AI Service — handles research, outline, and content generation
using OpenAI, Gemini, or Anthropic depending on the configured provider.
"""

import asyncio
import json
import re
import httpx
from bson import ObjectId
from app.database import ai_providers_col
from openai import RateLimitError
from anthropic import RateLimitError as AnthropicRateLimitError

try:
    from google.api_core.exceptions import ResourceExhausted
except ImportError:

    class ResourceExhausted(Exception):
        pass


ALLOWED_TAGS = {
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "p",
    "strong",
    "em",
    "ul",
    "ol",
    "li",
    "a",
    "img",
}
SAFE_ATTRS = {"a": {"href"}, "img": {"src"}}


def clean_html(html: str) -> str:
    """Remove markdown artifacts and sanitize HTML to allowed tags whitelist."""
    if not html or not html.strip():
        return ""

    text = html

    if "```html" in text:
        parts = text.split("```html")
        text = "".join(p.split("```")[0] if i > 0 else p for i, p in enumerate(parts))
    elif "```" in text:
        parts = text.split("```")
        text = "".join(p.split("```")[0] if i > 0 else p for i, p in enumerate(parts))

    text = text.replace("`", "")

    if not text.strip():
        return ""

    from bs4 import BeautifulSoup

    try:
        soup = BeautifulSoup(text, "lxml")
    except Exception:
        soup = BeautifulSoup(text, "html.parser")

    all_tags = list(soup.find_all(True))
    for tag in all_tags:
        if tag.name not in ALLOWED_TAGS:
            tag.unwrap()

    for tag in soup.find_all(True):
        if tag.name in SAFE_ATTRS:
            allowed = SAFE_ATTRS[tag.name]
            tag.attrs = {k: v for k, v in tag.attrs.items() if k in allowed}
        else:
            tag.attrs.clear()

    result = text
    if soup.body:
        result = "".join(str(child) for child in soup.body.children)
    else:
        result = str(soup)

    return result.strip()


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
) -> tuple[str, int, int]:
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
    prompt_tokens = response.usage.prompt_tokens if response.usage else 0
    completion_tokens = response.usage.completion_tokens if response.usage else 0
    return response.choices[0].message.content, prompt_tokens, completion_tokens


async def _call_gemini(
    api_key: str, prompt: str, system_prompt: str = ""
) -> tuple[str, int, int]:
    """Call Gemini API."""
    from google import genai

    client = genai.Client(api_key=api_key)
    full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=full_prompt,
    )
    input_tokens = 0
    output_tokens = 0
    if response.usage_metadata:
        input_tokens = response.usage_metadata.prompt_token_count or 0
        output_tokens = response.usage_metadata.candidates_token_count or 0
    return response.text, input_tokens, output_tokens


async def _call_anthropic(
    api_key: str, prompt: str, system_prompt: str = ""
) -> tuple[str, int, int]:
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
    input_tokens = response.usage.input_tokens
    output_tokens = response.usage.output_tokens
    return response.content[0].text, input_tokens, output_tokens


async def _call_ai(
    prompt: str,
    system_prompt: str = "",
    provider_id: str = None,
    model_name: str = None,
    max_retries: int = 1,
    delay: int = 60,
    on_retry: callable = None,
) -> tuple[str, int, int]:
    """Route to the appropriate AI provider with retry logic."""
    provider = await _get_provider(provider_id)
    provider_type = provider["provider_type"]
    api_key = provider["api_key"]
    print(f"[DEBUG] provider_type: {repr(provider_type)}")

    for attempt in range(max_retries):
        try:
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
            elif provider_type == "openrouter":
                api_url = provider.get("api_url", "https://openrouter.ai/api/v1/")
                return await _call_openai(
                    api_key,
                    prompt,
                    system_prompt,
                    base_url=api_url,
                    model_name=model_name
                    or provider.get("model_name", "anthropic/claude-3.5-sonnet"),
                )
            elif provider_type == "nvidia_nim":
                api_url = provider.get(
                    "api_url", "https://integrate.api.nvidia.com/v1/"
                )
                return await _call_openai(
                    api_key,
                    prompt,
                    system_prompt,
                    base_url=api_url,
                    model_name=model_name
                    or provider.get("model_name", "meta/llama-3.1-405b-instruct"),
                )
            else:
                raise Exception(f"Unknown provider type: {provider_type}")
        except (RateLimitError, AnthropicRateLimitError, ResourceExhausted) as e:
            if attempt < max_retries - 1:
                print(
                    f"[RATE_LIMIT] AI provider rate limit exceeded. Retrying in {delay}s... ({attempt + 1}/{max_retries})"
                )
                if on_retry:
                    await on_retry(attempt + 1, max_retries)
                await asyncio.sleep(delay)
            else:
                raise Exception(
                    f"AI provider call failed after {max_retries} retries: {e}"
                ) from e
        except Exception as e:
            raise Exception(
                f"An unexpected error occurred while calling the AI provider: {e}"
            ) from e


async def research_topic(
    topic: str,
    additional_requests: str = "",
    provider_id: str = None,
    model_name: str = None,
    language: str = "vietnamese",
    on_retry: callable = None,
) -> tuple[dict, int, int]:
    """Research a topic: audience, keywords, key points to mention."""
    if language == "vietnamese":
        system_prompt = (
            "You are an expert SEO content researcher for Vietnamese content. "
            "Write all content in Vietnamese. Use formal, professional Vietnamese "
            "with appropriate cultural context. Respond only in valid JSON."
        )
    else:
        system_prompt = (
            "You are an expert SEO content researcher. "
            "Write all content in English. Respond only in valid JSON."
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

    text, input_tokens, output_tokens = await _call_ai(
        prompt, system_prompt, provider_id, model_name, on_retry=on_retry
    )
    try:
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        text = re.sub(r"//.*", "", text)
        data = json.loads(text.strip())
    except (json.JSONDecodeError, IndexError):
        data = {"raw_research": text}
    return data, input_tokens, output_tokens


async def generate_outline(
    topic: str,
    research_data: dict,
    additional_requests: str = "",
    provider_id: str = None,
    model_name: str = None,
    target_section_count: int = None,
    language: str = "vietnamese",
    on_retry: callable = None,
) -> tuple[dict, int, int]:
    """Generate a post outline: SEO title, meta description, intro, sections."""
    if language == "vietnamese":
        system_prompt = (
            "You are an expert SEO content strategist for Vietnamese content. "
            "Write all content in Vietnamese. Use formal, professional Vietnamese "
            "with appropriate cultural context. Respond only in valid JSON."
        )
    else:
        system_prompt = (
            "You are an expert SEO content strategist. "
            "Write all content in English. Respond only in valid JSON."
        )
    section_count_hint = (
        f"Create exactly {target_section_count} sections"
        if target_section_count
        else "Create 5-8 sections"
    )
    prompt = f"""Create a detailed blog post outline based on:

Topic: {topic}
Use the following research data to inform the outline:
- Target Audience: {research_data.get("target_audience", "not specified")}
- Keywords: {", ".join(research_data.get("keywords", []))}
- Key Points: {", ".join(research_data.get("key_points", []))}

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

    text, input_tokens, output_tokens = await _call_ai(
        prompt, system_prompt, provider_id, model_name, on_retry=on_retry
    )
    try:
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        text = re.sub(r"//.*", "", text)
        data = json.loads(text.strip())
    except json.JSONDecodeError:
        data = {"raw_outline": text}
    return data, input_tokens, output_tokens


async def generate_section_content(
    topic: str,
    section_title: str,
    key_points: list,
    outline: dict,
    research_data: dict,
    additional_requests: str = "",
    provider_id: str = None,
    model_name: str = None,
    target_word_count: int = None,
    language: str = "vietnamese",
    on_retry: callable = None,
) -> tuple[str, int, int]:
    """Generate content for a single section."""
    if language == "vietnamese":
        system_prompt = (
            "You are an expert blog content writer for Vietnamese content. "
            "Write engaging, detailed, SEO-optimized content in Vietnamese. "
            "Use formal, professional Vietnamese with appropriate cultural context."
        )
    else:
        system_prompt = (
            "You are an expert blog content writer. "
            "Write engaging, detailed, SEO-optimized content in English."
        )
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

Use the following research data to inform the content:
- Target Audience: {research_data.get("target_audience", "not specified")}
- Keywords: {", ".join(research_data.get("keywords", []))}

{f"Additional requests: {additional_requests}" if additional_requests else ""}

{word_count_hint} of detailed, engaging content for this section.
Use subheadings (H3) where appropriate.
Include relevant examples and practical advice.
Do NOT include the section title itself — just the body content.
Format in HTML."""

    text, input_tokens, output_tokens = await _call_ai(
        prompt, system_prompt, provider_id, model_name, on_retry=on_retry
    )
    try:
        cleaned = clean_html(text)
    except Exception:
        cleaned = text
    return cleaned, input_tokens, output_tokens


async def generate_introduction(
    topic: str,
    outline: dict,
    research_data: dict,
    additional_requests: str = "",
    provider_id: str = None,
    model_name: str = None,
    language: str = "vietnamese",
    on_retry: callable = None,
) -> tuple[str, int, int]:
    """Generate the introduction based on hook/problem/promise."""
    intro = outline.get("introduction", {})
    if language == "vietnamese":
        system_prompt = (
            "You are an expert blog content writer for Vietnamese content. "
            "Write engaging introductions in Vietnamese. "
            "Use formal, professional Vietnamese with appropriate cultural context."
        )
    else:
        system_prompt = (
            "You are an expert blog content writer. "
            "Write engaging introductions in English."
        )
    prompt = f"""Write the introduction for a blog post.

Topic: {topic}
Title: {outline.get("title", topic)}
Research data: {json.dumps(research_data)}
Hook idea: {intro.get("hook", "")}
Problem to present: {intro.get("problem", "")}
Promise to make: {intro.get("promise", "")}
{f"Additional requests: {additional_requests}" if additional_requests else ""}

Write a compelling 150-300 word introduction that:
1. Opens with an engaging hook
2. Presents the problem
3. Promises what the reader will learn
Format in HTML."""

    text, input_tokens, output_tokens = await _call_ai(
        prompt, system_prompt, provider_id, model_name, on_retry=on_retry
    )
    try:
        cleaned = clean_html(text)
    except Exception:
        cleaned = text
    return cleaned, input_tokens, output_tokens


async def generate_full_content(
    topic: str,
    outline: dict,
    research_data: dict,
    additional_requests: str = "",
    provider_id: str = None,
    model_name: str = None,
    target_word_count: int = None,
    language: str = "vietnamese",
    on_retry: callable = None,
) -> tuple[str, list, int, int]:
    """Generate the full post content from an outline using parallel tasks."""
    outline_sections = outline.get("sections", [])

    # Calculate target words per section if target_word_count is provided
    words_per_section = None
    if target_word_count and len(outline_sections) > 0:
        try:
            target_word_count_int = int(target_word_count)
            if target_word_count_int > 0:
                words_per_section = target_word_count_int // len(outline_sections)
        except (ValueError, TypeError):
            words_per_section = None

    # Prepare all tasks
    tasks = [
        generate_introduction(
            topic,
            outline,
            research_data,
            additional_requests,
            provider_id,
            model_name,
            language,
            on_retry,
        )
    ]
    for sec in outline_sections:
        tasks.append(
            generate_section_content(
                topic,
                sec.get("title", ""),
                sec.get("key_points", []),
                outline,
                research_data,
                additional_requests,
                provider_id,
                model_name,
                words_per_section,
                language,
                on_retry,
            )
        )

    # Run all tasks in parallel
    results = await asyncio.gather(*tasks)

    # Process results
    intro_html, i_in, i_out = results[0]
    input_tokens = i_in
    output_tokens = i_out

    sections = []
    full_html = intro_html

    for i, (sec_html, s_in, s_out) in enumerate(results[1:]):
        sec_title = outline_sections[i].get("title", "")
        input_tokens += s_in
        output_tokens += s_out
        sections.append(
            {
                "title": sec_title,
                "content": sec_html,
                "image_url": None,
            }
        )
        full_html += f"\n<h2>{sec_title}</h2>\n{sec_html}"

    return full_html, sections, input_tokens, output_tokens


async def verify_api_key(provider_type: str, api_key: str, api_url: str = "") -> dict:
    """Verify an AI provider API key by making a simple test call."""
    try:
        if provider_type == "openai":
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=api_key)
            await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1,
            )
            return {"ok": True, "message": "API key is valid"}
        elif provider_type == "gemini":
            from google import genai

            client = genai.Client(api_key=api_key)
            client.models.generate_content(model="gemini-2.0-flash", contents="test")
            return {"ok": True, "message": "API key is valid"}
        elif provider_type == "anthropic":
            from anthropic import AsyncAnthropic

            client = AsyncAnthropic(api_key=api_key)
            await client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1,
                messages=[{"role": "user", "content": "test"}],
            )
            return {"ok": True, "message": "API key is valid"}
        elif provider_type == "openai_compatible":
            from openai import AsyncOpenAI

            base = api_url.rstrip("/")
            if not base.endswith("/v1"):
                base = base + "/v1"
            client = AsyncOpenAI(api_key=api_key, base_url=base)
            await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1,
            )
            return {"ok": True, "message": "API key is valid"}
        elif provider_type == "openrouter":
            from openai import AsyncOpenAI

            base = api_url.rstrip("/") if api_url else "https://openrouter.ai/api/v1"
            if not base.endswith("/v1"):
                base = base + "/v1"
            client = AsyncOpenAI(api_key=api_key, base_url=base)
            await client.chat.completions.create(
                model="anthropic/claude-3.5-sonnet",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1,
            )
            return {"ok": True, "message": "API key is valid"}
        elif provider_type == "nvidia_nim":
            from openai import AsyncOpenAI

            base = (
                api_url.rstrip("/")
                if api_url
                else "https://integrate.api.nvidia.com/v1"
            )
            if not base.endswith("/v1"):
                base = base + "/v1"
            client = AsyncOpenAI(api_key=api_key, base_url=base)
            await client.chat.completions.create(
                model="meta/llama-3.1-405b-instruct",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1,
            )
            return {"ok": True, "message": "API key is valid"}
        else:
            return {"ok": False, "error": f"Unknown provider type: {provider_type}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}
