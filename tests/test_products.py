from hypothesis import HealthCheck, given, settings, strategies as st

# from hypothesis.strategies import builds, integers, lists, text
from slugify import slugify


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    name=st.text(min_size=2, max_size=5000),
)
def test_create(client, name):
    # Perform POST request to /products/
    response = client.post(
        "/products/",
        json={"name": name},
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
    response = client.get(f"/products/{post_response_data['slug']}")
    assert response.status_code == 200, "Expected HTTP 200"
    response_data = response.json()
    assert response_data["name"] == post_response_data["name"]
    assert response_data["slug"] == post_response_data["slug"]

    # Perform DELETE request to /products/<slug>
    response = client.delete(f"/products/{response_data['slug']}")
    assert response.status_code == 204


def test_create_duplicate(client):
    # Example payload for creating a product
    payload = {"name": "Test Product"}

    # Perform POST request to /products/
    client.post("/products/", json=payload)
    response = client.post("/products/", json=payload)

    # Validate response and an error
    assert response.status_code == 409, "Expected HTTP 409"
    response_data = response.json()
    assert "unique constraint" in response_data["detail"].lower()


def test_get_nonexistent(client):
    response = client.get("/products/does-not-exist")
    assert response.status_code == 404, "Expected HTTP 404"


def test_list_basic(client):
    response = client.get("/products/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 1000  # Should match the maximum default limit


def test_list_offset_and_limit(client):
    response = client.get("/products/?offset=2&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5  # Should respect the 'limit'


def test_list_invalid_limit(client):
    response = client.get("/products/?limit=2000")  # Exceeds max allowed limit
    assert response.status_code == 422  # Unprocessable Entity for invalid query parameters


def test_list_invalid_offset(client):
    response = client.get("/products/?offset=-10")  # Negative offset
    assert response.status_code == 422  # Unprocessable Entity for invalid query parameters


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    name=st.text(min_size=2, max_size=5000),
)
def test_update(client, name):
    # Perform PATCH request to /products/
    response = client.post(
        "/products/",
        json={"name": name},
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
        f"/products/{post_response_data['slug']}",
        json={}
    )
    assert response.status_code == 200, "Expected HTTP 200"
    patch_response_data = response.json()
    assert patch_response_data is not None

    # Validate that data was indeed inserted into a database
    response = client.get(f"/products/{post_response_data['slug']}")
    assert response.status_code == 200, "Expected HTTP 200"
    response_data = response.json()
    assert response_data["name"] == patch_response_data["name"]
    assert response_data["slug"] == patch_response_data["slug"]

    # Perform DELETE request to /products/<slug>
    response = client.delete(f"/products/{response_data['slug']}")
    assert response.status_code == 204


def test_patch_nonexistent(client):
    response = client.patch("/products/does-not-exist", json={})
    assert response.status_code == 404, "Expected HTTP 404"


def test_delete_nonexistent(client):
    response = client.delete("/products/does-not-exist")
    assert response.status_code == 404, "Expected HTTP 404"
