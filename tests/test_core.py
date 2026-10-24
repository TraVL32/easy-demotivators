from PIL import Image

from demotivator import DemotivatorStyle, create_demotivator, demotivator_bytes


def _img(w=800, h=600):
    return Image.new("RGB", (w, h), (120, 30, 200))


def test_basic():
    out = create_demotivator(_img(), "Заголовок", "Подпись")
    assert out.mode == "RGB" and out.width > 640


def test_long_text_and_tall_image():
    out = create_demotivator(_img(300, 3000), "слово " * 80, "x" * 300)
    assert out.height > 0


def test_no_text():
    assert create_demotivator(_img()).height > 0


def test_bytes():
    data = demotivator_bytes(_img(), "hi")
    assert data[:2] == b"\xff\xd8"


def test_rgba_input():
    img = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    assert create_demotivator(img, "a", style=DemotivatorStyle(upper=True))
