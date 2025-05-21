from hypothesis import HealthCheck, given, settings, strategies as st

from slugify import slugify


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    name=st.text(min_size=2, max_size=5000),
    location=st.text(min_size=2, max_size=5000),
    max_capacity=st.integers(min_value=1, max_value=1000000000000),
)
def test_create(client, name, location, max_capacity):
    # Perform POST request to /warehouses/
    response = client.post(
        "/warehouses/",
        json={
            "name": name,
            "location": location,
            "max_capacity": max_capacity,
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
    response = client.get(f"/warehouses/{post_response_data['slug']}")
    assert response.status_code == 200, "Expected HTTP 200"
    response_data = response.json()
    assert response_data["name"] == post_response_data["name"] == name
    assert response_data["slug"] == post_response_data["slug"]
    assert response_data["location"] == post_response_data["location"] == location
    assert response_data["capacity"] == post_response_data["capacity"] == max_capacity
    assert response_data["max_capacity"] == post_response_data["max_capacity"] == max_capacity

    # Perform DELETE request to /warehouses/<slug>
    response = client.delete(f"/warehouses/{response_data['slug']}")
    assert response.status_code == 204


def test_create_duplicate(client):
    # Example payload for creating a warehouse
    payload = {
        "name": "Test Warehouse",
        "location": "123 Test St, Test City, TS",
        "max_capacity": 100,
    }

    # Perform POST request to /warehouses/
    client.post("/warehouses/", json=payload)
    response = client.post("/warehouses/", json=payload)

    # Validate response and an error
    assert response.status_code == 409, "Expected HTTP 409"
    response_data = response.json()
    assert "unique constraint" in response_data["detail"].lower()


def test_get_nonexistent(client):
    response = client.get("/warehouses/does-not-exist")
    assert response.status_code == 404, "Expected HTTP 404"


def test_list_basic(client):
    response = client.get("/warehouses/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 1000  # Should match the maximum default limit


def test_list_offset_and_limit(client):
    response = client.get("/warehouses/?offset=2&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5  # Should respect the 'limit'


def test_list_invalid_limit(client):
    response = client.get("/warehouses/?limit=2000")  # Exceeds max allowed limit
    assert response.status_code == 422  # Unprocessable Entity for invalid query parameters


def test_list_invalid_offset(client):
    response = client.get("/warehouses/?offset=-10")  # Negative offset
    assert response.status_code == 422  # Unprocessable Entity for invalid query parameters


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    name=st.text(min_size=2, max_size=5000),
    location=st.text(min_size=2, max_size=5000),
    new_location=st.text(min_size=2, max_size=10000),
    max_capacity=st.integers(min_value=1, max_value=1000000000000),
    new_max_capacity=st.integers(min_value=1, max_value=1000000000000),
)
def test_update(client, name, location, new_location, max_capacity, new_max_capacity):
    # Perform PATCH request to /warehouses/
    response = client.post(
        "/warehouses/",
        json={
            "name": name,
            "location": location,
            "max_capacity": max_capacity,
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
        f"/warehouses/{post_response_data['slug']}",
        json={
            "location": new_location,
            "max_capacity": new_max_capacity,
        },
    )
    assert response.status_code == 200, "Expected HTTP 200"
    patch_response_data = response.json()
    assert patch_response_data is not None

    # Validate that data was indeed inserted into a database
    response = client.get(f"/warehouses/{post_response_data['slug']}")
    assert response.status_code == 200, "Expected HTTP 200"
    response_data = response.json()
    assert response_data["name"] == patch_response_data["name"]
    assert response_data["slug"] == patch_response_data["slug"]
    assert response_data["location"] == patch_response_data["location"]
    assert response_data["max_capacity"] == patch_response_data["max_capacity"]

    # Perform DELETE request to /warehouses/<slug>
    response = client.delete(f"/warehouses/{response_data['slug']}")
    assert response.status_code == 204


def test_patch_nonexistent(client):
    response = client.patch("/warehouses/does-not-exist", json={})
    assert response.status_code == 404, "Expected HTTP 404"


def test_delete_nonexistent(client):
    response = client.delete("/warehouses/does-not-exist")
    assert response.status_code == 404, "Expected HTTP 404"
