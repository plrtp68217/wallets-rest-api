from decimal import Decimal
from uuid import uuid4

async def test_create_wallet(client):
    response = await client.post("api/v1/wallets")
    assert response.status_code == 200

async def test_get_wallets_when_empty_returns_empty_list(client):
    response = await client.get("api/v1/wallets")
    wallets = response.json()

    assert len(wallets) == 0

async def test_get_wallets_returns_all_created_wallets(client):
    await client.post("api/v1/wallets")
    await client.post("api/v1/wallets")
    await client.post("api/v1/wallets")

    response = await client.get("api/v1/wallets")
    wallets = response.json()
    
    assert len(wallets) == 3

async def test_deposit_increases_balance(client):
    created = await client.post("api/v1/wallets")

    wallet_id = created.json()["id"]

    response = await client.post(
        f"api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "DEPOSIT", "amount": 100},
    )

    assert response.status_code == 200
    assert Decimal(response.json()["balance"]) == Decimal("100.00")

async def test_withdraw_with_enough_balance_decreases_balance(client):
    created = await client.post("api/v1/wallets")

    wallet_id = created.json()["id"]

    await client.post(
        f"api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "DEPOSIT", "amount": 100},
    )

    response = await client.post(
        f"api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "WITHDRAW", "amount": 50},
    )

    assert response.status_code == 200
    assert Decimal(response.json()["balance"]) == Decimal("50.00")

async def test_withdraw_with_insufficient_balance_returns_400(client):
    created = await client.post("api/v1/wallets")

    wallet_id = created.json()["id"]

    await client.post(
        f"api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "DEPOSIT", "amount": 100},
    )

    response = await client.post(
        f"api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "WITHDRAW", "amount": 200},
    )

    assert response.status_code == 400

async def test_widthdraw_with_unknown_wallet_id(client):
    wallet_id = uuid4()

    response = await client.post(
        f"api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "WITHDRAW", "amount": 200},
    )
    
    assert response.status_code == 404

async def test_widthraw_with_incorrect_wallet_id(client):
    wallet_id = "123456"

    response = await client.post(
        f"api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "WIDTHRAW", "amount": 200},
    )

    assert response.status_code == 422