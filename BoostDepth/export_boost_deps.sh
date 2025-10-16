#!/usr/bin/env bash

set -euo pipefail

# Configuration
PROJECT_ROOT="."
BOOST_ROOT="boost"
BOOSTDEP_BIN="boost/dist/bin/boostdep"
OUT_CSV="boost_modules_dependencies.csv"

# Ensure boostdep is built
if [[ ! -x "$BOOSTDEP_BIN" ]]; then
  echo "Building boostdep at $BOOST_ROOT ..."
  cd "$BOOST_ROOT"
  ./bootstrap.sh >/dev/null
  ./b2 -q tools/boostdep/build
fi

# Create CSV with both primary (deps) and reverse tables, no table markers
echo "Exporting dependencies to $OUT_CSV ..."
{
  # Print a header row for our combined CSV
  echo "Operation,Module,Header,From"

  # List all modules (run from boost directory)
  MODULES=$(cd "$BOOST_ROOT" && ./dist/bin/boostdep --list-modules)

  # For each module, emit two tables in CSV (primary deps and reverse deps)
  while IFS= read -r MOD; do
    [[ -z "$MOD" ]] && continue
    # Primary (what MOD depends on)
    (cd "$BOOST_ROOT" && ./dist/bin/boostdep --csv --csv-no-table-marker --primary "$MOD") \
      | tail -n +2 \
      | awk -v op="Primary" -v m="$MOD" -F',' 'NF{print op "," m "," $0}'

    # Reverse (what depends on MOD)
    (cd "$BOOST_ROOT" && ./dist/bin/boostdep --csv --csv-no-table-marker --reverse "$MOD") \
      | tail -n +2 \
      | awk -v op="Reverse" -v m="$MOD" -F',' 'NF{print op "," m "," $0}'
  done <<< "$MODULES"
} > "$OUT_CSV"

echo "Done: $OUT_CSV"


