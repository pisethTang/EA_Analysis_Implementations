# A more compact implementations of all EA's from COMP SCI 3316

## Backend API

This project includes a FastAPI backend for running Genetic Algorithm solvers on TSP instances.

### Running the Server

From the repo root directory:

```bash
# Using uvicorn directly
uvicorn app.main:app --reload

# Or with the main module
python -m app.main
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

### Running Tests

From the repo root directory:

```bash
pytest tests/ -v
```

### API Endpoints

#### Health Check
- **GET** `/health` - Returns API status

#### List TSP Instances
- **GET** `/instances` - Lists available .tsp files from the `data/` directory

#### Run Solver
- **POST** `/runs` - Run GA on a TSP instance
  - Request body: `instance_filename`, `population_size`, `generations`, `mutation_rate`, `local_search_opt`
  - Response: `instance_name`, `algorithm_name`, `best_length`, `best_route`, `elapsed_time_seconds`, `parameters`
