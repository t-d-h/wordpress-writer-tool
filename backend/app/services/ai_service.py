"""
AI Service — handles research, outline, and content generation
using OpenAI, Gemini, or Anthropic depending on the configured provider.
"""
import json
from app.database import ai_providers_col


async def _get_provider():
    """Get the first available AI provider."""
    doc = await ai_providers_col.find_one()
    if not doc:
        raise Exception("No AI provider configured. Please add one in Settings.")
    return doc


async def _call_openai(api_key: str, prompt: str, system_prompt: str = "") -> tuple[str, int]:
    """Call OpenAI API."""
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=api_key)
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.7,
    )
    tokens = response.usage.total_tokens if response.usage else 0
    return response.choices[0].message.content, tokens


async def _call_gemini(api_key: str, prompt: str, system_prompt: str = "") -> tuple[str, int]:
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
        tokens = (response.usage_metadata.prompt_token_count or 0) + (response.usage_metadata.candidates_token_count or 0)
    return response.text, tokens


async def _call_anthropic(api_key: str, prompt: str, system_prompt: str = "") -> tuple[str, int]:
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
    tokens = response.usage.input_tokens + response.usage.output_tokens
    return response.content[0].text, tokens


async def _call_ai(prompt: str, system_prompt: str = "") -> tuple[str, int]:
    """Route to the appropriate AI provider."""
    provider = await _get_provider()
    provider_type = provider["provider_type"]
    api_key = provider["api_key"]

    if provider_type == "openai":
        return await _call_openai(api_key, prompt, system_prompt)
    elif provider_type == "gemini":
        return await _call_gemini(api_key, prompt, system_prompt)
    elif provider_type == "anthropic":
        return await _call_anthropic(api_key, prompt, system_prompt)
    else:
        raise Exception(f"Unknown provider type: {provider_type}")


async def research_topic(topic: str, additional_requests: str = "") -> tuple[dict, int]:
    """Research a topic: audience, keywords, key points to mention."""
    system_prompt = "You are an expert SEO content researcher. Respond only in valid JSON."
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

    text, tokens = await _call_ai(prompt, system_prompt)
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
    return data, tokens


async def generate_outline(topic: str, research_data: dict, additional_requests: str = "") -> tuple[dict, int]:
    """Generate a post outline: SEO title, meta description, intro, sections."""
    system_prompt = "You are an expert SEO content strategist. Respond only in valid JSON."
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
        ...more sections (aim for 5-8 sections for a comprehensive post)
    ]
}}"""

    text, tokens = await _call_ai(prompt, system_prompt)
    try:
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        data = json.loads(text.strip())
    except json.JSONDecodeError:
        data = {"raw_outline": text}
    return data, tokens


async def generate_section_content(topic: str, section_title: str, key_points: list, outline: dict, additional_requests: str = "") -> tuple[str, int]:
    """Generate content for a single section."""
    system_prompt = "You are an expert blog content writer. Write engaging, detailed, SEO-optimized content."
    prompt = f"""Write the content for a blog post section.

Blog post topic: {topic}
Blog post title: {outline.get("title", topic)}
Section title: {section_title}
Key points to cover: {json.dumps(key_points)}
{f"Additional requests: {additional_requests}" if additional_requests else ""}

Write 400-800 words of detailed, engaging content for this section.
Use subheadings (H3) where appropriate.
Include relevant examples and practical advice.
Do NOT include the section title itself — just the body content.
Format in HTML."""

    text, tokens = await _call_ai(prompt, system_prompt)
    return text, tokens


async def generate_introduction(topic: str, outline: dict, additional_requests: str = "") -> tuple[str, int]:
    """Generate the introduction based on hook/problem/promise."""
    intro = outline.get("introduction", {})
    system_prompt = "You are an expert blog content writer. Write engaging introductions."
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

    text, tokens = await _call_ai(prompt, system_prompt)
    return text, tokens


async def generate_full_content(topic: str, outline: dict, additional_requests: str = "") -> tuple[str, list, int]:
    """Generate the full post content from an outline. Returns (full_html, sections_list, total_tokens)."""
    total_tokens = 0

    # Generate introduction
    intro_html, intro_tokens = await generate_introduction(topic, outline, additional_requests)
    total_tokens += intro_tokens

    sections = []
    full_html = intro_html

    outline_sections = outline.get("sections", [])
    for sec in outline_sections:
        sec_title = sec.get("title", "")
        key_points = sec.get("key_points", [])
        sec_content, sec_tokens = await generate_section_content(
            topic, sec_title, key_points, outline, additional_requests
        )
        total_tokens += sec_tokens
        sections.append({
            "title": sec_title,
            "content": sec_content,
            "image_url": None,
        })
        full_html += f"\n<h2>{sec_title}</h2>\n{sec_content}"

    return full_html, sections, total_tokens
