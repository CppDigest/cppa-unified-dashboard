"""
Boost Module Dependency Analyzer

This module provides a class to analyze Boost module dependencies from CSV data.
It creates relation mappings for both module-to-module and header-to-header dependencies.
"""

import csv
from collections import defaultdict
from typing import Dict, DefaultDict
from pathlib import Path


class BoostDependencyAnalyzer:
    """
    Analyzes Boost module dependencies and creates relation data.
    
    Module relation data:
    - Primary operation: relation = 1
    - Reverse operation: relation = -1
    - Both operations exist: relation = 0
    
    Header relation data follows the same logic.
    """
    
    def __init__(self, csv_file_path: str = None):
        """
        Initialize the analyzer.
        
        Args:
            csv_file_path: Path to the boost_modules_dependencies.csv file.
                          If None, defaults to the parent directory.
        """
        if csv_file_path is None:
            # Default to parent directory
            csv_file_path = Path(__file__).parent.parent / "boost_modules_dependencies.csv"
        
        self.csv_file_path = Path(csv_file_path)
        
        # Module relation: module_relation[Module_A][Module_B] = 1/-1/0
        self.module_relation: Dict[str, Dict[str, int]] = {}
        self.module_relation_count: Dict[str, Dict[str, int]] = {}
        
        # Header relation: header_relation[Header_from_Module_B][Header_from_Module_A] = 1/-1/0
        self.header_relation: Dict[str, Dict[str, int]] = {}
        self.header_relation_count: Dict[str, Dict[str, int]] = {}
        
        # Temporary storage for tracking operations
        self._module_operations: DefaultDict[str, DefaultDict[str, set]] = defaultdict(lambda: defaultdict(set))
        self._header_operations: DefaultDict[str, DefaultDict[str, set]] = defaultdict(lambda: defaultdict(set))
    
    def read_csv(self) -> None:
        """
        Read the CSV file and populate relation data structures.
        """
        if not self.csv_file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.csv_file_path}")
        
        with open(self.csv_file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                operation = row['Operation']
                module_a = row['Module_A']  # Source module
                module_b = row['Module_B']  # Dependent module
                sub_header = row['Header']  # Header file path from Module_B
                from_headers = row['From']  # Space-separated header files from Module_A
                
                # Track module operations
                self._module_operations[module_a][module_b].add(operation)
                if operation == "Primary":
                    self._module_operations[module_b][module_a].add("Reverse")
                elif operation == "Reverse":
                    self._module_operations[module_b][module_a].add("Primary")
                
                # Track header operations: relation between headers
                # header_relation[header_b][from_header] based on operation type
                # Primary -> -1, Reverse -> 1
                if sub_header and from_headers:
                    header_list = from_headers.strip().split()
                    for from_header in header_list:
                        if from_header:  # Skip empty strings
                            # Store the operation directly (Primary maps to -1, Reverse maps to 1 later)
                            self._header_operations[sub_header][from_header].add("Reverse")
                            self._header_operations[from_header][sub_header].add("Primary")
        
        # Build final relation data
        self._build_module_relations()
        self._build_header_relations()
        
        # Clear temporary storage
        self._module_operations.clear()
        self._header_operations.clear()
    
    def _build_module_relations(self) -> None:
        """
        Build module relation data based on operations.
        
        Rules:
        - Primary only: 1
        - Reverse only: -1
        - Both Primary and Reverse: 0
        """
        for module_a, targets in self._module_operations.items():
            if module_a not in self.module_relation:
                self.module_relation[module_a] = {}
            
            for module_b, operations in targets.items():
                if 'Primary' in operations and 'Reverse' in operations:
                    # Both operations exist
                    self.module_relation[module_a][module_b] = 0
                elif 'Primary' in operations:
                    # Only Primary
                    self.module_relation[module_a][module_b] = 1
                elif 'Reverse' in operations:
                    # Only Reverse
                    self.module_relation[module_a][module_b] = -1
    
    def _build_header_relations(self) -> None:
        """
        Build header relation data based on operations.
        
        Rules:
        - Primary only: -1
        - Reverse only: 1
        - Both Primary and Reverse: 0
        """
        for header, targets in self._header_operations.items():
            if header not in self.header_relation:
                self.header_relation[header] = {}
            
            for target_header, operations in targets.items():
                if 'Primary' in operations and 'Reverse' in operations:
                    # Both operations exist
                    self.header_relation[header][target_header] = 0
                elif 'Primary' in operations:
                    # Only Primary: -1
                    self.header_relation[header][target_header] = -1
                elif 'Reverse' in operations:
                    # Only Reverse: 1
                    self.header_relation[header][target_header] = 1
    
    def get_module_relation(self, module_a: str, module_b: str) -> int:
        """
        Get the relation value between two modules.
        
        Args:
            module_a: The first module
            module_b: The second module
            
        Returns:
            1 for Primary, -1 for Reverse, 0 for both, None if no relation exists
        """
        return self.module_relation.get(module_a, {}).get(module_b, None)
    
    def get_header_relation(self, header_b: str, header_a: str) -> int:
        """
        Get the relation value between two headers.
        
        Args:
            header_b: The header file from Module_B (first key)
            header_a: The header file from Module_A (second key)
            
        Returns:
            1 for Primary, -1 for Reverse, 0 for both, None if no relation exists
        """
        return self.header_relation.get(header_b, {}).get(header_a, None)
    
    def get_module_dependencies(self, module_name: str) -> Dict[str, int]:
        """
        Get all dependencies for a specific module.
        
        Args:
            module_name: The module name
            
        Returns:
            Dictionary mapping dependent modules to their relation values
        """
        return self.module_relation.get(module_name, {})
    
    def get_header_dependencies(self, header_name: str) -> Dict[str, int]:
        """
        Get all header dependencies for a specific header.
        
        Args:
            header_name: The header file name (from Module_B)
            
        Returns:
            Dictionary mapping related headers (from Module_A) to their relation values
        """
        return self.header_relation.get(header_name, {})
    
    def get_all_modules(self) -> list:
        """
        Get a list of all modules that have dependencies.
        
        Returns:
            List of module names
        """
        return list(self.module_relation.keys())
    
    def get_all_headers(self) -> list:
        """
        Get a list of all headers that have relations with other headers.
        
        Returns:
            List of header file names (from Module_B in the CSV)
        """
        return list(self.header_relation.keys())
    
    def _count_transitive_relations(self, relation_dict: Dict[str, Dict[str, int]], 
                                    source: str, target_value: int) -> int:
        """
        Helper method to count transitive relations using BFS.
        
        Args:
            relation_dict: The relation dictionary (module_relation or header_relation)
            source: The source item to start from
            target_value: The relation value to count (1 for Primary, -1 for Reverse)
            
        Returns:
            Count of transitive relations
        """
        initial_deps = relation_dict.get(source, {})
        relation_list = [name for name, rel_value in initial_deps.items() if rel_value == target_value]
        seen_items = set(relation_list)
        count = 0
        
        while relation_list:
            next_item = relation_list.pop(0)
            for item_name, rel_value in relation_dict.get(next_item, {}).items():
                if rel_value == target_value and item_name not in seen_items:
                    count += 1
                    relation_list.append(item_name)
                    seen_items.add(item_name)
        
        return count
    
    def count_negative_relations_by_module(self) -> Dict[str, Dict[str, int]]:
        """
        Count the number of relations with value = -1 and 1 for each module.
        
        Returns:
            Dictionary mapping module names to their count of relations
        """
        self.module_relation_count = {}
        
        # Initialize counts for all modules
        for mod_name, mod_deps in self.module_relation.items():
            primary_level_1 = sum(1 for rel_value in mod_deps.values() if rel_value == 1)
            reverse_level_1 = sum(1 for rel_value in mod_deps.values() if rel_value == -1)
            
            self.module_relation_count[mod_name] = {
                "Primary_level_1": primary_level_1,
                "Primary_total": primary_level_1,
                "Reverse_level_1": reverse_level_1,
                "Reverse_total": reverse_level_1
            }
        
        # Calculate transitive counts
        for mod_name in self.module_relation:
            self.module_relation_count[mod_name]["Primary_total"] += \
                self._count_transitive_relations(self.module_relation, mod_name, 1)
            self.module_relation_count[mod_name]["Reverse_total"] += \
                self._count_transitive_relations(self.module_relation, mod_name, -1)
        
        return self.module_relation_count
    
    def count_negative_relations_by_header(self) -> Dict[str, Dict[str, int]]:
        """
        Count the number of relations with value = -1 and 1 for each header.
        
        Returns:
            Dictionary mapping header names to their count of relations (level_1 and total)
        """
        self.header_relation_count = {}
        
        # Initialize counts for all headers
        for hdr_name, hdr_deps in self.header_relation.items():
            primary_level_1 = sum(1 for rel_value in hdr_deps.values() if rel_value == 1)
            reverse_level_1 = sum(1 for rel_value in hdr_deps.values() if rel_value == -1)
            
            self.header_relation_count[hdr_name] = {
                "Primary_level_1": primary_level_1,
                "Primary_total": primary_level_1,
                "Reverse_level_1": reverse_level_1,
                "Reverse_total": reverse_level_1
            }
        
        # Calculate transitive counts
        for hdr_name in self.header_relation:
            self.header_relation_count[hdr_name]["Primary_total"] += \
                self._count_transitive_relations(self.header_relation, hdr_name, 1)
            self.header_relation_count[hdr_name]["Reverse_total"] += \
                self._count_transitive_relations(self.header_relation, hdr_name, -1)
        
        return self.header_relation_count
    
    def print_module_statistics(self) -> None:
        """
        Print statistics about module relations.
        """
        total_modules = len(self.module_relation)
        total_relations = sum(len(deps) for deps in self.module_relation.values())
        
        primary_count = 0
        reverse_count = 0
        both_count = 0
        
        for module_deps in self.module_relation.values():
            for rel_value in module_deps.values():
                if rel_value == 1:
                    primary_count += 1
                elif rel_value == -1:
                    reverse_count += 1
                elif rel_value == 0:
                    both_count += 1
        
        print("=" * 60)
        print("MODULE RELATION STATISTICS")
        print("=" * 60)
        print(f"Total modules with dependencies: {total_modules}")
        print(f"Total module relations: {total_relations}")
        print(f"  - Primary only (1): {primary_count}")
        print(f"  - Reverse only (-1): {reverse_count}")
        print(f"  - Both operations (0): {both_count}")
        print("=" * 60)
    
    def print_header_statistics(self) -> None:
        """
        Print statistics about header-to-header relations.
        """
        total_headers = len(self.header_relation)
        total_relations = sum(len(deps) for deps in self.header_relation.values())
        
        primary_count = 0
        reverse_count = 0
        both_count = 0
        
        for h_deps in self.header_relation.values():
            for rel_value in h_deps.values():
                if rel_value == 1:
                    primary_count += 1
                elif rel_value == -1:
                    reverse_count += 1
                elif rel_value == 0:
                    both_count += 1
        
        print("=" * 60)
        print("HEADER RELATION STATISTICS")
        print("=" * 60)
        print(f"Total headers with relations: {total_headers}")
        print(f"Total header-to-header relations: {total_relations}")
        print(f"  - Reverse only (1): {primary_count}")
        print(f"  - Primary only (-1): {reverse_count}")
        print(f"  - Both operations (0): {both_count}")
        print("=" * 60)


def run_basic_statistics(analyzer: BoostDependencyAnalyzer) -> None:
    """
    Print basic module and header statistics.
    
    This function outputs:
    - Total number of modules and their dependencies
    - Count of Primary (1), Reverse (-1), and Both (0) relations for modules
    - Total number of headers and their relations
    - Count of Primary (-1), Reverse (1), and Both (0) relations for headers
    
    Args:
        analyzer: BoostDependencyAnalyzer instance with loaded data
    """
    # Display module-level statistics
    analyzer.print_module_statistics()
    print()
    
    # Display header-level statistics
    analyzer.print_header_statistics()
    print()


def run_example_queries(analyzer: BoostDependencyAnalyzer) -> None:
    """
    Run example queries to demonstrate analyzer capabilities.
    
    This function demonstrates three types of queries:
    1. Check relation between two specific modules
    2. Get all dependencies for a specific module
    3. Query header-to-header relations and their types
    
    Args:
        analyzer: BoostDependencyAnalyzer instance with loaded data
    """
    print("=" * 60)
    print("EXAMPLE QUERIES")
    print("=" * 60)
    
    # Example 1: Check specific module relation
    # This shows how to query if one module depends on another
    relation = analyzer.get_module_relation("accumulators", "array")
    if relation is not None:
        print(f"Module relation: accumulators -> array = {relation}")
    
    # Example 2: Get all dependencies for a module
    # This retrieves all modules that "accumulators" depends on
    deps = analyzer.get_module_dependencies("accumulators")
    print(f"\nAccumulators has {len(deps)} dependencies")
    print("First 10 dependencies:")
    for module, rel in list(deps.items())[:10]:
        print(f"  {module}: {rel}")
    
    # Example 3: Check header-to-header relations
    # This shows dependencies between individual header files
    header_deps = analyzer.get_header_dependencies("boost/mpl/contains.hpp")
    if header_deps:
        print(f"\nHeader 'boost/mpl/contains.hpp' has {len(header_deps)} header relations")
        print("First 5 header relations:")
        for other_header, rel in list(header_deps.items())[:5]:
            # Convert numeric relation to readable string
            rel_str = "Primary" if rel == 1 else "Reverse" if rel == -1 else "Both"
            print(f"  {other_header}: {rel} ({rel_str})")


def print_sorted_module_stats(module_counts: Dict[str, Dict[str, int]], top_n: int = 10) -> None:
    """
    Print sorted module statistics by Primary and Reverse relations.
    
    This function displays the top N modules sorted by:
    1. Primary relations (total) - includes transitive dependencies
    2. Primary relations (level_1) - direct dependencies only
    3. Reverse relations (total) - includes transitive dependencies
    4. Reverse relations (level_1) - direct dependencies only
    
    Args:
        module_counts: Module relation counts dictionary from count_negative_relations_by_module()
                       Structure: {module_name: {Primary_level_1, Primary_total, 
                                                  Reverse_level_1, Reverse_total}}
        top_n: Number of top modules to display for each category (default: 10)
    """
    # Print modules with most Primary relations (by total)
    # Total includes both direct and transitive dependencies
    print("\nModules with most Primary relations (by total):")
    sorted_modules = sorted(module_counts.items(), key=lambda x: x[1]["Primary_total"], reverse=True)
    for module_name, count_dict in sorted_modules[:top_n]:
        print(f"  {module_name}: Primary(level_1={count_dict['Primary_level_1']}, "
              f"total={count_dict['Primary_total']}), "
              f"Reverse(level_1={count_dict['Reverse_level_1']}, "
              f"total={count_dict['Reverse_total']})")
    
    # Print modules with most Primary relations (by level_1)
    # Level_1 shows only direct dependencies (no transitive)
    print("\nModules with most Primary relations (by level_1):")
    sorted_modules = sorted(module_counts.items(), key=lambda x: x[1]["Primary_level_1"], reverse=True)
    for module_name, count_dict in sorted_modules[:top_n]:
        print(f"  {module_name}: Primary(level_1={count_dict['Primary_level_1']}, "
              f"total={count_dict['Primary_total']}), "
              f"Reverse(level_1={count_dict['Reverse_level_1']}, "
              f"total={count_dict['Reverse_total']})")
    
    # Print modules with most Reverse relations (by total)
    # Reverse relations indicate other modules that depend on this module
    print("\nModules with most Reverse relations (by total):")
    sorted_modules = sorted(module_counts.items(), key=lambda x: x[1]["Reverse_total"], reverse=True)
    for module_name, count_dict in sorted_modules[:top_n]:
        print(f"  {module_name}: Primary(level_1={count_dict['Primary_level_1']}, "
              f"total={count_dict['Primary_total']}), "
              f"Reverse(level_1={count_dict['Reverse_level_1']}, "
              f"total={count_dict['Reverse_total']})")
    
    # Print modules with most Reverse relations (by level_1)
    # Direct reverse dependencies only (no transitive)
    print("\nModules with most Reverse relations (by level_1):")
    sorted_modules = sorted(module_counts.items(), key=lambda x: x[1]["Reverse_level_1"], reverse=True)
    for module_name, count_dict in sorted_modules[:top_n]:
        print(f"  {module_name}: Primary(level_1={count_dict['Primary_level_1']}, "
              f"total={count_dict['Primary_total']}), "
              f"Reverse(level_1={count_dict['Reverse_level_1']}, "
              f"total={count_dict['Reverse_total']})")


def print_sorted_header_stats(header_counts: Dict[str, Dict[str, int]], top_n: int = 10) -> None:
    """
    Print sorted header statistics by Primary and Reverse relations.
    
    This function displays the top N headers sorted by:
    1. Primary relations (total) - includes transitive dependencies
    2. Reverse relations (total) - includes transitive dependencies
    
    Note: For headers, Primary (1) means the header depends on others,
          and Reverse (-1) means others depend on this header.
    
    Args:
        header_counts: Header relation counts dictionary from count_negative_relations_by_header()
                       Structure: {header_name: {Primary_level_1, Primary_total, 
                                                  Reverse_level_1, Reverse_total}}
        top_n: Number of top headers to display for each category (default: 10)
    """
    # Print headers with most Primary relations (by total)
    # These headers have the most dependencies on other headers
    print("\nHeaders with most Primary relations (by total):")
    sorted_headers = sorted(header_counts.items(), key=lambda x: x[1]["Primary_total"], reverse=True)
    for header_name, count_dict in sorted_headers[:top_n]:
        print(f"  {header_name}: Primary(level_1={count_dict['Primary_level_1']}, "
              f"total={count_dict['Primary_total']}), "
              f"Reverse(level_1={count_dict['Reverse_level_1']}, "
              f"total={count_dict['Reverse_total']})")
    
    # Print headers with most Reverse relations (by total)
    # These headers are most depended upon by other headers
    print("\nHeaders with most Reverse relations (by total):")
    sorted_headers = sorted(header_counts.items(), key=lambda x: x[1]["Reverse_total"], reverse=True)
    for header_name, count_dict in sorted_headers[:top_n]:
        print(f"  {header_name}: Primary(level_1={count_dict['Primary_level_1']}, "
              f"total={count_dict['Primary_total']}), "
              f"Reverse(level_1={count_dict['Reverse_level_1']}, "
              f"total={count_dict['Reverse_total']})")


def generate_statistics_report(analyzer: BoostDependencyAnalyzer, output_file: str = "boost_dependency_report.md") -> str:
    """
    Generate a comprehensive statistics report and save it to a markdown file.
    
    Args:
        analyzer: BoostDependencyAnalyzer instance with loaded data
        output_file: Path to the output markdown file
        
    Returns:
        Path to the generated report file
    """
    from pathlib import Path
    from datetime import datetime
    
    # Calculate statistics
    module_counts = analyzer.count_negative_relations_by_module()
    header_counts = analyzer.count_negative_relations_by_header()
    
    # Generate report content
    md_content = []
    md_content.append(f"# Boost Dependency Analysis Report\n\n")
    md_content.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    # Overall statistics
    total_modules = len(analyzer.module_relation)
    total_module_relations = sum(len(deps) for deps in analyzer.module_relation.values())
    total_headers = len(analyzer.header_relation)
    total_header_relations = sum(len(deps) for deps in analyzer.header_relation.values())
    
    # Count relation types for modules
    module_primary = sum(1 for deps in analyzer.module_relation.values() 
                         for val in deps.values() if val == 1)
    module_reverse = sum(1 for deps in analyzer.module_relation.values() 
                         for val in deps.values() if val == -1)
    module_both = sum(1 for deps in analyzer.module_relation.values() 
                      for val in deps.values() if val == 0)
    
    # Count relation types for headers
    header_primary = sum(1 for deps in analyzer.header_relation.values() 
                         for val in deps.values() if val == 1)
    header_reverse = sum(1 for deps in analyzer.header_relation.values() 
                         for val in deps.values() if val == -1)
    header_both = sum(1 for deps in analyzer.header_relation.values() 
                      for val in deps.values() if val == 0)
    
    md_content.append("## Overall Statistics\n\n")
    md_content.append("### Module Relations\n\n")
    md_content.append("| Metric | Value |\n")
    md_content.append("|--------|-------|\n")
    md_content.append(f"| Total modules | {total_modules} |\n")
    md_content.append(f"| Total module relations | {total_module_relations} |\n")
    md_content.append(f"| Primary Dependents | {module_primary} |\n")
    md_content.append(f"| Primary Dependencies | {module_reverse} |\n")
    md_content.append(f"| Both operations (0) | {module_both} |\n\n")
    
    md_content.append("### Header Relations\n\n")
    md_content.append("| Metric | Value |\n")
    md_content.append("|--------|-------|\n")
    md_content.append(f"| Total headers | {total_headers} |\n")
    md_content.append(f"| Total header relations | {total_header_relations} |\n")
    md_content.append(f"| Primary Dependencies | {header_primary} |\n")
    md_content.append(f"| Reverse Dependents | {header_reverse} |\n")
    md_content.append(f"| Both operations (0) | {header_both} |\n\n")
    
    # Top modules by Primary relations
    md_content.append("## Top Modules by All Dependents\n\n")
    sorted_modules = sorted(module_counts.items(), key=lambda x: x[1]["Primary_total"], reverse=True)
    md_content.append("| Rank | Module | Primary Dependents | All Dependents | Primary Dependencies | All Dependencies |\n")
    md_content.append("|------|--------|-------------------|-----------------|-------------------|------------------|\n")
    for i, (mod, counts) in enumerate(sorted_modules[:20], 1):
        md_content.append(f"| {i} | {mod} | {counts['Primary_level_1']} | {counts['Primary_total']} | {counts['Reverse_level_1']} | {counts['Reverse_total']} |\n")
    md_content.append("\n")
    
    # Top modules by Primary relations
    md_content.append("## Top Modules by Primary Dependents \n\n")
    sorted_modules = sorted(module_counts.items(), key=lambda x: x[1]["Primary_level_1"], reverse=True)
    md_content.append("| Rank | Module | Primary Dependents | All Dependents | Primary Dependencies | All Dependencies |\n")
    md_content.append("|------|--------|-------------------|-----------------|-------------------|------------------|\n")
    for i, (mod, counts) in enumerate(sorted_modules[:20], 1):
        md_content.append(f"| {i} | {mod} | {counts['Primary_level_1']} | {counts['Primary_total']} | {counts['Reverse_level_1']} | {counts['Reverse_total']} |\n")
    md_content.append("\n")
    
    
    # Top modules by Reverse relations
    md_content.append("## Top Modules by All Dependencies\n\n")
    sorted_modules = sorted(module_counts.items(), key=lambda x: x[1]["Reverse_total"], reverse=True)
    md_content.append("| Rank | Module | Primary Dependents | All Dependents | Primary Dependencies | All Dependencies |\n")
    md_content.append("|------|--------|-------------------|-----------------|-------------------|------------------|\n")
    for i, (mod, counts) in enumerate(sorted_modules[:20], 1):
        md_content.append(f"| {i} | {mod} | {counts['Primary_level_1']} | {counts['Primary_total']} | {counts['Reverse_level_1']} | {counts['Reverse_total']} |\n")
    md_content.append("\n")
    
    # Top modules by Reverse relations
    md_content.append("## Top Modules by Primary Dependencies\n\n")
    sorted_modules = sorted(module_counts.items(), key=lambda x: x[1]["Reverse_level_1"], reverse=True)
    md_content.append("| Rank | Module | Primary Dependents | All Dependents | Primary Dependencies | All Dependencies |\n")
    md_content.append("|------|--------|-------------------|-----------------|-------------------|------------------|\n")
    for i, (mod, counts) in enumerate(sorted_modules[:20], 1):
        md_content.append(f"| {i} | {mod} | {counts['Primary_level_1']} | {counts['Primary_total']} | {counts['Reverse_level_1']} | {counts['Reverse_total']} |\n")
    md_content.append("\n")
    
    
    # Top headers by Primary relations
    md_content.append("## Top Headers by All Dependents\n\n")
    sorted_headers = sorted(header_counts.items(), key=lambda x: x[1]["Primary_total"], reverse=True)
    md_content.append("| Rank | Header | Primary Dependents | All Dependents | Primary Dependencies | All Dependencies |\n")
    md_content.append("|------|--------|-------------------|-----------------|-------------------|------------------|\n")
    for i, (hdr, counts) in enumerate(sorted_headers[:20], 1):
        md_content.append(f"| {i} | {hdr} | {counts['Primary_level_1']} | {counts['Primary_total']} | {counts['Reverse_level_1']} | {counts['Reverse_total']} |\n")
    md_content.append("\n")
    
    # Top headers by Reverse relations
    md_content.append("## Top Headers by All Dependencies\n\n")
    sorted_headers = sorted(header_counts.items(), key=lambda x: x[1]["Reverse_total"], reverse=True)
    md_content.append("| Rank | Header | Primary Dependents | All Dependents | Primary Dependencies | All Dependencies |\n")
    md_content.append("|------|--------|-------------------|-----------------|-------------------|------------------|\n")
    for i, (hdr, counts) in enumerate(sorted_headers[:20], 1):
        md_content.append(f"| {i} | {hdr} | {counts['Primary_level_1']} | {counts['Primary_total']} | {counts['Reverse_level_1']} | {counts['Reverse_total']} |\n")
    md_content.append("\n")
    
    # Module dependency distribution
    md_content.append("## Module Dependency Distribution\n\n")
    primary_dist = {}
    reverse_dist = {}
    for counts in module_counts.values():
        p_count = counts['Primary_level_1']
        r_count = counts['Reverse_level_1']
        primary_dist[p_count] = primary_dist.get(p_count, 0) + 1
        reverse_dist[r_count] = reverse_dist.get(r_count, 0) + 1
    
    md_content.append("### Primary Dependents Distribution\n\n")
    md_content.append("| Dependents | Number of Modules |\n")
    md_content.append("|--------------|-------------------|\n")
    for count in sorted(primary_dist.keys(), reverse=True)[:15]:
        md_content.append(f"| {count} | {primary_dist[count]} |\n")
    md_content.append("\n")
    
    md_content.append("### Primary Dependencies Distribution\n\n")
    md_content.append("| Dependencies | Number of Modules |\n")
    md_content.append("|--------------|-------------------|\n")
    for count in sorted(reverse_dist.keys(), reverse=True)[:15]:
        md_content.append(f"| {count} | {reverse_dist[count]} |\n")
    md_content.append("\n")
    
    # Write to file
    output_path = Path(output_file)
    output_path.write_text(''.join(md_content), encoding='utf-8')
    print(f"Statistics report exported to: {output_path.absolute()}")
    
    return str(output_path.absolute())


def run_relation_analysis(analyzer: BoostDependencyAnalyzer) -> None:
    """
    Run detailed relation analysis for modules and headers.
    
    This function performs comprehensive analysis of dependencies by:
    1. Counting Primary and Reverse relations for each module
       - Primary: modules this module depends on
       - Reverse: modules that depend on this module
    2. Counting Primary and Reverse relations for each header
    3. Displaying top modules/headers sorted by various metrics
    
    Both direct (level_1) and transitive (total) counts are calculated,
    where transitive counts include all reachable dependencies via BFS.
    
    Args:
        analyzer: BoostDependencyAnalyzer instance with loaded data
    """
    print("\n" + "=" * 60)
    print("NEGATIVE RELATION COUNTS (value = -1)")
    print("=" * 60)
    
    # Analyze module relations
    # This calculates both direct and transitive dependency counts
    module_counts = analyzer.count_negative_relations_by_module()
    print_sorted_module_stats(module_counts)
    
    print("=" * 60)
    
    # Analyze header relations
    # Similar to modules but at the header file granularity
    header_counts = analyzer.count_negative_relations_by_header()
    print_sorted_header_stats(header_counts)
    
    print("=" * 60)


def main() -> None:
    """
    Main function to run the Boost dependency analysis.
    
    This function orchestrates the complete analysis workflow:
    1. Loads and parses boost_modules_dependencies.csv
    2. Displays basic statistics about module and header relations
    3. Demonstrates example queries for common use cases
    4. Performs detailed relation analysis with sorted results
    5. Generates a comprehensive statistics report in markdown format
    
    The analysis provides insights into:
    - Module-to-module dependency patterns
    - Header-to-header dependency patterns
    - Direct vs. transitive dependencies
    - Most dependent and most depended-upon components
    
    Output is organized into clear sections with visual separators
    for easy reading and interpretation.
    """
    # Step 1: Initialize and load data
    # Create analyzer instance and read CSV file
    print("Reading boost_modules_dependencies.csv...")
    analyzer = BoostDependencyAnalyzer()
    analyzer.read_csv()
    print("CSV file processed successfully!\n")
    
    # Step 2: Run analysis sections in logical order
    # Each section provides different insights into the dependency structure
    run_basic_statistics(analyzer)     # Overview statistics
    run_example_queries(analyzer)      # Example usage demonstrations
    run_relation_analysis(analyzer)    # Detailed analysis and rankings
    
    # Step 3: Generate statistics report
    print("\nGenerating statistics report...")
    generate_statistics_report(analyzer, "boost_dependency_report.md")


# Example usage
if __name__ == "__main__":
    main()

