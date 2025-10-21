"""
Merge Optimizer for Boost Modules and Headers

This module provides a class to find optimal merge plans for modules and headers
by calculating the damage of merging each pair.
"""

import argparse
from typing import Dict, List, Tuple
from pathlib import Path
from datetime import datetime


class MergeOptimizer:
    """
    Finds optimal merge plans for modules and headers by minimizing merge damage.
    
    Damage is calculated as the sum of primary_damage and reverse_damage.
    For a pair of items:
    - reverse_damage = reverse_count[item1] + reverse_count[item2] - shared_reverse_count
    - primary_damage = primary_count[item1] + primary_count[item2] - shared_primary_count
    """
    
    def __init__(self, 
                 module_relation: Dict[str, Dict[str, int]] = None,
                 header_relation: Dict[str, Dict[str, int]] = None,
                 module_relation_count: Dict[str, Dict[str, int]] = None,
                 header_relation_count: Dict[str, Dict[str, int]] = None,
                 merge_count: int = 3):
        """
        Initialize the MergeOptimizer.
        
        Args:
            module_relation: Module-to-module relations from BoostDependencyAnalyzer
            header_relation: Header-to-header relations from BoostDependencyAnalyzer
            module_relation_count: Relation counts for modules
            header_relation_count: Relation counts for headers
        """
        self.module_relation = module_relation or {}
        self.header_relation = header_relation or {}
        self.module_relation_count = module_relation_count or {}
        self.header_relation_count = header_relation_count or {}
        
        # Store calculated damages
        self.module_merge_damages: Dict[Tuple[str, ...], Dict[str, int]] = {}
        self.header_merge_damages: Dict[Tuple[str, ...], Dict[str, int]] = {}
        self.merge_count = merge_count
        self.selected_nodes: List[str] = []
        self.candidate_modules: List[str] = []
        self.candidate_headers: List[str] = []
    
    def _count_shared_relations(self, 
                                relation_dict: Dict[str, Dict[str, int]], 
                                item1: str, 
                                item2: str, 
                                target_value: int) -> int:
        """
        Count shared relations between two items for a specific relation value.
        
        Args:
            relation_dict: The relation dictionary (module_relation or header_relation)
            item1: First item name
            item2: Second item name
            target_value: The relation value to count (1 for Primary, -1 for Reverse)
            
        Returns:
            Count of shared relations with the target value
        """
        relations1 = {name for name, val in relation_dict.get(item1, {}).items() if val == target_value}
        relations2 = {name for name, val in relation_dict.get(item2, {}).items() if val == target_value}
        return len(relations1 & relations2)
    
    def _calculate_edge_metrics(self, modules: Tuple[str, ...]) -> Dict[str, int]:
        """
        Calculate edge metrics for a set of modules to be merged.
        
        Args:
            modules: Tuple of module names to merge
            
        Returns:
            Dictionary containing edge metrics:
            - original_edges: Sum of edges from all modules
            - internal_edges: Edges between modules in the merge group
            - merged_edges: Unique edges after merge
            - edge_reduction: Number of edges saved
        """
        original_edges = sum(
            len(self.module_relation.get(mod, {})) for mod in modules
        )
        
        unique_targets = set()
        internal_edges = 0
        
        for mod in modules:
            for target in self.module_relation.get(mod, {}).keys():
                if target in modules:
                    internal_edges += 1
                else:
                    unique_targets.add(target)
        
        merged_edges = len(unique_targets)
        edge_reduction = original_edges - merged_edges
        
        return {
            'original_edges': original_edges,
            'internal_edges': internal_edges,
            'merged_edges': merged_edges,
            'edge_reduction': edge_reduction
        }
    
    def _calculate_overall_impact(self, best_merges: List[Tuple[Tuple[str, ...], Dict[str, int]]]) -> Dict[str, int]:
        """
        Calculate overall impact of all merges.
        
        Args:
            best_merges: List of merge recommendations
            
        Returns:
            Dictionary containing overall statistics
        """
        original_edges = sum(len(deps) for deps in self.module_relation.values())
        reduced_edges = original_edges
        merged_modules = set()
        
        for modules, _ in best_merges:
            metrics = self._calculate_edge_metrics(modules)
            reduced_edges -= metrics['edge_reduction']
            merged_modules.update(modules)
        
        return {
            'original_edges': original_edges,
            'reduced_edges': reduced_edges,
            'edge_reduction': original_edges - reduced_edges,
            'modules_merged': len(merged_modules)
        }
    
    def calculate_merge_damage_for_nodes(self, note_type: str, nodes: List[str]) -> Dict[str, int]:
        """
        Calculate the damage of merging multiple nodes together.
        
        Args:
            note_type: "module" or "header"
            nodes: List of node names to merge
            
        Returns:
            Dictionary with damage metrics
        """
        if note_type == "module":
            relation_dict = self.module_relation
            relation_count = self.module_relation_count
        elif note_type == "header":
            relation_dict = self.header_relation
            relation_count = self.header_relation_count
        else:
            return {}
        
        if len(nodes) == 0:
            return {
                "primary_damage": 0,
                "reverse_damage": 0,
                "total_damage": 0,
                "shared_primary": 0,
                "shared_reverse": 0
            }
        
        # Count total relations for each note_type (with redundancy)
        total_primary_count = 0
        total_reverse_count = 0
        
        # Track relations and how many nodes have them
        primary_relations = {}  # {target: count of nodes that have this relation}
        reverse_relations = {}
        
        for node in nodes:
            count = relation_count.get(node, {})
            total_primary_count += count.get("Primary_level_1", 0)
            total_reverse_count += count.get("Reverse_level_1", 0)
            
            # Track which nodes have which relations
            for target, rel_value in relation_dict.get(node, {}).items():
                if rel_value == 1:  # Primary relation
                    primary_relations[target] = primary_relations.get(target, 0) + 1
                elif rel_value == -1:  # Reverse relation
                    reverse_relations[target] = reverse_relations.get(target, 0) + 1
        
        # Count shared relations (relations that appear in 2+ nodes)
        shared_primary = sum(1 for count in primary_relations.values() if count >= 2)
        shared_reverse = sum(1 for count in reverse_relations.values() if count >= 2)
        
        # Count unique relations (total distinct dependencies)
        unique_primary = len(primary_relations)
        unique_reverse = len(reverse_relations)
        
        # Calculate unshared (redundant) count
        # unshared = total_count (with redundancy) - shared_count
        # This represents how many redundant relations exist
        redundant_primary = total_primary_count - unique_primary
        redundant_reverse = total_reverse_count - unique_reverse
        
        # Calculate unshared unique relations
        unshared_primary_unique = unique_primary - shared_primary
        unshared_reverse_unique = unique_reverse - shared_reverse
        
        # Primary damage: unshared / (shared + 1)
        # More shared dependencies = lower damage
        # More unshared unique dependencies = higher damage
        primary_damage = unshared_primary_unique / (shared_primary + 1)
        reverse_damage = unshared_reverse_unique / (shared_reverse + 1)
        
        total_damage = primary_damage + reverse_damage
        
        return {
            "primary_damage": primary_damage,
            "reverse_damage": reverse_damage,
            "total_damage": total_damage,
            "shared_primary": shared_primary,
            "shared_reverse": shared_reverse,
            "unique_primary": unique_primary,
            "unique_reverse": unique_reverse,
            "unshared_primary": unshared_primary_unique,
            "unshared_reverse": unshared_reverse_unique,
            "redundant_primary": redundant_primary,
            "redundant_reverse": redundant_reverse
        }
        
        
    def calculate_merge_damage(self, note_type: str, depth: int = 1, last_index: int = -1):
        """
        Recursively calculate merge damages for all combinations of nodes.
        
        Args:
            type: "module" or "header"
            depth: Current recursion depth
            last_index: Last index used to avoid duplicates
        """
        nodes = []
        if note_type == "module":
            nodes = self.candidate_modules
        elif note_type == "header":
            nodes = self.candidate_headers
        
        for i in range(last_index + 1, len(nodes)):
            node = nodes[i]
            self.selected_nodes.append(node)
            
            if depth < self.merge_count:
                # Continue recursion to select more nodes
                self.calculate_merge_damage(note_type, depth + 1, i)
            else:
                # Calculate damage for this combination
                damage = self.calculate_merge_damage_for_nodes(note_type, self.selected_nodes)
                # Store with tuple of all selected nodes as key
                node_tuple = tuple(sorted(self.selected_nodes))
                
                if note_type == "module":
                    self.module_merge_damages[node_tuple] = damage
                elif note_type == "header":
                    self.header_merge_damages[node_tuple] = damage
            
            self.selected_nodes.pop()
    
    def calculate_all_module_damages(self) -> Dict[Tuple[str, ...], Dict[str, int]]:
        """
        Calculate merge damages for all combinations of modules.
        
        Returns:
            Dictionary mapping module tuples to their damage metrics
        """
        self.module_merge_damages = {}
        self.candidate_modules = []
        self.selected_nodes = []
        
        # Select candidate modules (those with reverse dependencies)
        for module in self.module_relation.keys():
            if self.module_relation_count[module]["Reverse_level_1"] > 0:
                self.candidate_modules.append(module)
        
        print(f"Found {len(self.candidate_modules)} candidate modules for merging")
        self.calculate_merge_damage(note_type="module", depth=1, last_index=-1)
        
        return self.module_merge_damages
    
    def calculate_all_header_damages(self) -> Dict[Tuple[str, ...], Dict[str, int]]:
        """
        Calculate merge damages for all combinations of headers.
        
        Returns:
            Dictionary mapping header tuples to their damage metrics
        """
        self.header_merge_damages = {}
        self.candidate_headers = []
        self.selected_nodes = []
        
        # Select candidate headers (those with reverse dependencies)
        for header in self.header_relation.keys():
            if self.header_relation_count[header]["Reverse_level_1"] > 0:
                self.candidate_headers.append(header)
        
        print(f"Found {len(self.candidate_headers)} candidate headers for merging")
        self.calculate_merge_damage(note_type="header", depth=1, last_index=-1)
        
        return self.header_merge_damages
    
    def get_best_module_merges(self, top_n: int = 10) -> List[Tuple[Tuple[str, ...], Dict[str, int]]]:
        """
        Get the best module merge candidates sorted by edge reduction.
        
        Args:
            top_n: Number of top candidates to return
            
        Returns:
            List of tuples: ((module1, module2, ...), damage_dict)
        """
        if not self.module_merge_damages:
            self.calculate_all_module_damages()
        
        # Sort by edge reduction (higher reduction = better)
        sorted_merges = sorted(
            self.module_merge_damages.items(),
            key=lambda x: -self._calculate_edge_metrics(x[0])['edge_reduction']
        )
        seen_modules = set()
        final_merges = []
        for group in sorted_merges:
            modules = group[0]
            if any(module in seen_modules for module in modules):
                continue
            seen_modules.update(modules)
            final_merges.append(group)
            if len(final_merges) >= top_n:
                break
        return final_merges
    
    def get_best_header_merges(self, top_n: int = 10) -> List[Tuple[Tuple[str, ...], Dict[str, int]]]:
        """
        Get the best header merge candidates with minimal damage.
        
        Args:
            top_n: Number of top candidates to return
            
        Returns:
            List of tuples: ((header1, header2, ...), damage_dict)
        """
        if not self.header_merge_damages:
            self.calculate_all_header_damages()
        
        sorted_merges = sorted(
            self.header_merge_damages.items(),
            key=lambda x: x[1]["total_damage"]
        )
        
        return sorted_merges[:top_n]
    
    def print_module_merge_recommendations(self, top_n: int = 10):
        """
        Print the best module merge recommendations with detailed metrics.
        
        Args:
            top_n: Number of recommendations to print
        """
        best_merges = self.get_best_module_merges(top_n)
        impact = self._calculate_overall_impact(best_merges)
        
        print("=" * 80)
        print(f"TOP {top_n} MODULE MERGE RECOMMENDATIONS (Sorted by Edge Reduction)")
        print(f"Merge count: {self.merge_count} modules per combination")
        print("=" * 80)
        print()
        print(f"Overall Impact:")
        print(f"  Original total edges: {impact['original_edges']}")
        print(f"  Reduced total edges:  {impact['reduced_edges']}")
        print(f"  Edge reduction:       {impact['edge_reduction']} ({(impact['edge_reduction'] / impact['original_edges'] * 100):.2f}%)")
        print(f"  Modules merged:       {impact['modules_merged']} modules")
        print("=" * 80)
        print()
        
        for i, (modules, damage) in enumerate(best_merges, 1):
            metrics = self._calculate_edge_metrics(modules)
            
            # Simplified console output
            print(f"Rank {i}: {' + '.join(modules)}")
            print(f"  Edges: {metrics['original_edges']} -> {metrics['merged_edges']} (saved {metrics['edge_reduction']}, {(metrics['edge_reduction'] / metrics['original_edges'] * 100):.1f}%)")
            print(f"  Shared: Primary={damage['shared_primary']}, Reverse={damage['shared_reverse']} | Damage={damage['total_damage']:.2f}")
            print()
    
    def export_module_merge_to_markdown(self, output_file: str = "module_merge_recommendations.md", top_n: int = 10):
        """
        Export module merge recommendations to a markdown file.
        
        Args:
            output_file: Path to the output markdown file
            top_n: Number of recommendations to export
        """
        best_merges = self.get_best_module_merges(top_n)
        impact = self._calculate_overall_impact(best_merges)
        
        # Generate markdown content
        md_content = []
        md_content.append(f"# Module Merge Recommendations\n\n")
        md_content.append(f"**Merge Count:** {self.merge_count} modules per combination\n")
        md_content.append(f"**Top Recommendations:** {top_n}\n")
        md_content.append(f"**Sorting:** By Edge Reduction (highest first)\n\n")
        
        md_content.append("## Overall Impact\n")
        md_content.append("| Metric | Value |\n")
        md_content.append("|--------|-------|\n")
        md_content.append(f"| Original total edges | {impact['original_edges']} |\n")
        md_content.append(f"| Reduced total edges | {impact['reduced_edges']} |\n")
        md_content.append(f"| Edge reduction | {impact['edge_reduction']} ({(impact['edge_reduction'] / impact['original_edges'] * 100):.2f}%) |\n")
        md_content.append(f"| Modules merged | {impact['modules_merged']} |\n\n")
        
        md_content.append("---\n\n")
        
        # Add each recommendation
        for i, (modules, damage) in enumerate(best_merges, 1):
            md_content.append(f"## Rank {i}: {' + '.join(modules)}\n\n")
            
            # Calculate edge metrics using helper function
            metrics = self._calculate_edge_metrics(modules)
            
            md_content.append("### Edge Count Impact\n\n")
            md_content.append("| Metric | Value |\n")
            md_content.append("|--------|-------|\n")
            md_content.append(f"| Original edges (sum) | {metrics['original_edges']} |\n")
            md_content.append(f"| Internal edges (removed) | {metrics['internal_edges']} |\n")
            md_content.append(f"| Merged edges (unique) | {metrics['merged_edges']} |\n")
            md_content.append(f"| Edge reduction | {metrics['edge_reduction']} ({(metrics['edge_reduction'] / metrics['original_edges'] * 100):.2f}%) |\n\n")
            
            md_content.append("### Individual Module Details\n\n")
            for mod in modules:
                count = self.module_relation_count.get(mod, {})
                md_content.append(f"**{mod}:**\n")
                md_content.append(f"- Edges from this module: {len(self.module_relation.get(mod, {}))}\n")
                md_content.append(f"- Dependents Relations: Primary = {count.get('Primary_level_1', 0)}, All = {count.get('Primary_total', 0)}\n")
                md_content.append(f"- Dependencies Relations: Primary = {count.get('Reverse_level_1', 0)}, All = {count.get('Reverse_total', 0)}\n\n")
            
            md_content.append("### Summary\n\n")
            md_content.append("After merge, the combined module would have:\n")
            md_content.append(f"- **{metrics['merged_edges']}** total outgoing edges (reduced from {metrics['original_edges']})\n")
            md_content.append(f"- Redundancy saved: {damage['redundant_primary']} Dependents, {damage['redundant_reverse']} Dependencies\n")
            md_content.append(f"- Edges saved: **{metrics['edge_reduction']}** ({(metrics['edge_reduction'] / metrics['original_edges'] * 100):.2f}%)\n\n")
            md_content.append("---\n\n")
        
        # Write to file
        output_path = Path(output_file)
        output_path.write_text(''.join(md_content), encoding='utf-8')
        print(f"Module merge recommendations exported to: {output_path.absolute()}")
        
        return str(output_path.absolute())
    
    def print_header_merge_recommendations(self, top_n: int = 10):
        """
        Print the best header merge recommendations with detailed metrics.
        
        Args:
            top_n: Number of recommendations to print
        """
        best_merges = self.get_best_header_merges(top_n)
        
        print("=" * 80)
        print(f"TOP {top_n} HEADER MERGE RECOMMENDATIONS (Minimal Damage)")
        print(f"Merge count: {self.merge_count} headers per combination")
        print("=" * 80)
        print()
        
        for i, (headers, damage) in enumerate(best_merges, 1):
            print(f"{'='*80}")
            print(f"Rank {i}:")
            for j, hdr in enumerate(headers, 1):
                print(f"  Header {j}: {hdr}")
            print(f"{'='*80}")
            
            # Individual header details
            for hdr in headers:
                count = self.header_relation_count.get(hdr, {})
                short_name = hdr.split('/')[-1] if '/' in hdr else hdr
                print(f"\n  {short_name}:")
                print(f"    Primary Relations:")
                print(f"      - Level 1 (direct):     {count.get('Primary_level_1', 0)}")
                print(f"      - Total (with indirect): {count.get('Primary_total', 0)}")
                print(f"    Reverse Relations:")
                print(f"      - Level 1 (direct):     {count.get('Reverse_level_1', 0)}")
                print(f"      - Total (with indirect): {count.get('Reverse_total', 0)}")
            
            # Shared relations
            print(f"\n  Shared Relations:")
            print(f"    - Primary (overlapping dependencies):  {damage['shared_primary']}")
            print(f"    - Reverse (overlapping dependents):    {damage['shared_reverse']}")
            print(f"    - Unique Primary dependencies:         {damage['unique_primary']}")
            print(f"    - Unique Reverse dependencies:         {damage['unique_reverse']}")
            print(f"    - Unshared Primary:                    {damage['unshared_primary']}")
            print(f"    - Unshared Reverse:                    {damage['unshared_reverse']}")
            print(f"    - Redundant Primary:                   {damage['redundant_primary']}")
            print(f"    - Redundant Reverse:                   {damage['redundant_reverse']}")
            
            # Merge impact
            print(f"\n  Merge Impact:")
            print(f"    - Primary Damage:  {damage['primary_damage']:.2f}")
            print(f"      Formula: unshared_primary / (shared_primary + 1)")
            print(f"      = {damage['unshared_primary']} / ({damage['shared_primary']} + 1)")
            print(f"    - Reverse Damage:  {damage['reverse_damage']:.2f}")
            print(f"      Formula: unshared_reverse / (shared_reverse + 1)")
            print(f"      = {damage['unshared_reverse']} / ({damage['shared_reverse']} + 1)")
            print(f"    - Total Damage:    {damage['total_damage']:.2f}")
            
            # Summary
            print(f"\n  Summary:")
            print(f"    After merge, the combined header would have:")
            print(f"    - {damage['unique_primary']} unique Primary dependencies")
            print(f"    - {damage['unique_reverse']} unique Reverse dependencies")
            print(f"    - Redundancy saved: {damage['redundant_primary']} Primary, {damage['redundant_reverse']} Reverse")
            print()
    
    def get_merge_statistics(self, skip_headers: bool = True) -> Dict[str, int]:
        """
        Get statistics about calculated merges.
        
        Args:
            skip_headers: Whether to skip header merge analysis
            
        Returns:
            Dictionary with statistics
        """
        if not self.module_merge_damages:
            self.calculate_all_module_damages()
        if not skip_headers and not self.header_merge_damages:
            self.calculate_all_header_damages()
        
        return {
            "total_module_combinations": len(self.module_merge_damages),
            "total_header_combinations": len(self.header_merge_damages) if not skip_headers else 0,
            "modules_analyzed": len(self.module_relation),
            "headers_analyzed": len(self.header_relation) if not skip_headers else 0,
        }


def main():
    """
    Main function to run the merge optimizer with command-line arguments.
    
    Arguments:
        --csv: Path to the CSV file (optional, defaults to parent directory)
        --merge-count: Number of modules/headers to merge together (default: 3)
        --top-n: Number of top recommendations to display (default: 10)
        --skip-headers: Skip header merge analysis (faster execution)
    """
    parser = argparse.ArgumentParser(
        description="Find optimal merge candidates for Boost modules and headers"
    )
    parser.add_argument(
        "--csv",
        type=str,
        default=None,
        help="Path to boost_modules_dependencies.csv (default: parent directory)"
    )
    parser.add_argument(
        "--merge-count",
        type=int,
        default=3,
        help="Number of modules/headers to merge together (default: 3)"
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=10,
        help="Number of top recommendations to display (default: 10)"
    )
    parser.add_argument(
        "--skip-headers",
        default=True,
        action="store_true",
        help="Skip header merge analysis (faster execution)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="module_merge_recommendations_3.md",
        help="Output markdown file path (default: module_merge_recommendations.md)"
    )
    
    args = parser.parse_args()
    
    from boost_dependency_analyzer import BoostDependencyAnalyzer
    
    # Load dependency data
    print(f"Loading dependency data from: {args.csv or 'default location'}...")
    analyzer = BoostDependencyAnalyzer(csv_file_path=args.csv)
    analyzer.read_csv()
    print("Data loaded successfully!\n")
    
    # Get relation counts
    print("Calculating relation counts...")
    module_counts = analyzer.count_negative_relations_by_module()
    header_counts = analyzer.count_negative_relations_by_header()
    print("Relation counts calculated!\n")
    
    # Create merge optimizer
    print(f"Creating merge optimizer (merge count: {args.merge_count})...\n")
    optimizer = MergeOptimizer(
        module_relation=analyzer.module_relation,
        header_relation=analyzer.header_relation,
        module_relation_count=module_counts,
        header_relation_count=header_counts,
        merge_count=args.merge_count
    )
    
    # Print statistics
    stats = optimizer.get_merge_statistics(args.skip_headers)
    print("=" * 80)
    print("ANALYSIS STATISTICS")
    print("=" * 80)
    print(f"  Modules analyzed: {stats['modules_analyzed']}")
    print(f"  Headers analyzed: {stats['headers_analyzed']}")
    print(f"  Total module combinations to evaluate: {stats['total_module_combinations']}")
    print(f"  Total header combinations to evaluate: {stats['total_header_combinations']}")
    print("=" * 80)
    print()
    
    # Calculate and print module merge recommendations
    print("Calculating module merge damages...")
    optimizer.print_module_merge_recommendations(args.top_n)
    
    # Export to markdown
    print(f"\nExporting results to markdown file...")
    output_path = optimizer.export_module_merge_to_markdown(args.output, args.top_n)
    print(f"✓ Results saved to: {output_path}\n")
    
    # Calculate and print header merge recommendations
    if not args.skip_headers:
        print("\nCalculating header merge damages (this may take a while)...")
        optimizer.print_header_merge_recommendations(args.top_n)
    else:
        print("Skipping header merge analysis (--skip-headers flag set)")


# Example usage
if __name__ == "__main__":
    main()

