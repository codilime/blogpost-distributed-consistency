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
depends on your configuration), to find its IP address open another terminal and
run something like.

```sh
export FACTORY_IP_ADDRESS=$( docker inspect factory | jq -r '.[].NetworkSettings.IPAddress' )
```

This should give you an important information about the IP of the container. And
that will be available as the `FACTORY_IP_ADDRESS` environment variable. Now with
that variable available (so in the same terminal window), you can run some `curl`
commands to test the application:

### Creating new materials (oxygen, hydrogen and sulphur)
```sh
curl -X POST -H "Content-Type: application/json" \
  -d '{"name": "Oxygen", "quantity_unit": "mole"}' \
  http://${FACTORY_IP_ADDRESS}:8000/materials/

curl -X POST -H "Content-Type: application/json" \
  -d '{"name": "Hydrogen", "quantity_unit": "mole"}' \
  http://${FACTORY_IP_ADDRESS}:8000/materials/

curl -X POST -H "Content-Type: application/json" \
  -d '{"name": "Sulphur", "quantity_unit": "mole"}' \
  http://${FACTORY_IP_ADDRESS}:8000/materials/
```

### Listing materials
```sh
curl -s http://${FACTORY_IP_ADDRESS}:8000/materials/ | jq
```

### Updating a material
```sh
curl -X PATCH -H "Content-Type: application/json" \
  -d '{"quantity_unit": "µg"}' \
  http://${FACTORY_IP_ADDRESS}:8000/materials/sulphur
```

### Fetching information about a single material
```sh
curl -s http://${FACTORY_IP_ADDRESS}:8000/materials/sulphur | jq
```

### Removing a material
```sh
curl -X DELETE http://${FACTORY_IP_ADDRESS}:8000/materials/sulphur
```

### Creating a warehouse
```sh
curl -X POST -H "Content-Type: application/json" \
  -d '{"name": "Chemicals-1", "location": "Wien", "max_capacity": 1000000}' \
  http://${FACTORY_IP_ADDRESS}:8000/warehouses/
```

other operations look just like operations on materials, e.g. fetching
information about a single warehouse would be

```sh
curl -s http://${FACTORY_IP_ADDRESS}:8000/warehouses/chemicals-1 | jq
```

### Delivery process
```sh
curl -X POST -H "Content-Type: application/json" \
  -d '{"warehouse_id": "ad02b895-ea98-4bd5-a889-7869f3e521fb", \
    "positions": [{"material_id": "699139c4-eb11-4815-9021-2c8f66b38d5f", 
    "quantity": 10}, {"material_id": "c18605cd-3e1e-4898-8192-1da5662bc30a", \
    "quantity": 20}]}' \
  http://${FACTORY_IP_ADDRESS}:8000/delivery/
```

Delivered materials stored in a warehouse will diminish its capacity, so after
testing a delivery something will change, e.g.

```sh
curl -s http://${FACTORY_IP_ADDRESS}:8000/warehouses/chemicals-1 | jq
```

```sh
curl -s http://${FACTORY_IP_ADDRESS}:8000/materials/oxygen | jq
```

### Further testing

There are other endpoints, not described in this short README file. Feel
free to investigate them on your own by browsing files in the `routers/`
directory.
