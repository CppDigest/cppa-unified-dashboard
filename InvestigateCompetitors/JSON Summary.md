# C++ JSON libraries competing with Boost.JSON

## 1. Overview

Scope: DOM-style JSON parsing, serialization, and manipulation for C++11+ production code, comparing Boost.JSON with five major competitors.

The primary trade-offs are performance, API ergonomics, ecosystem maturity, and standards support.

Libraries covered:

- Boost.JSON (baseline) [1][2]  
- nlohmann/json [3][4]  
- RapidJSON [5][6]  
- simdjson [7][8]  
- jsoncons [9]  
- picojson [10]  

---

## 2. Library snapshots (vs Boost.JSON)

All performance statements are relative, based on the cited benchmarks and docs [2][6][8][11].

### Boost.JSON (reference) [1][2]

- Design: C++11 JSON DOM and serialization library integrated with Boost; emphasis on predictable performance and low allocations.  
- Performance: Public benchmarks referenced from the Boost.JSON docs indicate competitive performance among modern C++ JSON libraries for DOM parsing [2][11].  
- C++: Requires C++11 or later; supports the mainstream compilers (GCC, Clang, MSVC) supported by Boost [1][2].

### nlohmann/json [3][4]

- Design: STL-like JSON value type with very friendly syntax, implicit conversions, and rich examples.  
- Advantage vs Boost.JSON: Much easier API for many users and a very large ecosystem [3].  
- Disadvantage vs Boost.JSON: DOM parsing is typically around 2–5× slower and more memory hungry than Boost.JSON and other performance-oriented libraries [2][11]; heavy templates increase build times.  
- C++: Supports C++11 and later [3][4].

### RapidJSON [5][6]

- Design: Performance-oriented DOM and SAX parser with fine-grained control over memory and allocators.  
- Advantage vs Boost.JSON: Vendor and third‑party benchmarks report high parsing throughput on desktop CPUs, with competitive performance on workloads similar to those used for Boost.JSON [2][6][11].  
- Disadvantage vs Boost.JSON: Lower-level, more verbose API, with more manual lifetime and allocator handling; documentation is adequate but less cohesive than Boost or nlohmann/json [5].  
- C++: Supports C++11 and older compilers; does not rely on C++14/17 features [5][6].

### simdjson [7][8]

- Design: Uses SIMD instructions to achieve extremely high parsing throughput; provides DOM and on-demand streaming-style APIs.  
- Advantage vs Boost.JSON: Official benchmarks often show 2–4 GB/s parsing throughput, several times faster than RapidJSON. Boost.JSON is positioned as competitive with RapidJSON [2][11], so simdjson is typically much faster than Boost.JSON on modern x86 hardware [8][11].  
- Disadvantage vs Boost.JSON: Ergonomics are more performance-driven and less conventional than Boost.JSON (see C++ requirement below).  
- C++: Minimum C++17 for recent releases; older branches that support C++11 are legacy only [7][8].

### jsoncons [9]

- Design: Feature-rich JSON library with DOM, streaming, JSONPath, JSON Schema, and support for CBOR, MessagePack, BSON, and other encodings.  
- Advantage vs Boost.JSON: Significantly broader feature set and strong focus on standards conformance and type mapping, while still supporting C++11 [9].  
- Disadvantage vs Boost.JSON: Performance is generally good but usually below RapidJSON and simdjson; API surface is larger and more complex [9][11].  
- C++: Supports C++11 and later [9].

### picojson [10]

- Design: Very small, single-header DOM library with minimal dependencies.  
- Advantage vs Boost.JSON: Tiny codebase and trivial integration, suitable where dependency footprint is critical [10].  
- Disadvantage vs Boost.JSON: Significantly slower parsing and higher memory overhead than modern optimized libraries; limited features and less active maintenance [10][11].  
- C++: Minimum C++11; single-header, header-only API [10].

---

## 3. Comparison tables and usage guidance

### Performance and Ecosystem Metrics

Approximate values based on public stats and documentation.

| Library      | Parse speed vs Boost (DOM) | Memory vs Boost | Build impact | Approx LOC | Quality signals (tests/CI)                                   | Stars / contributors | Min C++ | API ergonomics (1–5) | Docs quality (1–5) |
|-------------|----------------------------|-----------------|-------------|-----------:|----------------------------------------------------------------|----------------------|---------|----------------------|--------------------|
| Boost.JSON  | 1.0 (baseline) [2]         | baseline [2]    | Medium      | ~20k       | Part of the Boost project with its standard testing and release processes [1][2] | ~0.5k / 37 [1]      | C++11   | 4 (value-based, clear) | 4 (Boost-style ref) |
| nlohmann/json | ~0.2–0.4× [2][11]        | higher [2][11]  | High        | ~30k       | Extensive tests, coverage badges, static analysis [3]          | ~48.7k / 317 [3]      | C++11   | 5 (STL-like, intuitive) | 5 (guide, cookbook) |
| RapidJSON   | ~1.0–1.2× [2][6][11]       | lower [6][11]   | Medium      | ~25k       | Includes performance benchmarks and test data [5][6]           | ~15k / 189+          | C++11   | 3 (low-level)        | 3–4 (good but dated) |
| simdjson    | ~3–5× [8][11]              | similar/lower [8] | Medium–High | ~20k     | Rigorous benchmarks and validation corpus [7][8]               | ~23.2k / 167 [7]      | C++17   | 3 (efficient but specialized) | 4 (performance-focused docs) |
| jsoncons    | ~0.6–0.9× [9][11]          | similar/slightly higher [9] | Medium | ~40k | Open-source GitHub project with documentation and examples [9] | ~0.8k+ / 68           | C++11   | 4 (rich but larger surface) | 4 (API and feature docs) |
| picojson    | ~0.2–0.3× [10][11]         | higher [10][11] | Low         | <5k        | Very small, single-header codebase [10]                        | ~1.1k / 22          | C++11   | 2 (minimal, manual)  | 2–3 (simple README) |

**Notes:**
- Parse speed factors are rough ratios derived from Boost.JSON docs, vendor benchmarks, and nativejson-benchmark [2][6][8][11].  
- Build impact is qualitative: header-only, heavily templated libraries such as nlohmann/json usually cost more compile time.

### Summary and Usage Guidance

| Library      | Main advantage vs Boost.JSON                          | Main disadvantage vs Boost.JSON                            | When to prefer                                             |
|-------------|--------------------------------------------------------|------------------------------------------------------------|-----------------------------------------------------------|
| Boost.JSON  | Balanced performance, robust tests, Boost integration  | Smaller community and ecosystem than nlohmann/json         | When using Boost already, need C++11 and solid all-rounder |
| nlohmann/json | Easiest, most idiomatic DOM API, huge ecosystem      | 2–5× slower and heavier in memory/compile time [2][11]     | When readability, examples and community support dominate  |
| RapidJSON   | Competitive throughput and lower memory use [2][6][11] | Lower-level, more verbose API                              | For C++11 code needing high performance and fine control   |
| simdjson    | By far the fastest parser (multi‑GB/s) [8][11]         | Requires C++17 and modern hardware; less conventional API  | For extreme throughput or low-latency ingestion pipelines  |
| jsoncons    | Richest feature set (JSONPath, schema, binary formats) | Slightly slower and more complex than Boost/RapidJSON [9]  | For multi-format data pipelines and standards-heavy use    |
| picojson    | Tiny single-header, minimal dependencies               | Much slower, fewer features, lighter testing [10][11]      | For very small tools or tight binary size constraints      |

---

## 4. Recent trends (2023–2025)

- Boost.JSON  
  - Activity: Regular commits and releases as part of Boost; CI remains active [1][2].  
  - Adoption: Stars and usage show slow, steady growth within projects that already depend on Boost [1].

- nlohmann/json  
  - Activity: Frequent releases and issue activity with many external contributors [3].  
  - Adoption: Continues to grow strongly in stars and downstream usage; widely treated as the default C++ JSON library [3].

- RapidJSON  
  - Activity: Maintenance updates and bug fixes continue, but major feature releases are less frequent than earlier years [5].  
  - Adoption: Stable or slowly growing, with many existing production deployments rather than rapid new adoption [5][11].

- simdjson  
  - Activity: Ongoing development with multiple major versions since 2023, continuous benchmark updates and platform enhancements [7][8].  
  - Adoption: GitHub stars and bindings for other languages indicate growing interest for high-performance workloads [7][8].

- jsoncons  
  - Activity: Regular commits adding features such as improved JSON Schema handling and binary formats [9].  
  - Adoption: Gradual growth driven by users needing multiple encodings and advanced JSON features [9].

- picojson  
  - Activity: Sporadic commits and relatively long-standing issues compared with more active projects [10].  
  - Adoption: Largely stable legacy usage, with limited growth [10].

---

## 5. Conclusions and practical choices

For modern C++11-centric production code, the strongest general-purpose options are Boost.JSON, nlohmann/json, RapidJSON, and jsoncons, with simdjson as a top choice if C++17 is acceptable.

- Favor Boost.JSON when:  
  - A balanced trade-off of speed, memory, robustness, and C++11 support is needed, especially in codebases already using Boost [1][2].  
  - You prefer a value-based API that is safer and more modern than RapidJSON while faster and leaner than nlohmann/json in many workloads [2][11].

- Prefer nlohmann/json over Boost.JSON when:  
  - API ergonomics, discoverability, and community resources outweigh raw performance or build times [3][4].  
  - You want an STL-like interface that is very easy for new contributors to understand.

- Prefer RapidJSON over Boost.JSON when:  
  - Competitive to slightly better parsing performance with lower memory use and fine-grained control over allocators and memory layout are critical, and a lower-level API is acceptable [5][6].  

- Prefer simdjson over Boost.JSON when:  
  - You control the toolchain (C++17+) and hardware and need multi‑GB/s parsing or very low latency, such as log ingestion or analytics [7][8][11].  

- Prefer jsoncons over Boost.JSON when:  
  - Requirements include JSONPath, schema validation, or multiple binary formats alongside JSON, and you need a library that supports C++11 [9].  

- Prefer picojson over Boost.JSON only when:  
  - Dependency and size constraints dominate, performance and feature richness are secondary, and JSON volumes are modest [10][11].  

Overall, Boost.JSON is a strong default for C++11 projects that value predictable performance, robust testing, and Boost integration, while alternatives offer clear advantages for ergonomics (nlohmann/json), raw speed (RapidJSON, simdjson), or advanced features (jsoncons).

---

### Sources

[1] Boost.JSON GitHub: https://github.com/boostorg/json  
[2] Boost.JSON documentation and benchmarks: https://www.boost.org/doc/libs/release/libs/json/doc/html/index.html  
[3] nlohmann/json GitHub: https://github.com/nlohmann/json  
[4] nlohmann/json documentation: https://json.nlohmann.me  
[5] RapidJSON GitHub: https://github.com/Tencent/rapidjson  
[6] RapidJSON performance notes: https://rapidjson.org/md_doc_performance.html  
[7] simdjson GitHub: https://github.com/simdjson/simdjson  
[8] simdjson documentation and benchmarks: https://simdjson.org  
[9] jsoncons GitHub: https://github.com/danielaparker/jsoncons  
[10] picojson GitHub: https://github.com/kazuho/picojson  
[11] nativejson-benchmark: https://github.com/miloyip/nativejson-benchmark