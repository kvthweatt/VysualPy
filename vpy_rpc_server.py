#!/usr/bin/env python3
"""
VysualPy RPC API Server

This module provides an HTTP RPC API for testing and manipulating BuildGraph components.
It enables automated testing via curl POST requests and lays the foundation for 
collaborative development features.

The API is focused on BuildGraph operations including:
- Creating and managing BuildableNodes
- Executing code compilation and analysis
- Retrieving graph state and metrics
- Running automated tests
"""

import json
import threading
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict, List, Any, Optional
import sys
import os
import uuid
from datetime import datetime, timezone

# Add the VysualPy directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from vpy_blueprints import BuildGraphScene, BuildGraphView, BuildGraphWindow
    from vpy_content_aggregator import NodeContentAggregator
except ImportError as e:
    print(f"Warning: Could not import VysualPy modules: {e}")
    # Define mock classes for testing without Qt
    BuildGraphScene = None
    BuildGraphView = None
    BuildGraphWindow = None
    NodeContentAggregator = None


class VysualPyRPCHandler(BaseHTTPRequestHandler):
    """HTTP request handler for VysualPy RPC API."""
    
    def __init__(self, *args, **kwargs):
        self.api_server = None  # Will be set by the server
        super().__init__(*args, **kwargs)
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        """Handle POST requests for RPC calls."""
        try:
            # Parse the URL path
            parsed_path = urlparse(self.path)
            path = parsed_path.path.strip('/')
            
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            request_body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
            
            try:
                request_data = json.loads(request_body)
            except json.JSONDecodeError:
                self.send_error_response(400, "Invalid JSON in request body")
                return
            
            # Route the request
            if path == 'api/buildgraph/create':
                self.handle_create_buildgraph(request_data)
            elif path == 'api/buildgraph/add_node':
                self.handle_add_node(request_data)
            elif path == 'api/buildgraph/get_nodes':
                self.handle_get_nodes(request_data)
            elif path == 'api/buildgraph/update_node':
                self.handle_update_node(request_data)
            elif path == 'api/buildgraph/remove_node':
                self.handle_remove_node(request_data)
            elif path == 'api/buildgraph/compile':
                self.handle_compile(request_data)
            elif path == 'api/buildgraph/analyze':
                self.handle_analyze(request_data)
            elif path == 'api/buildgraph/get_aggregated_content':
                self.handle_get_aggregated_content(request_data)
            elif path == 'api/buildgraph/test':
                self.handle_run_test(request_data)
            elif path == 'api/buildgraph/status':
                self.handle_get_status(request_data)
            elif path == 'api/buildgraph/destroy':
                self.handle_destroy_buildgraph(request_data)
            else:
                self.send_error_response(404, f"Unknown API endpoint: {path}")
                
        except Exception as e:
            self.send_error_response(500, f"Internal server error: {str(e)}")
            traceback.print_exc()
    
    def do_GET(self):
        """Handle GET requests for status and information."""
        try:
            parsed_path = urlparse(self.path)
            path = parsed_path.path.strip('/')
            
            if path == '' or path == 'api':
                self.handle_api_info()
            elif path == 'api/status':
                self.handle_server_status()
            elif path == 'api/buildgraphs':
                self.handle_list_buildgraphs()
            else:
                self.send_error_response(404, f"Unknown GET endpoint: {path}")
                
        except Exception as e:
            self.send_error_response(500, f"Internal server error: {str(e)}")
    
    def send_json_response(self, data: Dict[str, Any], status_code: int = 200):
        """Send a JSON response."""
        response_body = json.dumps(data, indent=2)
        
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', str(len(response_body)))
        self.end_headers()
        
        self.wfile.write(response_body.encode('utf-8'))
    
    def send_error_response(self, status_code: int, message: str):
        """Send an error response."""
        self.send_json_response({
            'success': False,
            'error': message,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }, status_code)
    
    def handle_api_info(self):
        """Return API information and available endpoints."""
        info = {
            'name': 'VysualPy RPC API',
            'version': '1.0.0',
            'description': 'HTTP RPC API for BuildGraph testing and collaboration',
            'endpoints': {
                'POST /api/buildgraph/create': 'Create a new BuildGraph instance',
                'POST /api/buildgraph/add_node': 'Add a BuildableNode to a graph',
                'POST /api/buildgraph/get_nodes': 'Get all nodes in a graph',
                'POST /api/buildgraph/update_node': 'Update a node\'s content',
                'POST /api/buildgraph/remove_node': 'Remove a node from a graph',
                'POST /api/buildgraph/compile': 'Compile the graph content',
                'POST /api/buildgraph/analyze': 'Analyze graph dependencies',
                'POST /api/buildgraph/get_aggregated_content': 'Get aggregated code content',
                'POST /api/buildgraph/test': 'Run automated tests on the graph',
                'POST /api/buildgraph/destroy': 'Destroy a BuildGraph instance',
                'GET /api/status': 'Get server status',
                'GET /api/buildgraphs': 'List all active BuildGraph instances'
            },
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        self.send_json_response(info)
    
    def handle_server_status(self):
        """Return server status information."""
        status = {
            'status': 'running',
            'active_buildgraphs': len(self.server.api_server.buildgraphs) if self.server.api_server else 0,
            'uptime': (datetime.now(timezone.utc) - self.server.api_server.start_time).total_seconds() if self.server.api_server else 0,
            'qt_available': BuildGraphScene is not None,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        self.send_json_response(status)
    
    def handle_list_buildgraphs(self):
        """List all active BuildGraph instances."""
        if not self.server.api_server:
            self.send_error_response(500, "API server not initialized")
            return
        
        buildgraphs = []
        for graph_id, graph_info in self.server.api_server.buildgraphs.items():
            buildgraphs.append({
                'id': graph_id,
                'created_at': graph_info.get('created_at'),
                'node_count': len(graph_info.get('nodes', [])),
                'last_modified': graph_info.get('last_modified')
            })
        
        self.send_json_response({
            'success': True,
            'buildgraphs': buildgraphs,
            'total_count': len(buildgraphs)
        })
    
    def handle_create_buildgraph(self, request_data: Dict[str, Any]):
        """Create a new BuildGraph instance."""
        if not self.server.api_server:
            self.send_error_response(500, "API server not initialized")
            return
        
        graph_id = request_data.get('id') or str(uuid.uuid4())
        initial_code = request_data.get('code', '')
        
        try:
            result = self.server.api_server.create_buildgraph(graph_id, initial_code)
            self.send_json_response(result)
        except Exception as e:
            self.send_error_response(500, f"Failed to create BuildGraph: {str(e)}")
    
    def handle_add_node(self, request_data: Dict[str, Any]):
        """Add a BuildableNode to a graph."""
        if not self.server.api_server:
            self.send_error_response(500, "API server not initialized")
            return
        
        graph_id = request_data.get('graph_id')
        if not graph_id:
            self.send_error_response(400, "graph_id is required")
            return
        
        node_data = {
            'name': request_data.get('name', f'Node_{uuid.uuid4().hex[:8]}'),
            'content': request_data.get('content', ''),
            'x': request_data.get('x', 0),
            'y': request_data.get('y', 0)
        }
        
        try:
            result = self.server.api_server.add_node(graph_id, node_data)
            self.send_json_response(result)
        except Exception as e:
            self.send_error_response(500, f"Failed to add node: {str(e)}")
    
    def handle_get_nodes(self, request_data: Dict[str, Any]):
        """Get all nodes in a graph."""
        if not self.server.api_server:
            self.send_error_response(500, "API server not initialized")
            return
        
        graph_id = request_data.get('graph_id')
        if not graph_id:
            self.send_error_response(400, "graph_id is required")
            return
        
        try:
            result = self.server.api_server.get_nodes(graph_id)
            self.send_json_response(result)
        except Exception as e:
            self.send_error_response(500, f"Failed to get nodes: {str(e)}")
    
    def handle_update_node(self, request_data: Dict[str, Any]):
        """Update a node's content."""
        if not self.server.api_server:
            self.send_error_response(500, "API server not initialized")
            return
        
        graph_id = request_data.get('graph_id')
        node_id = request_data.get('node_id')
        
        if not graph_id or not node_id:
            self.send_error_response(400, "graph_id and node_id are required")
            return
        
        updates = {
            'content': request_data.get('content'),
            'name': request_data.get('name'),
            'x': request_data.get('x'),
            'y': request_data.get('y')
        }
        
        # Remove None values
        updates = {k: v for k, v in updates.items() if v is not None}
        
        try:
            result = self.server.api_server.update_node(graph_id, node_id, updates)
            self.send_json_response(result)
        except Exception as e:
            self.send_error_response(500, f"Failed to update node: {str(e)}")
    
    def handle_remove_node(self, request_data: Dict[str, Any]):
        """Remove a node from a graph."""
        if not self.server.api_server:
            self.send_error_response(500, "API server not initialized")
            return
        
        graph_id = request_data.get('graph_id')
        node_id = request_data.get('node_id')
        
        if not graph_id or not node_id:
            self.send_error_response(400, "graph_id and node_id are required")
            return
        
        try:
            result = self.server.api_server.remove_node(graph_id, node_id)
            self.send_json_response(result)
        except Exception as e:
            self.send_error_response(500, f"Failed to remove node: {str(e)}")
    
    def handle_compile(self, request_data: Dict[str, Any]):
        """Compile the graph content."""
        if not self.server.api_server:
            self.send_error_response(500, "API server not initialized")
            return
        
        graph_id = request_data.get('graph_id')
        if not graph_id:
            self.send_error_response(400, "graph_id is required")
            return
        
        try:
            result = self.server.api_server.compile_graph(graph_id)
            self.send_json_response(result)
        except Exception as e:
            self.send_error_response(500, f"Failed to compile graph: {str(e)}")
    
    def handle_analyze(self, request_data: Dict[str, Any]):
        """Analyze graph dependencies."""
        if not self.server.api_server:
            self.send_error_response(500, "API server not initialized")
            return
        
        graph_id = request_data.get('graph_id')
        if not graph_id:
            self.send_error_response(400, "graph_id is required")
            return
        
        try:
            result = self.server.api_server.analyze_graph(graph_id)
            self.send_json_response(result)
        except Exception as e:
            self.send_error_response(500, f"Failed to analyze graph: {str(e)}")
    
    def handle_get_aggregated_content(self, request_data: Dict[str, Any]):
        """Get aggregated code content."""
        if not self.server.api_server:
            self.send_error_response(500, "API server not initialized")
            return
        
        graph_id = request_data.get('graph_id')
        if not graph_id:
            self.send_error_response(400, "graph_id is required")
            return
        
        try:
            result = self.server.api_server.get_aggregated_content(graph_id)
            self.send_json_response(result)
        except Exception as e:
            self.send_error_response(500, f"Failed to get aggregated content: {str(e)}")
    
    def handle_run_test(self, request_data: Dict[str, Any]):
        """Run automated tests on the graph."""
        if not self.server.api_server:
            self.send_error_response(500, "API server not initialized")
            return
        
        graph_id = request_data.get('graph_id')
        test_type = request_data.get('test_type', 'syntax')
        
        if not graph_id:
            self.send_error_response(400, "graph_id is required")
            return
        
        try:
            result = self.server.api_server.run_test(graph_id, test_type)
            self.send_json_response(result)
        except Exception as e:
            self.send_error_response(500, f"Failed to run test: {str(e)}")
    
    def handle_get_status(self, request_data: Dict[str, Any]):
        """Get status of a specific BuildGraph."""
        if not self.server.api_server:
            self.send_error_response(500, "API server not initialized")
            return
        
        graph_id = request_data.get('graph_id')
        if not graph_id:
            self.send_error_response(400, "graph_id is required")
            return
        
        try:
            result = self.server.api_server.get_buildgraph_status(graph_id)
            self.send_json_response(result)
        except Exception as e:
            self.send_error_response(500, f"Failed to get status: {str(e)}")
    
    def handle_destroy_buildgraph(self, request_data: Dict[str, Any]):
        """Destroy a BuildGraph instance."""
        if not self.server.api_server:
            self.send_error_response(500, "API server not initialized")
            return
        
        graph_id = request_data.get('graph_id')
        if not graph_id:
            self.send_error_response(400, "graph_id is required")
            return
        
        try:
            result = self.server.api_server.destroy_buildgraph(graph_id)
            self.send_json_response(result)
        except Exception as e:
            self.send_error_response(500, f"Failed to destroy BuildGraph: {str(e)}")
    
    def log_message(self, format, *args):
        """Override to customize logging."""
        timestamp = datetime.now(timezone.utc).isoformat()
        print(f"[{timestamp}] {self.address_string()} - {format % args}")


class VysualPyAPIServer:
    """Main API server class that manages BuildGraph instances and operations."""
    
    def __init__(self):
        self.buildgraphs = {}  # Dict[str, Dict] - stores BuildGraph instances and metadata
        self.start_time = datetime.now(timezone.utc)
        self.qt_available = BuildGraphScene is not None
    
    def create_buildgraph(self, graph_id: str, initial_code: str = '') -> Dict[str, Any]:
        """Create a new BuildGraph instance."""
        if graph_id in self.buildgraphs:
            raise ValueError(f"BuildGraph with ID {graph_id} already exists")
        
        # Create mock graph data structure since we may not have Qt
        graph_info = {
            'id': graph_id,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'last_modified': datetime.now(timezone.utc).isoformat(),
            'nodes': {},
            'aggregator': None,
            'scene': None,
            'initial_code': initial_code
        }
        
        # If Qt is available, create actual BuildGraph components
        if self.qt_available and BuildGraphScene:
            try:
                # Note: In a real implementation, you might need to handle Qt application context
                # For now, we'll store the structure without creating actual Qt objects
                pass
            except Exception as e:
                print(f"Warning: Could not create Qt BuildGraph components: {e}")
        
        self.buildgraphs[graph_id] = graph_info
        
        return {
            'success': True,
            'graph_id': graph_id,
            'created_at': graph_info['created_at'],
            'qt_available': self.qt_available
        }
    
    def add_node(self, graph_id: str, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a BuildableNode to a graph."""
        if graph_id not in self.buildgraphs:
            raise ValueError(f"BuildGraph with ID {graph_id} not found")
        
        graph_info = self.buildgraphs[graph_id]
        node_id = str(uuid.uuid4())
        
        node_info = {
            'id': node_id,
            'name': node_data.get('name', f'Node_{node_id[:8]}'),
            'content': node_data.get('content', ''),
            'x': node_data.get('x', 0),
            'y': node_data.get('y', 0),
            'created_at': datetime.now(timezone.utc).isoformat(),
            'last_modified': datetime.now(timezone.utc).isoformat()
        }
        
        graph_info['nodes'][node_id] = node_info
        graph_info['last_modified'] = datetime.now(timezone.utc).isoformat()
        
        return {
            'success': True,
            'node_id': node_id,
            'node': node_info
        }
    
    def get_nodes(self, graph_id: str) -> Dict[str, Any]:
        """Get all nodes in a graph."""
        if graph_id not in self.buildgraphs:
            raise ValueError(f"BuildGraph with ID {graph_id} not found")
        
        graph_info = self.buildgraphs[graph_id]
        
        return {
            'success': True,
            'graph_id': graph_id,
            'nodes': list(graph_info['nodes'].values()),
            'node_count': len(graph_info['nodes'])
        }
    
    def update_node(self, graph_id: str, node_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a node's properties."""
        if graph_id not in self.buildgraphs:
            raise ValueError(f"BuildGraph with ID {graph_id} not found")
        
        graph_info = self.buildgraphs[graph_id]
        
        if node_id not in graph_info['nodes']:
            raise ValueError(f"Node with ID {node_id} not found in graph {graph_id}")
        
        node_info = graph_info['nodes'][node_id]
        
        # Update the node properties
        for key, value in updates.items():
            if key in ['name', 'content', 'x', 'y']:
                node_info[key] = value
        
        node_info['last_modified'] = datetime.now(timezone.utc).isoformat()
        graph_info['last_modified'] = datetime.now(timezone.utc).isoformat()
        
        return {
            'success': True,
            'node_id': node_id,
            'node': node_info
        }
    
    def remove_node(self, graph_id: str, node_id: str) -> Dict[str, Any]:
        """Remove a node from a graph."""
        if graph_id not in self.buildgraphs:
            raise ValueError(f"BuildGraph with ID {graph_id} not found")
        
        graph_info = self.buildgraphs[graph_id]
        
        if node_id not in graph_info['nodes']:
            raise ValueError(f"Node with ID {node_id} not found in graph {graph_id}")
        
        removed_node = graph_info['nodes'].pop(node_id)
        graph_info['last_modified'] = datetime.now(timezone.utc).isoformat()
        
        return {
            'success': True,
            'removed_node': removed_node,
            'remaining_nodes': len(graph_info['nodes'])
        }
    
    def compile_graph(self, graph_id: str) -> Dict[str, Any]:
        """Compile the graph content."""
        if graph_id not in self.buildgraphs:
            raise ValueError(f"BuildGraph with ID {graph_id} not found")
        
        graph_info = self.buildgraphs[graph_id]
        
        # Aggregate all node content
        aggregated_code = ""
        compilation_errors = []
        
        for node_info in graph_info['nodes'].values():
            content = node_info.get('content', '')
            if content.strip():
                aggregated_code += f"# From node: {node_info['name']}\n"
                aggregated_code += content + "\n\n"
        
        # Try to compile the aggregated code
        try:
            compile(aggregated_code, f'<buildgraph-{graph_id}>', 'exec')
            compilation_success = True
        except SyntaxError as e:
            compilation_success = False
            compilation_errors.append({
                'type': 'SyntaxError',
                'message': str(e),
                'line': e.lineno,
                'offset': e.offset
            })
        except Exception as e:
            compilation_success = False
            compilation_errors.append({
                'type': type(e).__name__,
                'message': str(e)
            })
        
        return {
            'success': True,
            'graph_id': graph_id,
            'compilation_success': compilation_success,
            'errors': compilation_errors,
            'aggregated_code_length': len(aggregated_code),
            'node_count': len(graph_info['nodes'])
        }
    
    def analyze_graph(self, graph_id: str) -> Dict[str, Any]:
        """Analyze graph dependencies and structure."""
        if graph_id not in self.buildgraphs:
            raise ValueError(f"BuildGraph with ID {graph_id} not found")
        
        graph_info = self.buildgraphs[graph_id]
        
        analysis = {
            'node_count': len(graph_info['nodes']),
            'total_lines': 0,
            'functions': [],
            'classes': [],
            'imports': [],
            'variables': []
        }
        
        # Analyze each node's content
        for node_info in graph_info['nodes'].values():
            content = node_info.get('content', '')
            lines = content.split('\n')
            analysis['total_lines'] += len([line for line in lines if line.strip()])
            
            # Simple analysis of code elements
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('def '):
                    func_name = stripped.split('(')[0].replace('def ', '').strip()
                    analysis['functions'].append({
                        'name': func_name,
                        'node': node_info['name'],
                        'node_id': node_info['id']
                    })
                elif stripped.startswith('class '):
                    class_name = stripped.split(':')[0].replace('class ', '').split('(')[0].strip()
                    analysis['classes'].append({
                        'name': class_name,
                        'node': node_info['name'],
                        'node_id': node_info['id']
                    })
                elif stripped.startswith('import ') or stripped.startswith('from '):
                    analysis['imports'].append({
                        'statement': stripped,
                        'node': node_info['name'],
                        'node_id': node_info['id']
                    })
                elif '=' in stripped and not stripped.startswith('#'):
                    # Simple variable detection
                    var_name = stripped.split('=')[0].strip()
                    if var_name.isidentifier():
                        analysis['variables'].append({
                            'name': var_name,
                            'node': node_info['name'],
                            'node_id': node_info['id']
                        })
        
        return {
            'success': True,
            'graph_id': graph_id,
            'analysis': analysis
        }
    
    def get_aggregated_content(self, graph_id: str) -> Dict[str, Any]:
        """Get aggregated code content from all nodes."""
        if graph_id not in self.buildgraphs:
            raise ValueError(f"BuildGraph with ID {graph_id} not found")
        
        graph_info = self.buildgraphs[graph_id]
        
        # Build aggregated content with proper organization
        content_parts = []
        line_mapping = {}
        current_line = 1
        
        # Add header
        content_parts.append(f"# Aggregated content from BuildGraph: {graph_id}")
        content_parts.append(f"# Generated at: {datetime.now(timezone.utc).isoformat()}")
        content_parts.append("")
        current_line += 3
        
        # Add content from each node
        for node_info in graph_info['nodes'].values():
            content = node_info.get('content', '').strip()
            if content:
                # Add node header
                node_header = f"# === From node: {node_info['name']} ==="
                content_parts.append(node_header)
                line_mapping[current_line] = {
                    'type': 'node_header',
                    'node_id': node_info['id'],
                    'node_name': node_info['name']
                }
                current_line += 1
                
                # Add node content
                node_lines = content.split('\n')
                for i, line in enumerate(node_lines):
                    content_parts.append(line)
                    line_mapping[current_line] = {
                        'type': 'code',
                        'node_id': node_info['id'],
                        'node_name': node_info['name'],
                        'original_line': i + 1
                    }
                    current_line += 1
                
                # Add separator
                content_parts.append("")
                current_line += 1
        
        aggregated_content = '\n'.join(content_parts)
        
        return {
            'success': True,
            'graph_id': graph_id,
            'content': aggregated_content,
            'line_count': len(content_parts),
            'line_mapping': line_mapping,
            'node_count': len(graph_info['nodes'])
        }
    
    def run_test(self, graph_id: str, test_type: str) -> Dict[str, Any]:
        """Run automated tests on the graph."""
        if graph_id not in self.buildgraphs:
            raise ValueError(f"BuildGraph with ID {graph_id} not found")
        
        graph_info = self.buildgraphs[graph_id]
        test_results = {
            'test_type': test_type,
            'passed': 0,
            'failed': 0,
            'errors': [],
            'details': []
        }
        
        if test_type == 'syntax':
            # Test syntax of each node
            for node_info in graph_info['nodes'].values():
                content = node_info.get('content', '')
                if content.strip():
                    try:
                        compile(content, f"<node-{node_info['id']}>", 'exec')
                        test_results['passed'] += 1
                        test_results['details'].append({
                            'node_id': node_info['id'],
                            'node_name': node_info['name'],
                            'status': 'passed',
                            'message': 'Syntax valid'
                        })
                    except SyntaxError as e:
                        test_results['failed'] += 1
                        test_results['errors'].append({
                            'node_id': node_info['id'],
                            'node_name': node_info['name'],
                            'error': str(e),
                            'line': e.lineno
                        })
                        test_results['details'].append({
                            'node_id': node_info['id'],
                            'node_name': node_info['name'],
                            'status': 'failed',
                            'message': f'Syntax error: {str(e)}'
                        })
        
        elif test_type == 'structure':
            # Test overall graph structure
            total_nodes = len(graph_info['nodes'])
            nodes_with_content = len([n for n in graph_info['nodes'].values() if n.get('content', '').strip()])
            
            if total_nodes > 0:
                test_results['passed'] += 1
                test_results['details'].append({
                    'test': 'node_count',
                    'status': 'passed',
                    'message': f'Graph has {total_nodes} nodes'
                })
            else:
                test_results['failed'] += 1
                test_results['details'].append({
                    'test': 'node_count',
                    'status': 'failed',
                    'message': 'Graph has no nodes'
                })
            
            if nodes_with_content > 0:
                test_results['passed'] += 1
                test_results['details'].append({
                    'test': 'content_coverage',
                    'status': 'passed',
                    'message': f'{nodes_with_content}/{total_nodes} nodes have content'
                })
            else:
                test_results['failed'] += 1
                test_results['details'].append({
                    'test': 'content_coverage',
                    'status': 'failed',
                    'message': 'No nodes have content'
                })
        
        return {
            'success': True,
            'graph_id': graph_id,
            'test_results': test_results
        }
    
    def get_buildgraph_status(self, graph_id: str) -> Dict[str, Any]:
        """Get detailed status of a BuildGraph."""
        if graph_id not in self.buildgraphs:
            raise ValueError(f"BuildGraph with ID {graph_id} not found")
        
        graph_info = self.buildgraphs[graph_id]
        
        # Calculate various metrics
        nodes = graph_info['nodes']
        node_count = len(nodes)
        nodes_with_content = len([n for n in nodes.values() if n.get('content', '').strip()])
        total_lines = sum(len(n.get('content', '').split('\n')) for n in nodes.values())
        
        return {
            'success': True,
            'graph_id': graph_id,
            'status': {
                'created_at': graph_info['created_at'],
                'last_modified': graph_info['last_modified'],
                'node_count': node_count,
                'nodes_with_content': nodes_with_content,
                'total_lines': total_lines,
                'qt_available': self.qt_available
            }
        }
    
    def destroy_buildgraph(self, graph_id: str) -> Dict[str, Any]:
        """Destroy a BuildGraph instance."""
        if graph_id not in self.buildgraphs:
            raise ValueError(f"BuildGraph with ID {graph_id} not found")
        
        # Clean up any Qt resources if necessary
        graph_info = self.buildgraphs[graph_id]
        
        # Remove from tracking
        del self.buildgraphs[graph_id]
        
        return {
            'success': True,
            'graph_id': graph_id,
            'destroyed_at': datetime.now(timezone.utc).isoformat()
        }


class VysualPyRPCServer:
    """HTTP server wrapper for the VysualPy RPC API."""
    
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.api_server = VysualPyAPIServer()
        self.httpd = None
        self.server_thread = None
    
    def start(self):
        """Start the RPC server."""
        # Create custom handler class with reference to api_server
        def handler_factory(*args, **kwargs):
            handler = VysualPyRPCHandler(*args, **kwargs)
            return handler
        
        self.httpd = HTTPServer((self.host, self.port), handler_factory)
        self.httpd.api_server = self.api_server  # Attach API server to HTTP server
        
        print(f"VysualPy RPC Server starting on http://{self.host}:{self.port}")
        print("Available endpoints:")
        print("  GET  /api              - API information")
        print("  GET  /api/status       - Server status")
        print("  GET  /api/buildgraphs  - List BuildGraphs")
        print("  POST /api/buildgraph/* - BuildGraph operations")
        print()
        
        # Start server in a separate thread
        self.server_thread = threading.Thread(target=self.httpd.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        return True
    
    def stop(self):
        """Stop the RPC server."""
        if self.httpd:
            print("Stopping VysualPy RPC Server...")
            self.httpd.shutdown()
            self.httpd.server_close()
            
        if self.server_thread:
            self.server_thread.join(timeout=5.0)
        
        print("VysualPy RPC Server stopped.")
    
    def is_running(self):
        """Check if the server is running."""
        return self.server_thread and self.server_thread.is_alive()


def main():
    """Main entry point for running the RPC server."""
    import argparse
    
    parser = argparse.ArgumentParser(description='VysualPy RPC API Server')
    parser.add_argument('--host', default='localhost', help='Host to bind to (default: localhost)')
    parser.add_argument('--port', type=int, default=8080, help='Port to bind to (default: 8080)')
    
    args = parser.parse_args()
    
    server = VysualPyRPCServer(host=args.host, port=args.port)
    
    try:
        server.start()
        print("Press Ctrl+C to stop the server")
        
        # Keep the main thread alive
        while True:
            threading.Event().wait(1.0)
            
    except KeyboardInterrupt:
        print("\nReceived interrupt signal")
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        server.stop()


if __name__ == '__main__':
    main()
