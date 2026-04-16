import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.ai_service import clean_html


def test_clean_html_strips_backticks():
    assert "`" not in clean_html("`<p>Hello</p>`")
    assert "`" not in clean_html("``code``")
    assert "`" not in clean_html("`<h1>Title</h1>`")
    result = clean_html("`<p>Test</p>`")
    assert "<p>Test</p>" in result


def test_clean_html_strips_code_blocks():
    result = clean_html("```html\n<p>Content</p>\n```")
    assert "```" not in result
    assert "<p>Content</p>" in result

    result = clean_html("```\n<p>Content</p>\n```")
    assert "```" not in result
    assert "<p>Content</p>" in result


def test_clean_html_no_markdown():
    result = clean_html("```html\n<p>Test</p>\n```<script>alert(1)</script>")
    assert "```" not in result
    assert "`" not in result
    assert "<p>Test</p>" in result
    assert "<script>" not in result


def test_clean_html_preserves_allowed_tags():
    result = clean_html("<h1>Title</h1><p>Para</p>")
    assert "<h1>Title</h1>" in result
    assert "<p>Para</p>" in result

    result = clean_html("<strong>Bold</strong><em>Italic</em>")
    assert "<strong>Bold</strong>" in result
    assert "<em>Italic</em>" in result

    result = clean_html("<ul><li>Item</li></ul>")
    assert "<ul>" in result
    assert "<li>Item</li>" in result

    result = clean_html('<a href="http://example.com">Link</a>')
    assert "<a" in result
    assert 'href="http://example.com"' in result

    result = clean_html('<img src="http://example.com/img.jpg">')
    assert "<img" in result
    assert 'src="http://example.com/img.jpg"' in result


def test_clean_html_removes_disallowed_tags():
    result = clean_html("<script>alert(1)</script><p>Safe</p>")
    assert "<script>" not in result
    assert "<p>Safe</p>" in result

    result = clean_html("<div>Wrapper</div><p>Content</p>")
    assert "<div>" not in result
    assert "<p>Content</p>" in result

    result = clean_html("<style>.red{color:red}</style><p>Text</p>")
    assert "<style>" not in result
    assert "<p>Text</p>" in result

    result = clean_html('<iframe src="evil.com"></iframe><p>Text</p>')
    assert "<iframe>" not in result
    assert "<p>Text</p>" in result

    result = clean_html("<span>Inline</span><strong>Bold</strong>")
    assert "<span>" not in result
    assert "<strong>Bold</strong>" in result
