import pytest


# Integration test for the main pipeline (mocking fetch_all_products)
@pytest.mark.asyncio
async def test_full_pipeline(monkeypatch):
    from main import main

    # Mock fetch_all_products to return fake data
    async def fake_fetch_all_products(url):
        return [
            {"id": 1, "title": "A", "price": 1.0, "userId": 1},
            {"id": 2, "title": "B", "price": 2.0, "warrantyInformation": "yes"},
        ]

    monkeypatch.setattr("fetcher.fetch_all_products", fake_fetch_all_products)
    # Run the main pipeline
    await main()
