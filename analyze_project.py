#!/usr/bin/env python3
"""
VysualPy Project Analyzer

This tool scans the VysualPy source files and generates a structural overview
of classes, functions, and their relationships. It helps track the codebase
during refactoring and provides quick reference information.

Usage:
    python analyze_project.py [--output PROJECT_STRUCTURE.md] [--json project_structure.json]
"""

import ast
import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class FunctionInfo:
    """Information about a function definition."""
    name: str
    line_number: int
    is_async: bool
    is_method: bool
    parent_class: Optional[str]
    docstring: Optional[str]
    parameters: List[str]
    decorators: List[str]


@dataclass
class ClassInfo:
    """Information about a class definition."""
    name: str
    line_number: int
    base_classes: List[str]
    docstring: Optional[str]
    methods: List[FunctionInfo]
    decorators: List[str]


@dataclass
class FileInfo:
    """Information about a Python source file."""
    file_path: str
    line_count: int
    classes: List[ClassInfo]
    functions: List[FunctionInfo]
    imports: List[str]
    docstring: Optional[str]


class ProjectAnalyzer:
    """Analyzes Python source files and extracts structural information."""
    
    def __init__(self, source_dir: str = "."):
        self.source_dir = Path(source_dir)
        self.files_info: Dict[str, FileInfo] = {}
        
    def analyze_file(self, file_path: Path) -> Optional[FileInfo]:
        """Analyze a single Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            visitor = FileVisitor(file_path.name)
            visitor.visit(tree)
            
            return FileInfo(
                file_path=str(file_path.relative_to(self.source_dir)),
                line_count=len(content.splitlines()),
                classes=visitor.classes,
                functions=visitor.functions,
                imports=visitor.imports,
                docstring=visitor.module_docstring
            )
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return None
    
    def analyze_project(self) -> Dict[str, FileInfo]:
        """Analyze all Python files in the project."""
        python_files = list(self.source_dir.glob("*.py"))
        
        for file_path in python_files:
            if file_path.name.startswith('.'):
                continue  # Skip hidden files
                
            file_info = self.analyze_file(file_path)
            if file_info:
                self.files_info[file_path.name] = file_info
                
        return self.files_info
    
    def generate_markdown_report(self) -> str:
        """Generate a markdown report of the project structure."""
        lines = [
            "# VysualPy Project Structure Report",
            "",
            f"Generated on: {self._get_timestamp()}",
            f"Total files analyzed: {len(self.files_info)}",
            "",
            "## Overview",
            ""
        ]
        
        # Summary statistics
        total_classes = sum(len(info.classes) for info in self.files_info.values())
        total_functions = sum(len(info.functions) for info in self.files_info.values())
        total_lines = sum(info.line_count for info in self.files_info.values())
        
        lines.extend([
            f"- Total Classes: {total_classes}",
            f"- Total Functions: {total_functions}",
            f"- Total Lines of Code: {total_lines}",
            "",
            "## File Details",
            ""
        ])
        
        # Detailed file information
        for file_name in sorted(self.files_info.keys()):
            file_info = self.files_info[file_name]
            lines.extend(self._format_file_info(file_info))
            
        return "\n".join(lines)
    
    def _format_file_info(self, file_info: FileInfo) -> List[str]:
        """Format file information as markdown."""
        lines = [
            f"### {file_info.file_path}",
            "",
            f"**Lines:** {file_info.line_count} | **Classes:** {len(file_info.classes)} | **Functions:** {len(file_info.functions)}",
            ""
        ]
        
        if file_info.docstring:
            lines.extend([
                "**Description:**",
                f"> {file_info.docstring}",
                ""
            ])
        
        # Imports
        if file_info.imports:
            lines.extend([
                "**Key Imports:**",
                ""
            ])
            for imp in file_info.imports[:10]:  # Limit to first 10
                lines.append(f"- `{imp}`")
            if len(file_info.imports) > 10:
                lines.append(f"- ... and {len(file_info.imports) - 10} more")
            lines.append("")
        
        # Classes
        if file_info.classes:
            lines.extend([
                "**Classes:**",
                ""
            ])
            for cls in file_info.classes:
                inheritance = f"({', '.join(cls.base_classes)})" if cls.base_classes else ""
                lines.append(f"- `{cls.name}{inheritance}` (line {cls.line_number})")
                if cls.methods:
                    for method in cls.methods[:5]:  # Show first 5 methods
                        method_type = "async method" if method.is_async else "method"
                        lines.append(f"  - `{method.name}()` ({method_type})")
                    if len(cls.methods) > 5:
                        lines.append(f"  - ... and {len(cls.methods) - 5} more methods")
            lines.append("")
        
        # Functions
        if file_info.functions:
            lines.extend([
                "**Functions:**",
                ""
            ])
            for func in file_info.functions:
                func_type = "async function" if func.is_async else "function"
                params = ", ".join(func.parameters[:3])  # Show first 3 params
                if len(func.parameters) > 3:
                    params += ", ..."
                lines.append(f"- `{func.name}({params})` ({func_type}, line {func.line_number})")
            lines.append("")
        
        lines.append("---")
        lines.append("")
        return lines
    
    def _get_timestamp(self) -> str:
        """Get current timestamp string."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def save_json(self, output_path: str):
        """Save analysis results as JSON."""
        data = {
            "timestamp": self._get_timestamp(),
            "files": {name: asdict(info) for name, info in self.files_info.items()}
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


class FileVisitor(ast.NodeVisitor):
    """AST visitor that extracts structural information from a Python file."""
    
    def __init__(self, filename: str):
        self.filename = filename
        self.classes: List[ClassInfo] = []
        self.functions: List[FunctionInfo] = []
        self.imports: List[str] = []
        self.module_docstring: Optional[str] = None
        self.current_class: Optional[str] = None
        
    def visit_Module(self, node):
        """Visit module and extract docstring."""
        if (node.body and isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and 
            isinstance(node.body[0].value.value, str)):
            self.module_docstring = node.body[0].value.value.strip()
        self.generic_visit(node)
    
    def visit_Import(self, node):
        """Visit import statements."""
        for alias in node.names:
            self.imports.append(alias.name)
    
    def visit_ImportFrom(self, node):
        """Visit from-import statements."""
        module = node.module or ""
        for alias in node.names:
            if alias.name == "*":
                self.imports.append(f"from {module} import *")
            else:
                self.imports.append(f"from {module} import {alias.name}")
    
    def visit_ClassDef(self, node):
        """Visit class definitions."""
        old_class = self.current_class
        self.current_class = node.name
        
        # Extract class information
        base_classes = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_classes.append(f"{base.attr}")
        
        docstring = self._extract_docstring(node)
        decorators = [self._decorator_name(dec) for dec in node.decorator_list]
        
        class_info = ClassInfo(
            name=node.name,
            line_number=node.lineno,
            base_classes=base_classes,
            docstring=docstring,
            methods=[],
            decorators=decorators
        )
        
        self.classes.append(class_info)
        
        # Visit class body to collect methods
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_info = self._create_function_info(child, is_method=True, parent_class=node.name)
                class_info.methods.append(method_info)
            else:
                self.visit(child)
        
        self.current_class = old_class
    
    def visit_FunctionDef(self, node):
        """Visit function definitions."""
        if self.current_class is None:  # Only top-level functions
            func_info = self._create_function_info(node, is_method=False)
            self.functions.append(func_info)
        
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node):
        """Visit async function definitions."""
        if self.current_class is None:  # Only top-level functions
            func_info = self._create_function_info(node, is_method=False, is_async=True)
            self.functions.append(func_info)
        
        self.generic_visit(node)
    
    def _create_function_info(self, node, is_method: bool = False, parent_class: Optional[str] = None, is_async: bool = False) -> FunctionInfo:
        """Create FunctionInfo from an AST node."""
        if hasattr(node, 'returns') and isinstance(node, ast.AsyncFunctionDef):
            is_async = True
            
        parameters = []
        for arg in node.args.args:
            parameters.append(arg.arg)
        
        docstring = self._extract_docstring(node)
        decorators = [self._decorator_name(dec) for dec in node.decorator_list]
        
        return FunctionInfo(
            name=node.name,
            line_number=node.lineno,
            is_async=is_async,
            is_method=is_method,
            parent_class=parent_class,
            docstring=docstring,
            parameters=parameters,
            decorators=decorators
        )
    
    def _extract_docstring(self, node) -> Optional[str]:
        """Extract docstring from a function or class node."""
        if (node.body and isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and 
            isinstance(node.body[0].value.value, str)):
            return node.body[0].value.value.strip()
        return None
    
    def _decorator_name(self, decorator) -> str:
        """Get decorator name as string."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return decorator.attr
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
            elif isinstance(decorator.func, ast.Attribute):
                return decorator.func.attr
        return str(decorator)


def main():
    """Main entry point for the project analyzer."""
    parser = argparse.ArgumentParser(description="VysualPy Project Details Generator")
    parser.add_argument("--output", "-o", default="PROJECT_STRUCTURE.md",
                       help="Output markdown file (default: PROJECT_STRUCTURE.md)")
    parser.add_argument("--json", "-j", help="Also save as JSON file")
    parser.add_argument("--dir", "-d", default=".", help="Source directory to analyze")
    
    args = parser.parse_args()
    
    print("Analyzing VysualPy project structure...")
    analyzer = ProjectAnalyzer(args.dir)
    analyzer.analyze_project()
    
    # Generate markdown report
    report = analyzer.generate_markdown_report()
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"Markdown report saved to: {args.output}")
    
    # Save JSON if requested
    if args.json:
        analyzer.save_json(args.json)
        print(f"JSON data saved to: {args.json}")
    
    # Print summary
    total_files = len(analyzer.files_info)
    total_classes = sum(len(info.classes) for info in analyzer.files_info.values())
    total_functions = sum(len(info.functions) for info in analyzer.files_info.values())
    
    print(f"\nAnalysis complete:")
    print(f"- Files analyzed: {total_files}")
    print(f"- Classes found: {total_classes}")
    print(f"- Functions found: {total_functions}")


if __name__ == "__main__":
    main()
