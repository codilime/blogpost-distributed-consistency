# Factory

A sample application written to illustrate the consistency of business operations in a microservices
architecture.

## Building process

After cloning the repository, `cd` into it and just create a Docker image running:

```sh
docker build -t factory:local .
```

## Running the application

Once you have an image built, run it like

```sh
docker run --rm --name factory -p 8000:8000 factory:local
```

This snippet is intended just for testing the app, it is usually not a good
idea to run any containers like that in production.

## Testing it

By default Docker container would probably start in `bridge` network mode (that
depends on your configuration), to find its IP address please run something like

```sh
docker inspect factory | grep IPAddress
```

In another terminal window simple `curl` can be used to test the application, e.g.

### Creating new materials (oxygen, hydrogen and sulphur)
```sh
curl -X POST -H "Content-Type: application/json" \
  -d '{"name": "Oxygen", "quantity_unit": "mole"}' \
  http://172.20.0.2:8000/materials/

curl -X POST -H "Content-Type: application/json" \
  -d '{"name": "Hydrogen", "quantity_unit": "mole"}' \
  http://172.20.0.2:8000/materials/

curl -X POST -H "Content-Type: application/json" \
  -d '{"name": "Sulphur", "quantity_unit": "mole"}' \
  http://172.20.0.2:8000/materials/
```

### Listing materials
```sh
curl -s http://172.20.0.2:8000/materials/ | jq
[
  {
    "name": "Oxygen",
    "slug": "oxygen",
    "quantity_unit": "mole",
    "id": "699139c4-eb11-4815-9021-2c8f66b38d5f"
  },
  {
    "name": "Hydrogen",
    "slug": "hydrogen",
    "quantity_unit": "mole",
    "id": "c18605cd-3e1e-4898-8192-1da5662bc30a"
  },
  {
    "name": "Sulphur",
    "slug": "sulphur",
    "quantity_unit": "mole",
    "id": "f49a9fff-8345-41cb-934f-f75adc3161b5"
  }
]
```

### Updating a material
```sh
curl -X PATCH -H "Content-Type: application/json" \
  -d '{"quantity_unit": "µg"}' \
  http://172.20.0.2:8000/materials/sulphur
```

### Fetching information about a single material
```sh
curl -s http://172.20.0.2:8000/materials/sulphur | jq
{
  "name": "Sulphur",
  "slug": "sulphur",
  "quantity_unit": "µg",
  "id": "f49a9fff-8345-41cb-934f-f75adc3161b5",
  "created_at": "2025-06-17T07:25:13",
  "boms": [],
  "stock": [],
  "products": []
}
```

### Removing a material
```sh
curl -X DELETE http://172.20.0.2:8000/materials/sulphur
```

### Creating a warehouse
```sh
curl -X POST -H "Content-Type: application/json" \
  -d '{"name": "Chemicals-1", "location": "Wien", "max_capacity": 1000000}' \
  http://172.20.0.2:8000/warehouses/
```

other operations look just like operations on materials, e.g. fetching
information about a single warehouse would be

```sh
curl -s http://172.20.0.2:8000/warehouses/chemicals-1 | jq
{
  "name": "Chemicals-1",
  "slug": "chemicals-1",
  "location": "Wien",
  "capacity": 1000000,
  "max_capacity": 1000000,
  "id": "ad02b895-ea98-4bd5-a889-7869f3e521fb",
  "created_at": "2025-06-17T07:28:47",
  "stock": []
}
```

### Delivery process
```sh
curl -X POST -H "Content-Type: application/json" \
  -d '{"warehouse_id": "ad02b895-ea98-4bd5-a889-7869f3e521fb", \
    "positions": [{"material_id": "699139c4-eb11-4815-9021-2c8f66b38d5f", 
    "quantity": 10}, {"material_id": "c18605cd-3e1e-4898-8192-1da5662bc30a", \
    "quantity": 20}]}' \
  http://172.20.0.2:8000/delivery/
```

Delivered materials stored in a warehouse will diminish its capacity, so after
testing a delivery something will change, e.g.

```sh
curl -s http://172.20.0.2:8000/warehouses/chemicals-1 | jq
{
  "name": "Chemicals-1",
  "slug": "chemicals-1",
  "location": "Wien",
  "capacity": 999970,
  "max_capacity": 1000000,
  "id": "ad02b895-ea98-4bd5-a889-7869f3e521fb",
  "created_at": "2025-06-17T07:28:47",
  "stock": [
    {
      "id": "d9b1f90d-8559-46e5-b6c3-546d16666aa0",
      "quantity": 10,
      "material_name": "Oxygen",
      "material_slug": "oxygen"
    },
    {
      "id": "31ed7603-43f2-41a9-a817-10ce54fbdf29",
      "quantity": 20,
      "material_name": "Hydrogen",
      "material_slug": "hydrogen"
    }
  ]
}
```

```sh
curl -s http://172.20.0.2:8000/materials/oxygen | jq
{
  "name": "Oxygen",
  "slug": "oxygen",
  "quantity_unit": "mole",
  "id": "699139c4-eb11-4815-9021-2c8f66b38d5f",
  "created_at": "2025-06-17T07:24:50",
  "boms": [],
  "stock": [
    {
      "id": "d9b1f90d-8559-46e5-b6c3-546d16666aa0",
      "warehouse_id": "ad02b895-ea98-4bd5-a889-7869f3e521fb",
      "quantity": 10,
      "warehouse_name": "Chemicals-1",
      "warehouse_slug": "chemicals-1"
    },
    {
      "id": "ca6bd72a-48ec-4a29-a3d9-545d09f8b7e9",
      "warehouse_id": "daae3903-dd42-473b-a160-0a838ccf65f0",
      "quantity": 10000,
      "warehouse_name": "Chemicals-2",
      "warehouse_slug": "chemicals-2"
    }
  ],
  "products": []
}
```

### Further testing

There are other endpoints, not described in this short README file. Feel
free to investigate them on your own by browsing files in the `routers/`
directory.
