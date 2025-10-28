"""
Merge Module Optimizer for Boost Modules

This module provides a class to find optimal merge plans for modules
by calculating the damage of merging each pair.
"""

import argparse
from typing import Dict, List, Tuple
from pathlib import Path


class MergeModuleOptimizer:
    """
    Finds optimal merge plans for modules by minimizing merge damage.
    
    Damage is calculated as the sum of primary_damage and reverse_damage.
    For a pair of modules:
    - reverse_damage = reverse_count[module1] + reverse_count[module2] - shared_reverse_count
    - primary_damage = primary_count[module1] + primary_count[module2] - shared_primary_count
    """
    
    def __init__(self, 
                 module_relation: Dict[str, Dict[str, int]] = None,
                 module_relation_count: Dict[str, Dict[str, int]] = None,
                 merge_count: int = 3):
        """
        Initialize the MergeModuleOptimizer.
        
        Args:
            module_relation: Module-to-module relations from BoostDependencyAnalyzer
            module_relation_count: Relation counts for modules
            merge_count: Number of modules to merge together (default: 3)
        """
        self.module_relation = module_relation or {}
        self.module_relation_count = module_relation_count or {}
        
        # Store calculated damages (now includes merge_count in key)
        self.module_merge_damages: Dict[Tuple[str, ...], Dict[str, int]] = {}
        self.merge_count = merge_count
        self.selected_nodes: List[str] = []
        self.candidate_modules: List[str] = []
        self.current_merge_count: int = merge_count
    
    def _count_shared_relations(self, 
                                relation_dict: Dict[str, Dict[str, int]], 
                                module1: str, 
                                module2: str, 
                                target_value: int) -> int:
        """
        Count shared relations between two modules for a specific relation value.
        
        Args:
            relation_dict: The relation dictionary (module_relation)
            module1: First module name
            module2: Second module name
            target_value: The relation value to count (1 for Primary, -1 for Reverse)
            
        Returns:
            Count of shared relations with the target value
        """
        relations1 = {name for name, val in relation_dict.get(module1, {}).items() if val == target_value}
        relations2 = {name for name, val in relation_dict.get(module2, {}).items() if val == target_value}
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
            'internal_edges': int(internal_edges / 2),
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
    
    def calculate_merge_damage_for_modules(self, modules: List[str]) -> Dict[str, int]:
        """
        Calculate the damage of merging multiple modules together.
        
        Args:
            modules: List of module names to merge
            
        Returns:
            Dictionary with damage metrics
        """
        if len(modules) == 0:
            return {
                "primary_damage": 0,
                "reverse_damage": 0,
                "total_damage": 0,
                "shared_primary": 0,
                "shared_reverse": 0
            }
        
        # Count total relations for each module (with redundancy)
        total_primary_count = 0
        total_reverse_count = 0
        
        # Track relations and how many modules have them
        primary_relations = {}  # {target: count of modules that have this relation}
        reverse_relations = {}
        
        for module in modules:
            count = self.module_relation_count.get(module, {})
            total_primary_count += count.get("Primary_level_1", 0)
            total_reverse_count += count.get("Reverse_level_1", 0)
            
            # Track which modules have which relations
            for target, rel_value in self.module_relation.get(module, {}).items():
                if rel_value == 1:  # Primary relation
                    primary_relations[target] = primary_relations.get(target, 0) + 1
                elif rel_value == -1:  # Reverse relation
                    reverse_relations[target] = reverse_relations.get(target, 0) + 1
        
        # Count shared relations (relations that appear in 2+ modules)
        shared_primary = sum(1 for count in primary_relations.values() if count >= 2)
        shared_reverse = sum(1 for count in reverse_relations.values() if count >= 2)
        
        # Count unique relations (total distinct dependencies)
        unique_primary = len(primary_relations)
        unique_reverse = len(reverse_relations)
        
        # Calculate redundant count
        # redundant = total_count (with redundancy) - unique_count
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
        
    def calculate_merge_damage(self, depth: int = 1, last_index: int = -1):
        """
        Recursively calculate merge damages for all combinations of modules.
        
        Args:
            depth: Current recursion depth
            last_index: Last index used to avoid duplicates
        """
        modules = self.candidate_modules
        
        for i in range(last_index + 1, len(modules)):
            module = modules[i]
            self.selected_nodes.append(module)
            
            if depth < self.current_merge_count:
                # Continue recursion to select more modules
                self.calculate_merge_damage(depth + 1, i)
            else:
                # Calculate damage for this combination
                damage = self.calculate_merge_damage_for_modules(self.selected_nodes)
                # Store with tuple of all selected modules as key
                module_tuple = tuple(sorted(self.selected_nodes))
                self.module_merge_damages[module_tuple] = damage
            
            self.selected_nodes.pop()
    
    def calculate_all_module_damages(self, merge_count_range: Tuple[int, int] = None, candidate_count: int = 30) -> Dict[Tuple[str, ...], Dict[str, int]]:
        """
        Calculate merge damages for all combinations of modules across multiple merge counts.
        
        Args:
            merge_count_range: Tuple of (min_merge_count, max_merge_count). 
                             If None, uses self.merge_count only.
        
        Returns:
            Dictionary mapping module tuples to their damage metrics
        """
        self.module_merge_damages = {}
        self.candidate_modules = []
        self.selected_nodes = []
        
        # Select top 20 modules by Reverse_level_1 count (most dependents)
        modules_with_reverse = []
        for module in self.module_relation.keys():
            reverse_count = self.module_relation_count[module]["Reverse_level_1"]
            if reverse_count > 0:
                modules_with_reverse.append((module, reverse_count))
        
        # Sort by reverse count (descending) and take top 20
        modules_with_reverse.sort(key=lambda x: x[1], reverse=True)
        self.candidate_modules = [module for module, _ in modules_with_reverse[:candidate_count]]
        
        print(f"Selected top {candidate_count} candidate modules for merging (by Reverse_level_1 count)")
        print(f"Top candidates: {', '.join(self.candidate_modules[:5])}...")
        
        # Calculate damages for each merge count in range
        if merge_count_range:
            min_count, max_count = merge_count_range
            print(f"\nCalculating merge strategies for merge counts {min_count} to {max_count}...")
            
            for count in range(min_count, max_count + 1):
                self.current_merge_count = count
                self.selected_nodes = []
                print(f"  Processing merge count {count}...")
                self.calculate_merge_damage(depth=1, last_index=-1)
            
            print(f"\nTotal strategies found: {len(self.module_merge_damages)}")
        else:
            # Single merge count (backward compatibility)
            self.current_merge_count = self.merge_count
            self.calculate_merge_damage(depth=1, last_index=-1)
        
        return self.module_merge_damages
    
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
        # sorted_merges = sorted(
        #     self.module_merge_damages.items(),
        #     key=lambda x: -x[1]['total_damage']
        # )
        seen_modules = set()
        final_merges = []
        count_limit = int(top_n / 4) + 1
        count_per_merge_count = {}
        
        for group in sorted_merges:
            modules = group[0]
            merge_count = len(modules)
            if merge_count not in count_per_merge_count:
                count_per_merge_count[merge_count] = 0
            elif count_per_merge_count[merge_count] >= top_n:
                continue
            
            # if any(module in seen_modules for module in modules):
            #     continue
            seen_modules.update(modules)
            final_merges.append(group)
            count_per_merge_count[merge_count] += 1
            # if len(final_merges) >= top_n:
                # break
        return final_merges
    
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
        print("=" * 80)
        print()
        print("Overall Impact:")
        print(f"  Original total edges: {impact['original_edges']}")
        print(f"  Reduced total edges:  {impact['reduced_edges']}")
        print(f"  Edge reduction:       {impact['edge_reduction']}")
        print(f"  Modules merged:       {impact['modules_merged']} modules")
        print("=" * 80)
        print()
        
        for i, (modules, damage) in enumerate(best_merges, 1):
            metrics = self._calculate_edge_metrics(modules)
            merge_count = len(modules)
            
            # Simplified console output
            print(f"Rank {i}: {' + '.join(modules)} (merge count: {merge_count})")
            print(f"  Edges: {metrics['original_edges']} -> {metrics['merged_edges']} (saved {metrics['edge_reduction']})")
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
        md_content.append("# Module Merge Recommendations\n\n")
        md_content.append(f"**Top Recommendations:** {top_n}\n")
        md_content.append("**Sorting:** By Edge Reduction (highest first)\n")
        md_content.append("**Strategy:** Best merges across all merge counts (2-5 modules)\n\n")
        
        # md_content.append("## Overall Impact\n")
        # md_content.append("| Metric | Value |\n")
        # md_content.append("|--------|-------|\n")
        # md_content.append(f"| Original total edges | {impact['original_edges']} |\n")
        # md_content.append(f"| Reduced total edges | {impact['reduced_edges']} |\n")
        # md_content.append(f"| Edge reduction | {impact['edge_reduction']} |\n")
        # md_content.append(f"| Modules merged | {impact['modules_merged']} |\n\n")
        
        md_content.append("---\n\n")
        
        # Add each recommendation
        for i, (modules, damage) in enumerate(best_merges, 1):
            merge_count = len(modules)
            md_content.append(f"## Rank {i}: {' + '.join(modules)}\n\n")
            md_content.append(f"**Merge Count:** {merge_count} modules\n\n")
            
            # Calculate edge metrics using helper function
            metrics = self._calculate_edge_metrics(modules)
            
            md_content.append("### Edge Count Impact\n\n")
            md_content.append("| Metric | Value |\n")
            md_content.append("|--------|-------|\n")
            md_content.append(f"| Original edges (sum) | {metrics['original_edges']} |\n")
            md_content.append(f"| Internal edges (removed) | {metrics['internal_edges']} |\n")
            md_content.append(f"| Merged edges (unique) | {metrics['merged_edges']} |\n")
            md_content.append(f"| Edge reduction | {metrics['edge_reduction']} |\n\n")
            
            md_content.append("### Individual Module Details\n\n")
            for mod in modules:
                count = self.module_relation_count.get(mod, {})
                md_content.append(f"**{mod}:**\n")
                md_content.append(f"- Edges from this module: {len(self.module_relation.get(mod, {}))}\n")
                md_content.append(f"- Dependencies Relations: Primary = {count.get('Primary_level_1', 0)}, All = {count.get('Primary_total', 0)}\n")
                md_content.append(f"- Dependents Relations: Primary = {count.get('Reverse_level_1', 0)}, All = {count.get('Reverse_total', 0)}\n\n")
            
            md_content.append("### Summary\n\n")
            md_content.append("After merge, the combined module would have:\n")
            md_content.append(f"- **{metrics['merged_edges']}** total outgoing edges (reduced from {metrics['original_edges']})\n")
            md_content.append(f"- Redundancy saved: {damage['redundant_primary']} Dependents, {damage['redundant_reverse']} Dependencies\n")
            md_content.append(f"- Edges saved: **{metrics['edge_reduction']}**\n\n")
            md_content.append("---\n\n")
        
        # Write to file
        output_path = Path(output_file)
        output_path.write_text(''.join(md_content), encoding='utf-8')
        print(f"Module merge recommendations exported to: {output_path.absolute()}")
        
        return str(output_path.absolute())
    
    def get_merge_statistics(self) -> Dict[str, int]:
        """
        Get statistics about calculated merges.
        
        Returns:
            Dictionary with statistics
        """
        if not self.module_merge_damages:
            self.calculate_all_module_damages()
        
        return {
            "total_module_combinations": len(self.module_merge_damages),
            "modules_analyzed": len(self.module_relation),
        }


def main():
    """
    Main function to run the merge optimizer with command-line arguments.
    
    Arguments:
        --csv: Path to the CSV file (optional, defaults to parent directory)
        --min-merge: Minimum merge count (default: 2)
        --max-merge: Maximum merge count (default: 5)
        --top-n: Number of top recommendations to display (default: 10)
        --output: Output markdown file path
    """
    parser = argparse.ArgumentParser(
        description="Find optimal merge candidates for Boost modules across multiple merge counts"
    )
    parser.add_argument(
        "--csv",
        type=str,
        default=None,
        help="Path to boost_modules_dependencies.csv (default: parent directory)"
    )
    parser.add_argument(
        "--min-merge",
        type=int,
        default=2,
        help="Minimum number of modules to merge together (default: 2)"
    )
    parser.add_argument(
        "--max-merge",
        type=int,
        default=5,
        help="Maximum number of modules to merge together (default: 5)"
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=10,
        help="Number of top recommendations to display (default: 10)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="module_merge_recommendations.md",
        help="Output markdown file path (default: module_merge_recommendations.md)"
    )
    parser.add_argument(
        "--candidate-count",
        type=int,
        default=40,
        help="Number of candidate modules to consider for merging (default: 40)"
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
    print("Relation counts calculated!\n")
    
    # Create merge optimizer
    print(f"Creating merge optimizer (merge count range: {args.min_merge}-{args.max_merge})...\n")
    optimizer = MergeModuleOptimizer(
        module_relation=analyzer.module_relation,
        module_relation_count=module_counts,
        merge_count=args.min_merge  # Default, but will be overridden by range
    )
    
    # Calculate damages across all merge counts
    print("Calculating module merge damages across all merge counts...")
    optimizer.calculate_all_module_damages(merge_count_range=(args.min_merge, args.max_merge), candidate_count=args.candidate_count)
    
    # Print statistics
    stats = optimizer.get_merge_statistics()
    print("\n" + "=" * 80)
    print("ANALYSIS STATISTICS")
    print("=" * 80)
    print(f"  Modules analyzed: {stats['modules_analyzed']}")
    print(f"  Merge count range: {args.min_merge} to {args.max_merge}")
    print(f"  Total merge strategies evaluated: {stats['total_module_combinations']}")
    print("=" * 80)
    print()
    
    # Print recommendations
    optimizer.print_module_merge_recommendations(args.top_n)
    
    # Export to markdown
    print("\nExporting results to markdown file...")
    output_path = optimizer.export_module_merge_to_markdown(f"multi_{args.output}", args.top_n)
    print(f"Results saved to: {output_path}\n")


# Example usage
if __name__ == "__main__":
    main()

