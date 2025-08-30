# VysualPy RPC API

A REST API for testing and collaborating with VysualPy BuildGraph components. This API enables automated testing, remote BuildGraph manipulation, and lays the foundation for real-time collaboration features.

## Features

- **BuildGraph Management**: Create, update, and destroy BuildGraph instances
- **Node Operations**: Add, remove, update, and query BuildableNodes
- **Code Analysis**: Compile, analyze dependencies, and aggregate code content
- **Automated Testing**: Run syntax and structure tests on BuildGraphs
- **Remote Access**: HTTP REST API accessible via curl or any HTTP client
- **Collaboration Ready**: Foundation for multi-user collaborative editing

## Quick Start

### 1. Start the RPC Server

```bash
# Start on default port (8080)
python vpy_rpc_server.py

# Start on custom host/port
python vpy_rpc_server.py --host 0.0.0.0 --port 9000
```

### 2. Test the API

```bash
# Run the complete test suite
python test_rpc_api.py

# Show curl examples
python test_rpc_api.py --curl-examples
```

### 3. Basic Usage Examples

#### Create a BuildGraph
```bash
curl -X POST http://localhost:8080/api/buildgraph/create \
  -H "Content-Type: application/json" \
  -d '{"id": "my_graph", "code": "print(\"Hello, World!\")"}'
```

#### Add a Node
```bash
curl -X POST http://localhost:8080/api/buildgraph/add_node \
  -H "Content-Type: application/json" \
  -d '{
    "graph_id": "my_graph",
    "name": "MathUtils",
    "content": "def add(a, b):\n    return a + b",
    "x": 100,
    "y": 200
  }'
```

#### Compile the Graph
```bash
curl -X POST http://localhost:8080/api/buildgraph/compile \
  -H "Content-Type: application/json" \
  -d '{"graph_id": "my_graph"}'
```

## API Endpoints

### Information Endpoints
- `GET /api` - API information and available endpoints
- `GET /api/status` - Server status and uptime
- `GET /api/buildgraphs` - List all active BuildGraphs

### BuildGraph Management
- `POST /api/buildgraph/create` - Create a new BuildGraph
- `POST /api/buildgraph/destroy` - Destroy a BuildGraph
- `POST /api/buildgraph/status` - Get BuildGraph status

### Node Operations
- `POST /api/buildgraph/add_node` - Add a node to a BuildGraph
- `POST /api/buildgraph/get_nodes` - Get all nodes in a BuildGraph
- `POST /api/buildgraph/update_node` - Update a node's content
- `POST /api/buildgraph/remove_node` - Remove a node from a BuildGraph

### Code Analysis
- `POST /api/buildgraph/compile` - Compile the aggregated graph content
- `POST /api/buildgraph/analyze` - Analyze dependencies and structure
- `POST /api/buildgraph/get_aggregated_content` - Get organized code content

### Testing
- `POST /api/buildgraph/test` - Run automated tests (syntax, structure)

## Request/Response Format

All API endpoints use JSON for request and response data. POST requests require the `Content-Type: application/json` header.

### Standard Response Format
```json
{
  "success": true,
  "data": { /* endpoint-specific data */ },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Error Response Format
```json
{
  "success": false,
  "error": "Error message description",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Example Use Cases

### Automated Testing Pipeline

```bash
#!/bin/bash
# Create a BuildGraph
GRAPH_ID=$(curl -s -X POST http://localhost:8080/api/buildgraph/create \
  -H "Content-Type: application/json" \
  -d '{"id": "test_graph"}' | jq -r '.graph_id')

# Add test nodes
curl -s -X POST http://localhost:8080/api/buildgraph/add_node \
  -H "Content-Type: application/json" \
  -d '{
    "graph_id": "'$GRAPH_ID'",
    "name": "TestFunction",
    "content": "def test():\n    assert 2 + 2 == 4\n    return True"
  }'

# Run syntax tests
curl -s -X POST http://localhost:8080/api/buildgraph/test \
  -H "Content-Type: application/json" \
  -d '{"graph_id": "'$GRAPH_ID'", "test_type": "syntax"}'

# Clean up
curl -s -X POST http://localhost:8080/api/buildgraph/destroy \
  -H "Content-Type: application/json" \
  -d '{"graph_id": "'$GRAPH_ID'"}'
```

### Code Analysis and Metrics

```python
import requests
import json

# Create and populate a BuildGraph
response = requests.post("http://localhost:8080/api/buildgraph/create", 
                        json={"id": "analysis_test"})
graph_id = response.json()["graph_id"]

# Add multiple nodes with different code patterns
nodes = [
    {"name": "Utils", "content": "import math\ndef calculate(x):\n    return math.sqrt(x)"},
    {"name": "Data", "content": "class DataProcessor:\n    def __init__(self):\n        self.data = []"},
    {"name": "Main", "content": "def main():\n    processor = DataProcessor()\n    result = calculate(16)"}
]

for node in nodes:
    node["graph_id"] = graph_id
    requests.post("http://localhost:8080/api/buildgraph/add_node", json=node)

# Analyze the graph structure
analysis = requests.post("http://localhost:8080/api/buildgraph/analyze", 
                        json={"graph_id": graph_id})
print(f"Functions found: {len(analysis.json()['analysis']['functions'])}")
print(f"Classes found: {len(analysis.json()['analysis']['classes'])}")
print(f"Total lines: {analysis.json()['analysis']['total_lines']}")
```

## Collaboration Features (Future)

The RPC API is designed to support collaborative development features:

- **Real-time Sync**: Multiple users can work on the same BuildGraph
- **Change Tracking**: All modifications include timestamps and user info
- **Conflict Resolution**: API supports merging and conflict detection
- **Session Management**: Track active users and their changes
- **Permission System**: Control access to different BuildGraphs

## Architecture

The RPC API is built with a modular architecture:

```
VysualPyRPCServer
├── VysualPyAPIServer (Business Logic)
│   ├── BuildGraph Management
│   ├── Node Operations  
│   ├── Code Analysis
│   └── Testing Framework
└── VysualPyRPCHandler (HTTP Interface)
    ├── Request Routing
    ├── JSON Serialization
    ├── Error Handling
    └── CORS Support
```

## Requirements

- Python 3.7+
- `requests` library (for testing)
- Optional: VysualPy Qt components (for full integration)

## Development

The API server can run independently of the Qt-based VysualPy application, making it ideal for:

- Headless testing environments
- CI/CD pipelines
- Remote development scenarios
- Multi-platform deployment

## Contributing

When extending the API:

1. Add new endpoints to `VysualPyRPCHandler`
2. Implement business logic in `VysualPyAPIServer`
3. Add tests to `test_rpc_api.py`
4. Update this README with new examples

## License

Part of the VysualPy project - see main project license for details.
