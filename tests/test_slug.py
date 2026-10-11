from app.api.admin_books import make_slug


def test_make_slug_ascii():
    assert make_slug("Atomic Habits") == "atomic-habits"
    assert make_slug("The Little Prince!") == "the-little-prince"


def test_make_slug_non_ascii_unicode():
    slug = make_slug("សៀវភៅត្រៀមប្រឡង")
    assert slug.startswith("book-")
    assert len(slug) > 5


def test_make_slug_special_characters_only():
    slug = make_slug("???!!!###")
    assert slug.startswith("book-")
