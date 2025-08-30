#!/usr/bin/env python3
"""
Test script for VysualPy RPC API

This script demonstrates how to test the VysualPy RPC API using both Python requests
and curl commands. It provides examples of all available API endpoints.
"""

import json
import requests
import time
import sys
from typing import Dict, Any

API_BASE_URL = "http://localhost:8080"

def test_api_info():
    """Test getting API information."""
    print("=== Testing API Info ===")
    response = requests.get(f"{API_BASE_URL}/api")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_server_status():
    """Test getting server status."""
    print("=== Testing Server Status ===")
    response = requests.get(f"{API_BASE_URL}/api/status")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_create_buildgraph():
    """Test creating a BuildGraph."""
    print("=== Testing Create BuildGraph ===")
    data = {
        "id": "test_graph_001",
        "code": "# Initial test code\nprint('Hello from BuildGraph!')"
    }
    
    response = requests.post(f"{API_BASE_URL}/api/buildgraph/create", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    return data["id"] if response.status_code == 200 else None

def test_add_node(graph_id: str):
    """Test adding a node to a BuildGraph."""
    print("=== Testing Add Node ===")
    data = {
        "graph_id": graph_id,
        "name": "TestNode1",
        "content": "def hello_world():\n    return 'Hello, World!'",
        "x": 100,
        "y": 200
    }
    
    response = requests.post(f"{API_BASE_URL}/api/buildgraph/add_node", json=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    print()
    return result.get("node_id") if response.status_code == 200 else None

def test_add_multiple_nodes(graph_id: str):
    """Test adding multiple nodes to a BuildGraph."""
    print("=== Testing Add Multiple Nodes ===")
    
    nodes = [
        {
            "name": "MathUtils",
            "content": "import math\n\ndef calculate_area(radius):\n    return math.pi * radius ** 2",
            "x": 50,
            "y": 50
        },
        {
            "name": "DataProcessor",
            "content": "def process_data(data):\n    return [x * 2 for x in data if x > 0]",
            "x": 300,
            "y": 100
        },
        {
            "name": "MainLogic",
            "content": "def main():\n    radius = 5\n    area = calculate_area(radius)\n    data = [1, -2, 3, 4, -5]\n    processed = process_data(data)\n    print(f'Area: {area}, Processed: {processed}')",
            "x": 150,
            "y": 300
        }
    ]
    
    node_ids = []
    for node_data in nodes:
        node_data["graph_id"] = graph_id
        response = requests.post(f"{API_BASE_URL}/api/buildgraph/add_node", json=node_data)
        if response.status_code == 200:
            result = response.json()
            node_ids.append(result.get("node_id"))
            print(f"Added node '{node_data['name']}' with ID: {result.get('node_id')}")
        else:
            print(f"Failed to add node '{node_data['name']}': {response.text}")
    
    print(f"Added {len(node_ids)} nodes")
    print()
    return node_ids

def test_get_nodes(graph_id: str):
    """Test getting all nodes in a BuildGraph."""
    print("=== Testing Get Nodes ===")
    data = {"graph_id": graph_id}
    
    response = requests.post(f"{API_BASE_URL}/api/buildgraph/get_nodes", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_update_node(graph_id: str, node_id: str):
    """Test updating a node."""
    print("=== Testing Update Node ===")
    data = {
        "graph_id": graph_id,
        "node_id": node_id,
        "content": "def updated_function():\n    print('This function has been updated!')\n    return 42",
        "name": "UpdatedNode"
    }
    
    response = requests.post(f"{API_BASE_URL}/api/buildgraph/update_node", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_compile_graph(graph_id: str):
    """Test compiling a BuildGraph."""
    print("=== Testing Compile Graph ===")
    data = {"graph_id": graph_id}
    
    response = requests.post(f"{API_BASE_URL}/api/buildgraph/compile", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_analyze_graph(graph_id: str):
    """Test analyzing a BuildGraph."""
    print("=== Testing Analyze Graph ===")
    data = {"graph_id": graph_id}
    
    response = requests.post(f"{API_BASE_URL}/api/buildgraph/analyze", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_get_aggregated_content(graph_id: str):
    """Test getting aggregated content."""
    print("=== Testing Get Aggregated Content ===")
    data = {"graph_id": graph_id}
    
    response = requests.post(f"{API_BASE_URL}/api/buildgraph/get_aggregated_content", json=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    if result.get("success"):
        print(f"Content length: {len(result.get('content', ''))}")
        print(f"Line count: {result.get('line_count')}")
        print(f"Node count: {result.get('node_count')}")
        print("Content preview:")
        content = result.get('content', '')
        lines = content.split('\n')
        for i, line in enumerate(lines[:15]):  # Show first 15 lines
            print(f"  {i+1:2d}: {line}")
        if len(lines) > 15:
            print(f"  ... ({len(lines) - 15} more lines)")
    else:
        print(f"Response: {json.dumps(result, indent=2)}")
    print()

def test_run_syntax_test(graph_id: str):
    """Test running syntax tests."""
    print("=== Testing Syntax Test ===")
    data = {
        "graph_id": graph_id,
        "test_type": "syntax"
    }
    
    response = requests.post(f"{API_BASE_URL}/api/buildgraph/test", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_run_structure_test(graph_id: str):
    """Test running structure tests."""
    print("=== Testing Structure Test ===")
    data = {
        "graph_id": graph_id,
        "test_type": "structure"
    }
    
    response = requests.post(f"{API_BASE_URL}/api/buildgraph/test", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_get_status(graph_id: str):
    """Test getting BuildGraph status."""
    print("=== Testing Get BuildGraph Status ===")
    data = {"graph_id": graph_id}
    
    response = requests.post(f"{API_BASE_URL}/api/buildgraph/status", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_list_buildgraphs():
    """Test listing all BuildGraphs."""
    print("=== Testing List BuildGraphs ===")
    response = requests.get(f"{API_BASE_URL}/api/buildgraphs")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_remove_node(graph_id: str, node_id: str):
    """Test removing a node."""
    print("=== Testing Remove Node ===")
    data = {
        "graph_id": graph_id,
        "node_id": node_id
    }
    
    response = requests.post(f"{API_BASE_URL}/api/buildgraph/remove_node", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_destroy_buildgraph(graph_id: str):
    """Test destroying a BuildGraph."""
    print("=== Testing Destroy BuildGraph ===")
    data = {"graph_id": graph_id}
    
    response = requests.post(f"{API_BASE_URL}/api/buildgraph/destroy", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def print_curl_examples():
    """Print example curl commands for all API endpoints."""
    print("=== CURL Command Examples ===")
    print()
    
    print("# Get API information")
    print("curl -X GET http://localhost:8080/api")
    print()
    
    print("# Get server status")
    print("curl -X GET http://localhost:8080/api/status")
    print()
    
    print("# List all BuildGraphs")
    print("curl -X GET http://localhost:8080/api/buildgraphs")
    print()
    
    print("# Create a new BuildGraph")
    print('curl -X POST http://localhost:8080/api/buildgraph/create \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"id": "test_graph", "code": "print(\\"Hello, World!\\")"}\'')
    print()
    
    print("# Add a node to the BuildGraph")
    print('curl -X POST http://localhost:8080/api/buildgraph/add_node \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"graph_id": "test_graph", "name": "HelloNode", "content": "def hello():\\n    return \\"Hello!\\"", "x": 100, "y": 200}\'')
    print()
    
    print("# Get all nodes in a BuildGraph")
    print('curl -X POST http://localhost:8080/api/buildgraph/get_nodes \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"graph_id": "test_graph"}\'')
    print()
    
    print("# Update a node")
    print('curl -X POST http://localhost:8080/api/buildgraph/update_node \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"graph_id": "test_graph", "node_id": "NODE_ID", "content": "def updated_function():\\n    return 42"}\'')
    print()
    
    print("# Compile the BuildGraph")
    print('curl -X POST http://localhost:8080/api/buildgraph/compile \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"graph_id": "test_graph"}\'')
    print()
    
    print("# Analyze the BuildGraph")
    print('curl -X POST http://localhost:8080/api/buildgraph/analyze \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"graph_id": "test_graph"}\'')
    print()
    
    print("# Get aggregated content")
    print('curl -X POST http://localhost:8080/api/buildgraph/get_aggregated_content \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"graph_id": "test_graph"}\'')
    print()
    
    print("# Run syntax tests")
    print('curl -X POST http://localhost:8080/api/buildgraph/test \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"graph_id": "test_graph", "test_type": "syntax"}\'')
    print()
    
    print("# Run structure tests")
    print('curl -X POST http://localhost:8080/api/buildgraph/test \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"graph_id": "test_graph", "test_type": "structure"}\'')
    print()
    
    print("# Get BuildGraph status")
    print('curl -X POST http://localhost:8080/api/buildgraph/status \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"graph_id": "test_graph"}\'')
    print()
    
    print("# Remove a node")
    print('curl -X POST http://localhost:8080/api/buildgraph/remove_node \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"graph_id": "test_graph", "node_id": "NODE_ID"}\'')
    print()
    
    print("# Destroy the BuildGraph")
    print('curl -X POST http://localhost:8080/api/buildgraph/destroy \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"graph_id": "test_graph"}\'')
    print()

def run_full_test_suite():
    """Run the complete test suite."""
    print("VysualPy RPC API Test Suite")
    print("===========================")
    print()
    
    try:
        # Basic server tests
        test_api_info()
        test_server_status()
        test_list_buildgraphs()
        
        # Create a BuildGraph
        graph_id = test_create_buildgraph()
        if not graph_id:
            print("Failed to create BuildGraph, stopping tests")
            return
        
        # Add nodes
        first_node_id = test_add_node(graph_id)
        additional_node_ids = test_add_multiple_nodes(graph_id)
        all_node_ids = [first_node_id] + additional_node_ids
        all_node_ids = [nid for nid in all_node_ids if nid]  # Filter out None values
        
        # Test node operations
        test_get_nodes(graph_id)
        
        if all_node_ids:
            test_update_node(graph_id, all_node_ids[0])
        
        # Test analysis and compilation
        test_compile_graph(graph_id)
        test_analyze_graph(graph_id)
        test_get_aggregated_content(graph_id)
        
        # Test automated testing
        test_run_syntax_test(graph_id)
        test_run_structure_test(graph_id)
        
        # Test status
        test_get_status(graph_id)
        test_list_buildgraphs()
        
        # Clean up - remove a node and then destroy the graph
        if all_node_ids:
            test_remove_node(graph_id, all_node_ids[-1])
        
        test_destroy_buildgraph(graph_id)
        
        print("=== Test Suite Complete ===")
        print("All tests completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the RPC server.")
        print("Make sure the server is running on http://localhost:8080")
        print("You can start it with: python vpy_rpc_server.py")
        
    except Exception as e:
        print(f"Unexpected error during testing: {e}")

def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--curl-examples":
        print_curl_examples()
    else:
        run_full_test_suite()

if __name__ == "__main__":
    main()
