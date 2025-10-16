#!/usr/bin/env python3
"""
Boost Library Dependency Explorer (CSV-based)
Reads boost_modules_dependencies.csv exported by boostdep and generates
JSON + Graphviz graph for a library's dependency neighborhood.

Usage examples:
  python3 make-dependency.py --lib asio
  python3 make-dependency.py --lib asio --depth 2
  python3 make-dependency.py --lib asio --inverse true --depth 2
"""

import argparse
import csv
import json
import os
import re
import subprocess
from pathlib import Path
from collections import defaultdict, deque

def load_csv_dependencies(csv_path="boost_modules_dependencies.csv"):
    """Load Primary and Reverse relationships from the boostdep CSV export.

    Returns two dicts:
      forward_deps: module -> set(dependency_module)
      reverse_deps: module -> set(dependent_module)
    """
    forward_deps = defaultdict(set)
    reverse_deps = defaultdict(set)

    if not Path(csv_path).exists():
        print(f"❌ Error: CSV not found at {csv_path}. Run export_boost_deps.sh first.")
        return None, None

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for row in reader:
            if not row or len(row) < 4:
                continue
            operation, module, dep_module = row[0].strip(), row[1].strip(), row[2].strip()
            if not module or not dep_module:
                continue
            if operation.lower() == 'primary':
                forward_deps[module].add(dep_module)
            elif operation.lower() == 'reverse':
                reverse_deps[module].add(dep_module)

    return forward_deps, reverse_deps

def get_all_modules(forward_deps, reverse_deps):
    modules = set(forward_deps.keys()) | set(reverse_deps.keys())
    for s in forward_deps.values():
        modules.update(s)
    for s in reverse_deps.values():
        modules.update(s)
    return modules

def traverse_neighborhood(seed, forward_deps, reverse_deps, depth=-1, include_reverse=False):
    """BFS traversal to collect nodes and edges around a seed module."""
    nodes = set([seed])
    edges = set()
    q_forward = deque([(seed, 0)])
    q_reverse = deque([(seed, 0)]) if include_reverse else deque()
    max_depth = None if depth is None or depth < 0 else depth

    seen_f = set([seed])
    while q_forward:
        mod, d = q_forward.popleft()
        if max_depth is not None and d >= max_depth:
            continue
        for dep in forward_deps.get(mod, ()):  # mod -> dep
            nodes.add(dep)
            edges.add((mod, dep))
            if dep not in seen_f:
                seen_f.add(dep)
                q_forward.append((dep, d + 1))

    seen_r = set([seed])
    while q_reverse:
        mod, d = q_reverse.popleft()
        if max_depth is not None and d >= max_depth:
            continue
        for dep in reverse_deps.get(mod, ()):  # dep -> mod
            nodes.add(dep)
            if dep not in seen_r:
                seen_r.add(dep)
                q_reverse.append((dep, d + 1))

    # include all intra-node forward edges (to show rings)
    for u in list(nodes):
        for v in forward_deps.get(u, ()):  # u -> v
            if v in nodes:
                edges.add((u, v))

    return nodes, edges

def get_dependents(lib_name, data):
    """Deprecated in CSV mode (kept for backward compatibility)."""
    return []

def write_json(output_base, seed, nodes, edges, depth, reverse):
    data = {
        "seed": seed,
        "depth": depth,
        "reverse": reverse,
        "nodes": sorted(nodes),
        "edges": sorted([{"from": u, "to": v} for (u, v) in edges], key=lambda e: (e["from"], e["to"]))
    }
    out_path = f"{output_base}.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"💾 JSON saved: {out_path}")

def generate_dot(seed, nodes, edges):
    """Generate enhanced horizontal layered DOT with 2-cycle emphasis and level visualization."""
    sanitized_seed = sanitize_node_name(seed)
    lines = []
    lines.append(f"digraph {sanitized_seed}Deps {{")
    
    # Enhanced vertical layout with ordered level visualization
    lines.append("  rankdir=TB;")  # Top to bottom (vertical)
    lines.append("  ranksep=4.0;")  # Space between levels
    lines.append("  nodesep=2.5;")  # Space between nodes
    lines.append("  splines=ortho;")  # Orthogonal edges for cleaner look
    
    # Node styling with level-based colors
    lines.append("  node [shape=box, style=filled, fontname=Arial, fontsize=16];")
    lines.append("  edge [fontname=Arial, fontsize=12];")
    
    # Calculate layers (ancestors and descendants)
    ancestor_layers, descendant_layers = calculate_ancestor_descendant_layers(seed, nodes, edges)
    
    # Detect 2-cycles (direct bidirectional dependencies)
    two_cycles = detect_2_cycles(edges)
    
    # Create ancestor layers (A1, A2, A3...) with ordered level visualization
    for layer_num in sorted(ancestor_layers.keys()):
        layer_nodes = ancestor_layers[layer_num]
        if not layer_nodes:
            continue
            
        lines.append(f"  subgraph cluster_ancestor_{layer_num} {{")
        lines.append(f"    label=\"A{layer_num} (Ancestors)\";")
        lines.append("    style=filled;")
        lines.append("    fillcolor=lightpink;")
        lines.append("    rank=same;")
        
        for node in sorted(layer_nodes):
            # Level-based node styling with ordered colors
            if layer_num == 1:
                lines.append(f"    {sanitize_node_name(node)} [label=\"{node}\", fillcolor=lightcoral, style=filled];")
            elif layer_num == 2:
                lines.append(f"    {sanitize_node_name(node)} [label=\"{node}\", fillcolor=lightpink, style=filled];")
            else:
                lines.append(f"    {sanitize_node_name(node)} [label=\"{node}\", fillcolor=lightgray, style=filled];")
        
        lines.append("  }")
    
    # Create ROOT layer with enhanced styling
    lines.append(f"  subgraph cluster_root {{")
    lines.append(f"    label=\"ROOT (Depth 0)\";")
    lines.append("    style=filled;")
    lines.append("    fillcolor=red;")
    lines.append("    rank=same;")
    lines.append(f"    {sanitize_node_name(seed)} [label=\"{seed}\\n(ROOT)\", fillcolor=darkred, fontcolor=white, style=filled, penwidth=3];")
    lines.append("  }")
    
    # Create descendant layers (D1, D2, D3...) with ordered level visualization
    for layer_num in sorted(descendant_layers.keys()):
        layer_nodes = descendant_layers[layer_num]
        if not layer_nodes:
            continue
            
        lines.append(f"  subgraph cluster_descendant_{layer_num} {{")
        lines.append(f"    label=\"D{layer_num} (Descendants)\";")
        lines.append("    style=filled;")
        lines.append("    fillcolor=lightblue;")
        lines.append("    rank=same;")
        
        for node in sorted(layer_nodes):
            # Level-based node styling with ordered colors
            if layer_num == 1:
                lines.append(f"    {sanitize_node_name(node)} [label=\"{node}\", fillcolor=lightblue, style=filled];")
            elif layer_num == 2:
                lines.append(f"    {sanitize_node_name(node)} [label=\"{node}\", fillcolor=lightcyan, style=filled];")
            else:
                lines.append(f"    {sanitize_node_name(node)} [label=\"{node}\", fillcolor=lightsteelblue, style=filled];")
        
        lines.append("  }")
    
    # Add all edges with enhanced 2-cycle emphasis
    for (u, v) in sorted(edges):
        if (u, v) in two_cycles:
            # Enhanced 2-cycle edges (thick red lines)
            lines.append(f"  {sanitize_node_name(u)} -> {sanitize_node_name(v)} [color=red, penwidth=6, style=bold, arrowsize=2.5];")
        else:
            lines.append(f"  {sanitize_node_name(u)} -> {sanitize_node_name(v)} [color=black, penwidth=1, arrowsize=1];")
    
    # Add 2-cycle information
    if two_cycles:
        lines.append("  // 2-CYCLES DETECTED (Direct Bidirectional Dependencies):")
        for cycle_edge in two_cycles:
            lines.append(f"  // {cycle_edge[0]} <-> {cycle_edge[1]} (2-CYCLE)")
    
    lines.append("}")
    return "\n".join(lines) + "\n"

def calculate_ancestor_descendant_layers(seed, nodes, edges):
    """Calculate ancestor and descendant layers from seed node."""
    from collections import defaultdict, deque
    
    # Build forward and reverse adjacency lists
    forward_adj = defaultdict(set)
    reverse_adj = defaultdict(set)
    for u, v in edges:
        forward_adj[u].add(v)
        reverse_adj[v].add(u)
    
    # Calculate descendant layers (what seed depends on - dependencies)
    descendant_layers = defaultdict(set)
    visited_desc = set()
    queue_desc = deque([(seed, 0)])
    
    while queue_desc:
        node, layer = queue_desc.popleft()
        if node in visited_desc:
            continue
        visited_desc.add(node)
        
        if layer > 0:  # Don't include seed in descendant layers
            descendant_layers[layer].add(node)
        
        # Add dependencies to next layer
        for dep in forward_adj[node]:
            if dep not in visited_desc:
                queue_desc.append((dep, layer + 1))
    
    # Calculate ancestor layers (what depends on seed - dependents)
    ancestor_layers = defaultdict(set)
    visited_anc = set()
    queue_anc = deque([(seed, 0)])
    
    while queue_anc:
        node, layer = queue_anc.popleft()
        if node in visited_anc:
            continue
        visited_anc.add(node)
        
        if layer > 0:  # Don't include seed in ancestor layers
            ancestor_layers[layer].add(node)
        
        # Add dependents to next layer
        for dep in reverse_adj[node]:
            if dep not in visited_anc:
                queue_anc.append((dep, layer + 1))
    
    return ancestor_layers, descendant_layers

def detect_2_cycles(edges):
    """Detect 2-cycles (direct bidirectional dependencies) in the graph."""
    from collections import defaultdict
    
    # Build adjacency list
    adj = defaultdict(set)
    for u, v in edges:
        adj[u].add(v)
    
    # Find 2-cycles: edges where both (u,v) and (v,u) exist
    two_cycles = set()
    for u, v in edges:
        if (v, u) in edges:
            two_cycles.add((u, v))
            two_cycles.add((v, u))
    
    return two_cycles

def generate_dependency_dot(lib_data, all_deps, dependents, data):
    """Deprecated (kept for backward compatibility). Use generate_dot with CSV traversal."""
    return "digraph Empty { }\n"

def sanitize_node_name(name):
    """Sanitize library name for DOT format."""
    # Remove all special characters except underscores
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    # Remove multiple underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    # Handle empty names
    if not sanitized:
        sanitized = 'unnamed'
    # Handle reserved words
    reserved_words = ['graph', 'digraph', 'node', 'edge', 'subgraph']
    if sanitized in reserved_words:
        sanitized = f"{sanitized}_lib"
    return sanitized

def generate_markdown_report(lib_data, all_deps, dependents, data):
    """Deprecated in CSV mode: no markdown emitted."""
    return ""

def generate_graph_image(dot_file, output_format="png"):
    """Generate graph image from DOT file using Graphviz with optimal settings."""
    try:
        base_name = Path(dot_file).stem
        output_dir = Path(dot_file).parent
        output_file = str(output_dir / f"{base_name}.{output_format}")
        
        # Ultra high-quality settings for maximum readability - VERTICAL LAYOUT
        if output_format == "svg":
            # SVG settings (vector, infinitely scalable) - VERTICAL
            cmd = ["dot", "-T", output_format, 
                   "-Grankdir=TB",                 # Force vertical layout
                   "-Granksep=4.0",                # Much more space between ranks
                   "-Gnodesep=2.5",                # Space between nodes
                   "-Gfontsize=20",                # Large font
                   "-Gfontname=Arial",             # Clear font
                   "-Gbgcolor=white",              # White background
                   "-Nfontsize=18",                # Large node font
                   "-Nfontname=Arial",             # Node font
                   "-Efontsize=14",                # Large edge font
                   "-Efontname=Arial",             # Edge font
                   "-Gmargin=0.5",                 # Small margin
                   "-Gcharset=utf8",               # UTF-8 encoding
                   "-Gconcentrate=true",           # Concentrate edges
                   "-Goverlap=false",              # Prevent node overlap
                   "-o", output_file, dot_file]
        else:
            # PNG settings (raster, high DPI) - VERTICAL
            cmd = ["dot", "-T", output_format, 
                   "-Grankdir=TB",                 # Force vertical layout
                   "-Gdpi=600",                    # Ultra high DPI for crisp text
                   "-Gsize=24,48",                 # Taller canvas for vertical layout
                   "-Granksep=4.0",                # Much more space between ranks
                   "-Gnodesep=2.5",                # Space between nodes
                   "-Gfontsize=20",                # Large font
                   "-Gfontname=Arial",             # Clear font
                   "-Gbgcolor=white",              # White background
                   "-Nfontsize=18",                # Large node font
                   "-Nfontname=Arial",             # Node font
                   "-Efontsize=14",                # Large edge font
                   "-Efontname=Arial",             # Edge font
               "-o", output_file, dot_file]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return output_file
        else:
            print(f"❌ Error generating graph: {result.stderr}")
            return None
            
    except FileNotFoundError:
        print("❌ Graphviz not found. Install with: sudo apt-get install graphviz")
        return None
    except Exception as e:
        print(f"❌ Error generating graph: {e}")
        return None

def cleanup_old_files(lib_name, depth=None):
    """Clean up old files for the library."""
    import os
    import glob
    import shutil
    
    # Remove old files in dependencies/{lib_name} directory
    deps_dir = f"dependencies/{lib_name}"
    if os.path.exists(deps_dir):
        try:
            # Only remove files matching the current depth pattern
            if depth is not None:
                pattern = f"{lib_name}_deps_d{depth}_rev.*"
                old_files = glob.glob(f"{deps_dir}/{pattern}")
                for file in old_files:
                    os.remove(file)
                    print(f"🗑️  Removed old file: {file}")
            else:
                # Remove entire directory only if no depth specified
                shutil.rmtree(deps_dir)
                print(f"🗑️  Removed old directory: {deps_dir}")
        except:
            pass
    
    # Also clean up any old files in root directory (backward compatibility)
    old_files = glob.glob(f"{lib_name}_*.*")
    for file in old_files:
        try:
            os.remove(file)
            print(f"🗑️  Removed old file: {file}")
        except:
            pass
    
def save_dot_and_image(output_base, dot_content):
    dot_file = f"{output_base}.dot"
    with open(dot_file, 'w', encoding='utf-8') as f:
        f.write(dot_content)
    print(f"💾 DOT saved: {dot_file}")
    
    # Generate both PNG and SVG for maximum quality
    png_image = generate_graph_image(dot_file, "png")
    if png_image:
        print(f"📊 PNG image generated: {png_image}")
    
    svg_image = generate_graph_image(dot_file, "svg")
    if svg_image:
        print(f"📊 SVG image generated: {svg_image} (vector, infinitely scalable)")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Explore Boost module dependencies from CSV')
    parser.add_argument('--lib', required=True, help='Seed Boost module, e.g., asio')
    parser.add_argument('--dep', type=int, default=-1, help='Traversal depth; -1 for full closure')
    parser.add_argument('--rev', type=str, default='false', help='Include reverse (dependents): true/false')
    parser.add_argument('--csv', type=str, default='boost_modules_dependencies.csv', help='Path to boostdep CSV')
    args = parser.parse_args()
    
    lib = args.lib
    depth = args.dep
    reverse = str(args.rev).lower() in ('1', 't', 'true', 'yes', 'y')

    print(f"🔍 Building dependency neighborhood for '{lib}' (depth={depth}, reverse={reverse})")
    print("=" * 50)
    
    cleanup_old_files(lib, depth)
    
    fwd, rev = load_csv_dependencies(args.csv)
    if fwd is None:
        return
    
    modules = get_all_modules(fwd, rev)
    if lib not in modules:
        print(f"❌ Module '{lib}' not found in CSV. Run export_boost_deps.sh first.")
        return
    
    nodes, edges = traverse_neighborhood(lib, fwd, rev, depth=depth, include_reverse=reverse)
    print(f"📊 Nodes: {len(nodes)} | Edges: {len(edges)}")

    # Create dependencies/{lib} directory
    import os
    deps_dir = f"dependencies/{lib}"
    os.makedirs(deps_dir, exist_ok=True)
    
    base = f"{deps_dir}/{lib}_deps"
    if depth is not None and depth >= 0:
        base += f"_d{depth}"
    if reverse:
        base += "_rev"

    write_json(base, lib, nodes, edges, depth, reverse)
    dot_text = generate_dot(lib, nodes, edges)
    save_dot_and_image(base, dot_text)
    print(f"\n✅ Done for {lib}")

if __name__ == "__main__":
    main()
