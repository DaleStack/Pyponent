from pyponent.core import render_to_string
from pyponent.html import div, p


def test_render_simple_html():
    # 1. Give the wrapper a hardcoded ID so it doesn't generate a random 'pyp-' one
    node = div(p("Hello World", id="test-id"), class_name="container", id="wrapper-id")

    # 2. Render it
    html = render_to_string(node)

    # 3. Assert the exact expected output!
    assert '<div class="container" id="wrapper-id">' in html
    assert '<p id="test-id">Hello World</p>' in html
