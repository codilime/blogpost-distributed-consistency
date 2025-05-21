import pytest
from starlette.testclient import TestClient


@pytest.mark.parametrize(
    ("warehouse_capacity", "hydrogen_quantity", "sulphur_quantity", "expected_post_status_code"),
    [
        (100, 2, 1, 201),
        (100, 200, 100, 400),
        (100, 20, 10, 201),
        (1, 2, 1, 400),
        (3, 2, 1, 201),
    ],
)
def test_delivery_basic(
    client: TestClient,
    warehouse_capacity: int,
    hydrogen_quantity: int,
    sulphur_quantity: int,
    expected_post_status_code: int,
) -> None:  # noqa: D103
    warehouse = client.post(
        "/warehouses/",
        json={"name": "Test Warehouse", "location": "Wien", "max_capacity": warehouse_capacity},
    ).json()
    sulphur = client.post(
        "/materials/",
        json={"name": "sulphur", "quantity_unit": "mole"},
    ).json()
    hydrogen = client.post(
        "/materials/",
        json={"name": "hydrogen", "quantity_unit": "mole"},
    ).json()
    delivery_create_response = client.post(
        "/delivery/",
        json={
            "warehouse_id": warehouse.get("id"),
            "positions": [
                {"material_id": hydrogen.get("id"), "quantity": hydrogen_quantity},
                {"material_id": sulphur.get("id"), "quantity": sulphur_quantity},
            ],
        },
    )

    assert delivery_create_response.status_code == expected_post_status_code
    if expected_post_status_code == 201:
        warehouse_read = client.get(f"/warehouses/{warehouse['slug']}").json()
        assert {(s.get("material_name"), s.get("quantity")) for s in warehouse_read["stock"]} == {
            (hydrogen["name"], hydrogen_quantity),
            (sulphur["name"], sulphur_quantity),
        }
        assert (
            warehouse_read["capacity"] == warehouse_capacity - hydrogen_quantity - sulphur_quantity
        )
    if expected_post_status_code >= 400:
        warehouse_read = client.get(f"/warehouses/{warehouse['slug']}").json()
        assert warehouse_read["stock"] == []
        assert warehouse_read["capacity"] == warehouse_capacity


@pytest.mark.xfail(reason="Not yet implemented")
def test_material_deletion_removes_stock(client: TestClient) -> None:  # noqa: D103
    warehouse = client.post(
        "/warehouses/",
        json={"name": "Test Warehouse", "location": "Wien", "capacity": 3},
    ).json()
    sulphur = client.post(
        "/materials/",
        json={"name": "sulphur", "quantity_unit": "mole"},
    ).json()
    hydrogen = client.post(
        "/materials/",
        json={"name": "hydrogen", "quantity_unit": "mole"},
    ).json()
    client.post(
        "/delivery/",
        json={
            "warehouse_id": warehouse.get("id"),
            "positions": [
                {"material_id": hydrogen.get("id"), "quantity": 2},
                {"material_id": sulphur.get("id"), "quantity": 1},
            ],
        },
    )

    warehouse_read = client.get(f"/warehouses/{warehouse['slug']}").json()
    assert {(s.get("material_name"), s.get("quantity")) for s in warehouse_read["stock"]} == {
        (hydrogen["name"], 2),
        (sulphur["name"], 1),
    }

    client.delete(f"/materials/{hydrogen['id']}")
    assert client.delete(f"/materials/{hydrogen['id']}").status_code == 404

    warehouse_read = client.get(f"/warehouses/{warehouse['slug']}").json()
    assert {(s.get("material_name"), s.get("quantity")) for s in warehouse_read["stock"]} == {
        (sulphur["name"], 1),
    }