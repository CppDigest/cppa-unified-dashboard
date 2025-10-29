# BoostDepth - Boost Library Dependency Analysis

A comprehensive toolset for analyzing Boost C++ library dependencies using the official `boostdep` tool. This project generates dependency graphs, JSON data, and visualizations for Boost libraries.

## Overview

BoostDepth provides comprehensive tools for dependency analysis:

### Core Tools

1. **`export_boost_deps.sh`** - Exports all Boost module dependencies to CSV
2. **`make-dependency.py`** - Generates dependency graphs for specific libraries
3. **`generate_all_deps.sh`** - Batch processes multiple libraries

### Advanced Analysis Tools

4. **`BoostDependencyAnalyzer`** - Analyzes module and header dependencies with relation mapping
5. **`HeaderNetworkOptimizer`** - Network analysis using Louvain community detection for merge optimization
6. **`HeaderModuleAnalyzer`** - Analyzes internal vs external module connections for headers
7. **`MergeOptimizer`** - Suggests module merge strategies based on dependency patterns

## Prerequisites

### Basic Tools
- Boost C++ libraries (cloned in `boost/` directory)
- Python 3.x
- Graphviz (for generating graph images)
- Bash shell

### Advanced Analysis Tools
- NetworkX (`pip install networkx>=2.6.3`)
- python-louvain (`pip install python-louvain>=0.16`)
- libclang (`pip install libclang>=14.0`)

Install all dependencies:
```bash
pip install -r requirements.txt
```

## Installation

1. Clone this repository
2. Ensure Boost is available in the `boost/` directory
3. Install Graphviz: `sudo apt-get install graphviz`

## Usage

### 1. Export All Dependencies

First, export all Boost module dependencies to CSV:

```bash
bash export_boost_deps.sh
```

This creates `boost_modules_dependencies.csv` with all primary and reverse dependencies.

### 2. Generate Dependency Graphs for Specific Libraries

Generate dependency graphs for a specific library:

```bash
# Basic usage (full closure, no reverse dependencies)
python3 make-dependency.py --lib asio

# With depth limit
python3 make-dependency.py --lib asio --dep 2

# With reverse dependencies
python3 make-dependency.py --lib asio --dep 2 --rev true
```

**Arguments:**
- `--lib`: Library name (e.g., asio, beast, json)
- `--dep`: Traversal depth (-1 for full closure)
- `--rev`: Include reverse dependencies (true/false)
- `--csv`: Path to CSV file (default: `boost_modules_dependencies.csv`)

### 3. Batch Process Multiple Libraries

Process all libraries listed in `lib_list.txt`:

```bash
bash generate_all_deps.sh
```

This generates both depth 1 and depth 2 dependency graphs with reverse dependencies for all libraries in `lib_list.txt`.

## Advanced Network Analysis

### Header Network Optimizer

The `HeaderNetworkOptimizer` uses network analysis and the Louvain community detection algorithm to suggest optimal header merge strategies.

#### Quick Start

```bash
cd statistics
python header_network_optimizer.py
```

This will:
1. Load header dependencies
2. Build a dependency network graph
3. Detect communities using the Louvain method
4. Generate merge recommendations
5. Export results to markdown and JSON files

#### Programmatic Usage

```python
from statistics.boost_dependency_analyzer import BoostDependencyAnalyzer
from statistics.header_network_optimizer import HeaderNetworkOptimizer

# Load dependencies
analyzer = BoostDependencyAnalyzer()
analyzer.read_csv()

# Create optimizer and build network
optimizer = HeaderNetworkOptimizer(analyzer)
optimizer.build_network(min_degree=1)

# Detect communities
optimizer.detect_communities(resolution=1.0)

# Generate merge recommendations
recommendations = optimizer.suggest_merge_strategies(
    min_community_size=3,
    max_community_size=50,
    min_cohesion=0.5
)

# Export results
optimizer.export_recommendations(recommendations, top_n=30)
optimizer.export_network_data()
```

#### Key Features

- **Community Detection**: Uses Louvain algorithm to identify clusters of related headers
- **Merge Recommendations**: Suggests which headers to merge based on:
  - Cohesion (internal vs external connectivity)
  - Density (how tightly connected)
  - Module distribution
  - Hub analysis
- **Comprehensive Reporting**: Generates detailed markdown reports
- **JSON Export**: Exports network data for further analysis

See [`statistics/HEADER_NETWORK_OPTIMIZER_README.md`](statistics/HEADER_NETWORK_OPTIMIZER_README.md) for detailed documentation.

### Boost Dependency Analyzer

Analyzes module and header dependencies with relation mapping:

```bash
cd statistics
python boost_dependency_analyzer.py
```

Features:
- Module-to-module dependency analysis
- Header-to-header dependency tracking
- Primary/Reverse/Bidirectional relation classification
- Transitive dependency counting
- Statistics and reporting

See [`statistics/ANALYZER_OPTIMIZER_README.md`](statistics/ANALYZER_OPTIMIZER_README.md) for detailed documentation.

### Header Module Analyzer

Analyzes header dependencies across module boundaries:

```bash
cd statistics
python header_module_analyzer.py
```

Features:
- Counts internal (same module) vs external (cross-module) connections for each header
- Identifies headers with high cross-module dependencies
- Provides module-level cohesion metrics
- Exports analysis to CSV and markdown reports

Example:
```python
from statistics.header_module_analyzer import HeaderModuleAnalyzer

analyzer = BoostDependencyAnalyzer()
analyzer.read_csv()

module_analyzer = HeaderModuleAnalyzer(analyzer)
module_analyzer.build_module_mapping()
module_analyzer.analyze_header_connections()

# Find headers with >70% external dependencies
problems = module_analyzer.find_headers_with_high_external_ratio(min_ratio=0.7)

# Get module summary
summary = module_analyzer.get_module_summary('asio')
print(f"Internal: {summary['total_internal']}, External: {summary['total_external']}")
```

See [`statistics/HEADER_MODULE_ANALYZER_README.md`](statistics/HEADER_MODULE_ANALYZER_README.md) for detailed documentation.

## Output Files

Each library generates the following files in `dependencies/{library_name}/`:

- **JSON**: `{lib}_deps_d{depth}_rev.json` - Structured dependency data
- **DOT**: `{lib}_deps_d{depth}_rev.dot` - Graphviz source code
- **PNG**: `{lib}_deps_d{depth}_rev.png` - High-resolution raster image (600 DPI)
- **SVG**: `{lib}_deps_d{depth}_rev.svg` - Vector image (infinitely scalable)

## Graph Features

- **Vertical Layout**: Top-to-bottom dependency flow
- **Layered Visualization**: 
  - A1, A2, A3... (Ancestor layers)
  - ROOT (Seed library)
  - D1, D2, D3... (Descendant layers)
- **2-Cycle Emphasis**: Direct bidirectional dependencies highlighted in red
- **High Quality**: Ultra-high DPI PNG and vector SVG outputs

## Example Libraries

The default `lib_list.txt` includes:
- `unordered` - Hash containers
- `beast` - HTTP and WebSocket
- `multiprecision` - Arbitrary precision arithmetic
- `asio` - Asynchronous I/O
- `json` - JSON parsing and serialization
- `url` - URL parsing and manipulation
- `exception` - Exception handling
- `graph` - Graph algorithms

## File Structure

```
BoostDepth/
├── boost/                          # Boost C++ libraries
├── dependencies/                   # Generated dependency graphs
│   ├── asio/
│   │   ├── asio_deps_d1_rev.json
│   │   ├── asio_deps_d1_rev.dot
│   │   ├── asio_deps_d1_rev.png
│   │   ├── asio_deps_d1_rev.svg
│   │   ├── asio_deps_d2_rev.json
│   │   ├── asio_deps_d2_rev.dot
│   │   ├── asio_deps_d2_rev.png
│   │   └── asio_deps_d2_rev.svg
│   └── ...
├── statistics/                     # Advanced analysis tools
│   ├── boost_dependency_analyzer.py      # Dependency analyzer
│   ├── header_network_optimizer.py       # Network optimization
│   ├── header_module_analyzer.py         # Module boundary analysis
│   ├── merge_optimizer.py                # Module merge suggestions
│   ├── example_network_analysis.py       # Network analysis examples
│   ├── example_module_analysis.py        # Module analysis examples
│   ├── view_community_headers.py         # Interactive header viewer
│   ├── ANALYZER_OPTIMIZER_README.md      # Analyzer documentation
│   ├── HEADER_NETWORK_OPTIMIZER_README.md # Optimizer documentation
│   └── HEADER_MODULE_ANALYZER_README.md  # Module analyzer documentation
├── boost_modules_dependencies.csv  # Exported dependency data
├── boost_dependency_report.md      # Generated statistics report
├── header_merge_recommendations.md # Network analysis results
├── header_network_data.json        # Network data export
├── header_module_analysis.csv      # Module boundary analysis (per-header)
├── module_summary.csv              # Module boundary analysis (per-module)
├── header_module_report.md         # Module boundary analysis report
├── lib_list.txt                   # List of libraries to process
├── requirements.txt               # Python dependencies
├── export_boost_deps.sh           # Export script
├── make-dependency.py              # Graph generation script
├── generate_all_deps.sh            # Batch processing script
└── README.md                       # This file
```

## Technical Details

- **Dependency Traversal**: BFS (Breadth-First Search) algorithm
- **Graph Generation**: Graphviz DOT format
- **Image Formats**: PNG (raster) and SVG (vector)
- **Data Format**: JSON with nodes and edges
- **Layout**: Vertical with orthogonal edges

## Troubleshooting

1. **"boostdep: Could not find Boost root"**: Ensure you're running from the project root directory
2. **"Graphviz not found"**: Install Graphviz with `sudo apt-get install graphviz`
3. **"Module not found"**: Run `export_boost_deps.sh` first to generate the CSV file

