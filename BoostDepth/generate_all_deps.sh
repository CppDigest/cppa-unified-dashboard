#!/bin/bash

# Script to generate dependencies for all libraries in lib_list.txt
# Generates both depth 1 and depth 2 with reverse dependencies

echo "🚀 Generating dependencies for all libraries..."
echo "=============================================="

# Read libraries from lib_list.txt
while IFS= read -r lib; do
    # Skip empty lines
    if [ -z "$lib" ]; then
        continue
    fi
    
    echo ""
    echo "📚 Processing library: $lib"
    echo "------------------------"
    
    # Generate depth 1 with reverse
    echo "🔍 Generating depth 1 with reverse dependencies..."
    python3 make-dependency.py --lib "$lib" --dep 1 --rev true
    
    # Generate depth 2 with reverse (without cleanup to preserve depth 1 files)
    echo "🔍 Generating depth 2 with reverse dependencies..."
    python3 make-dependency.py --lib "$lib" --dep 2 --rev true
    
    echo "✅ Completed: $lib"
    echo ""
    
done < lib_list.txt

echo "🎉 All libraries processed!"
echo ""
echo "📁 Generated files are organized in:"
echo "   dependencies/{library_name}/"
echo ""
echo "📊 Each library has:"
echo "   - {lib}_deps_d1_rev.json (depth 1 data)"
echo "   - {lib}_deps_d1_rev.dot (depth 1 source)"
echo "   - {lib}_deps_d1_rev.png (depth 1 image)"
echo "   - {lib}_deps_d1_rev.svg (depth 1 vector)"
echo "   - {lib}_deps_d2_rev.json (depth 2 data)"
echo "   - {lib}_deps_d2_rev.dot (depth 2 source)"
echo "   - {lib}_deps_d2_rev.png (depth 2 image)"
echo "   - {lib}_deps_d2_rev.svg (depth 2 vector)"
