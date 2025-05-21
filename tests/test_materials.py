from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from slugify import slugify


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    name=st.text(min_size=2, max_size=5000),
    quantity_unit=st.text(min_size=2, max_size=40),
)
def test_create(client, name, quantity_unit):
    # Perform POST request to /materials/
    response = client.post(
        "/materials/",
        json={
            "name": name,
            "quantity_unit": quantity_unit,
        },
    )

    # Validate response status_code
    if response.status_code == 409:
        # hypothesis might try to generate a bunch of entities with the same slug, that's expected
        return
    if response.status_code == 422 and len(slugify(name)) < 1:
        # an "unslugifiable" name is not to be allowed, that's expected
        return

    assert response.status_code == 201, "Expected HTTP 201"
    post_response_data = response.json()
    assert post_response_data is not None

    # Validate that data was indeed inserted into a database
    response = client.get(f"/materials/{post_response_data['slug']}")
    assert response.status_code == 200, "Expected HTTP 200"
    response_data = response.json()
    assert response_data["name"] == post_response_data["name"]
    assert response_data["slug"] == post_response_data["slug"]
    assert response_data["quantity_unit"] == post_response_data["quantity_unit"]

    # Perform DELETE request to /materials/<slug>
    response = client.delete(f"/materials/{response_data['slug']}")
    assert response.status_code == 204


def test_create_duplicate(client):
    # Example payload for creating a material
    payload = {
        "name": "Test Material",
        "quantity_unit": "mole",
    }

    # Perform POST request to /materials/
    client.post("/materials/", json=payload)
    response = client.post("/materials/", json=payload)

    # Validate response and an error
    assert response.status_code == 409, "Expected HTTP 409"
    response_data = response.json()
    assert "unique constraint" in response_data["detail"].lower()


def test_get_nonexistent(client):
    response = client.get("/materials/does-not-exist")
    assert response.status_code == 404, "Expected HTTP 404"


def test_list_basic(client):
    response = client.get("/materials/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 1000  # Should match the maximum default limit


def test_list_offset_and_limit(client):
    response = client.get("/materials/?offset=2&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5  # Should respect the 'limit'


def test_list_invalid_limit(client):
    response = client.get("/materials/?limit=2000")  # Exceeds max allowed limit
    assert response.status_code == 422  # Unprocessable Entity for invalid query parameters


def test_list_invalid_offset(client):
    response = client.get("/materials/?offset=-10")  # Negative offset
    assert response.status_code == 422  # Unprocessable Entity for invalid query parameters


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    name=st.text(min_size=2, max_size=5000),
    quantity_unit=st.text(min_size=2, max_size=40),
    new_quantity_unit=st.text(min_size=2, max_size=40),
)
def test_update(client, name, quantity_unit, new_quantity_unit):
    # Perform PATCH request to /materials/
    response = client.post(
        "/materials/",
        json={
            "name": name,
            "quantity_unit": quantity_unit,
        },
    )

    # Validate response status_code
    if response.status_code == 409:
        # hypothesis might try to generate a bunch of entities with the same slug, that's expected
        return
    if response.status_code == 422 and len(slugify(name)) < 1:
        # an "unslugifiable" name is not to be allowed, that's expected
        return

    assert response.status_code == 201, "Expected HTTP 201"
    post_response_data = response.json()
    assert post_response_data is not None

    response = client.patch(
        f"/materials/{post_response_data['slug']}",
        json={
            "quantity_unit": new_quantity_unit,
        }
    )
    assert response.status_code == 200, "Expected HTTP 200"
    patch_response_data = response.json()
    assert patch_response_data is not None

    # Validate that data was indeed inserted into a database
    response = client.get(f"/materials/{post_response_data['slug']}")
    assert response.status_code == 200, "Expected HTTP 200"
    response_data = response.json()
    assert response_data["name"] == patch_response_data["name"]
    assert response_data["slug"] == patch_response_data["slug"]
    assert response_data["quantity_unit"] == patch_response_data["quantity_unit"]

    # Perform DELETE request to /materials/<slug>
    response = client.delete(f"/materials/{response_data['slug']}")
    assert response.status_code == 204


def test_patch_nonexistent(client):
    response = client.patch("/materials/does-not-exist", json={})
    assert response.status_code == 404, "Expected HTTP 404"


def test_delete_nonexistent(client):
    response = client.delete("/materials/does-not-exist")
    assert response.status_code == 404, "Expected HTTP 404"
