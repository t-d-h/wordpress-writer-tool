import pytest
from src.validation.word_count import WordCountService


@pytest.mark.parametrize(
    "html_content, expected_word_count",
    [
        ("", 0),
        (None, 0),
        ("   ", 0),
        ("<p>Hello world</p>", 2),
        ("<div><p>This is a test.</p></div>", 4),
        ("Just text", 2),
        ("<b>Bold</b> and <i>italic</i>", 4),
        ("Multiple      spaces", 2),
        ("   leading and trailing spaces  ", 4),
        ("hyphenated-word", 1),
        ("word-with-number123", 1),
        ("<p>Embedded<br>break</p>", 2),
        ("&nbsp; &amp; &lt; &gt;", 0),  # HTML entities
        ("<!-- This is a comment -->", 0),
        ("<style>p {color: red;}</style>", 0),
        ("<script>alert('hello')</script>", 0),
    ],
)
def test_word_count_service(html_content, expected_word_count):
    """Test WordCountService with various HTML inputs."""
    assert WordCountService.count_words(html_content) == expected_word_count
