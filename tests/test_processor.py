from processor import normalize_product


def test_normalize_product_valid():
    product = {"id": 1, "title": "Test", "price": "10.5", "userId": 123}
    result = normalize_product(product)
    assert result is not None
    assert result.price == 10.5
    assert result.source == "https://jsonplaceholder.typicode.com/posts"


def test_normalize_product_malformed():
    product = {"id": 1, "price": "not_a_number"}
    result = normalize_product(product)
    assert result is None
