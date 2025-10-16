# BoostDepth - Boost Library Dependency Analysis

A comprehensive toolset for analyzing Boost C++ library dependencies using the official `boostdep` tool. This project generates dependency graphs, JSON data, and visualizations for Boost libraries.

## Overview

BoostDepth provides three main tools for dependency analysis:

1. **`export_boost_deps.sh`** - Exports all Boost module dependencies to CSV
2. **`make-dependency.py`** - Generates dependency graphs for specific libraries
3. **`generate_all_deps.sh`** - Batch processes multiple libraries

## Prerequisites

- Boost C++ libraries (cloned in `boost/` directory)
- Python 3.x
- Graphviz (for generating graph images)
- Bash shell

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
├── boost_modules_dependencies.csv  # Exported dependency data
├── lib_list.txt                   # List of libraries to process
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

