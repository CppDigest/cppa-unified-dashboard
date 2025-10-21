# Module Merge Recommendations

**Merge Count:** 3 modules per combination
**Top Recommendations:** 10
**Sorting:** By Edge Reduction (highest first)

## Overall Impact
| Metric | Value |
|--------|-------|
| Original total edges | 2764 |
| Reduced total edges | 2137 |
| Edge reduction | 627 (22.68%) |
| Modules merged | 30 |

---

## Rank 1: assert + config + core

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 334 |
| Internal edges (removed) | 6 |
| Merged edges (unique) | 137 |
| Edge reduction | 197 (58.98%) |

### Individual Module Details

**assert:**
- Edges from this module: 95
- Dependents Relations: Primary = 1, All = 1
- Dependencies Relations: Primary = 94, All = 129

**config:**
- Edges from this module: 137
- Dependents Relations: Primary = 0, All = 0
- Dependencies Relations: Primary = 137, All = 141

**core:**
- Edges from this module: 102
- Dependents Relations: Primary = 4, All = 4
- Dependencies Relations: Primary = 98, All = 115

### Summary

After merge, the combined module would have:
- **137** total outgoing edges (reduced from 334)
- Redundancy saved: 1 Dependents, 190 Dependencies
- Edges saved: **197** (58.98%)

---

## Rank 2: mpl + static_assert + type_traits

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 205 |
| Internal edges (removed) | 6 |
| Merged edges (unique) | 95 |
| Edge reduction | 110 (53.66%) |

### Individual Module Details

**mpl:**
- Edges from this module: 59
- Dependents Relations: Primary = 7, All = 10
- Dependencies Relations: Primary = 52, All = 76

**static_assert:**
- Edges from this module: 60
- Dependents Relations: Primary = 1, All = 1
- Dependencies Relations: Primary = 59, All = 121

**type_traits:**
- Edges from this module: 86
- Dependents Relations: Primary = 2, All = 2
- Dependencies Relations: Primary = 84, All = 107

### Summary

After merge, the combined module would have:
- **95** total outgoing edges (reduced from 205)
- Redundancy saved: 3 Dependents, 101 Dependencies
- Edges saved: **110** (53.66%)

---

## Rank 3: graph + iterator + throw_exception

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 164 |
| Internal edges (removed) | 4 |
| Merged edges (unique) | 99 |
| Edge reduction | 65 (39.63%) |

### Individual Module Details

**graph:**
- Edges from this module: 46
- Dependents Relations: Primary = 42, All = 71
- Dependencies Relations: Primary = 3, All = 6

**iterator:**
- Edges from this module: 47
- Dependents Relations: Primary = 10, All = 24
- Dependencies Relations: Primary = 37, All = 61

**throw_exception:**
- Edges from this module: 71
- Dependents Relations: Primary = 2, All = 2
- Dependencies Relations: Primary = 69, All = 122

### Summary

After merge, the combined module would have:
- **99** total outgoing edges (reduced from 164)
- Redundancy saved: 10 Dependents, 26 Dependencies
- Edges saved: **65** (39.63%)

---

## Rank 4: preprocessor + smart_ptr + utility

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 131 |
| Internal edges (removed) | 2 |
| Merged edges (unique) | 77 |
| Edge reduction | 54 (41.22%) |

### Individual Module Details

**preprocessor:**
- Edges from this module: 47
- Dependents Relations: Primary = 0, All = 0
- Dependencies Relations: Primary = 47, All = 94

**smart_ptr:**
- Edges from this module: 40
- Dependents Relations: Primary = 4, All = 5
- Dependencies Relations: Primary = 36, All = 64

**utility:**
- Edges from this module: 44
- Dependents Relations: Primary = 7, All = 8
- Dependencies Relations: Primary = 37, All = 84

### Summary

After merge, the combined module would have:
- **77** total outgoing edges (reduced from 131)
- Redundancy saved: 4 Dependents, 48 Dependencies
- Edges saved: **54** (41.22%)

---

## Rank 5: range + serialization + spirit

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 109 |
| Internal edges (removed) | 4 |
| Merged edges (unique) | 62 |
| Edge reduction | 47 (43.12%) |

### Individual Module Details

**range:**
- Edges from this module: 39
- Dependents Relations: Primary = 17, All = 30
- Dependencies Relations: Primary = 22, All = 45

**serialization:**
- Edges from this module: 34
- Dependents Relations: Primary = 23, All = 57
- Dependencies Relations: Primary = 11, All = 16

**spirit:**
- Edges from this module: 36
- Dependents Relations: Primary = 30, All = 56
- Dependencies Relations: Primary = 6, All = 19

### Summary

After merge, the combined module would have:
- **62** total outgoing edges (reduced from 109)
- Redundancy saved: 31 Dependents, 10 Dependencies
- Edges saved: **47** (43.12%)

---

## Rank 6: compute + fusion + thread

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 92 |
| Internal edges (removed) | 4 |
| Merged edges (unique) | 56 |
| Edge reduction | 36 (39.13%) |

### Individual Module Details

**compute:**
- Edges from this module: 31
- Dependents Relations: Primary = 29, All = 64
- Dependencies Relations: Primary = 2, All = 3

**fusion:**
- Edges from this module: 28
- Dependents Relations: Primary = 12, All = 21
- Dependencies Relations: Primary = 16, All = 67

**thread:**
- Edges from this module: 33
- Dependents Relations: Primary = 25, All = 49
- Dependencies Relations: Primary = 8, All = 25

### Summary

After merge, the combined module would have:
- **56** total outgoing edges (reduced from 92)
- Redundancy saved: 25 Dependents, 6 Dependencies
- Edges saved: **36** (39.13%)

---

## Rank 7: bind + function + optional

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 74 |
| Internal edges (removed) | 2 |
| Merged edges (unique) | 42 |
| Edge reduction | 32 (43.24%) |

### Individual Module Details

**bind:**
- Edges from this module: 17
- Dependents Relations: Primary = 2, All = 5
- Dependencies Relations: Primary = 15, All = 72

**function:**
- Edges from this module: 27
- Dependents Relations: Primary = 5, All = 6
- Dependencies Relations: Primary = 22, All = 71

**optional:**
- Edges from this module: 30
- Dependents Relations: Primary = 5, All = 6
- Dependencies Relations: Primary = 25, All = 66

### Summary

After merge, the combined module would have:
- **42** total outgoing edges (reduced from 74)
- Redundancy saved: 6 Dependents, 24 Dependencies
- Edges saved: **32** (43.24%)

---

## Rank 8: mpi + property_map + python

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 63 |
| Internal edges (removed) | 4 |
| Merged edges (unique) | 31 |
| Edge reduction | 32 (50.79%) |

### Individual Module Details

**mpi:**
- Edges from this module: 21
- Dependents Relations: Primary = 18, All = 73
- Dependencies Relations: Primary = 3, All = 3

**property_map:**
- Edges from this module: 19
- Dependents Relations: Primary = 15, All = 32
- Dependencies Relations: Primary = 4, All = 7

**python:**
- Edges from this module: 23
- Dependents Relations: Primary = 21, All = 72
- Dependencies Relations: Primary = 2, All = 5

### Summary

After merge, the combined module would have:
- **31** total outgoing edges (reduced from 63)
- Redundancy saved: 25 Dependents, 2 Dependencies
- Edges saved: **32** (50.79%)

---

## Rank 9: multi_index + property_tree + xpressive

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 63 |
| Internal edges (removed) | 2 |
| Merged edges (unique) | 35 |
| Edge reduction | 28 (44.44%) |

### Individual Module Details

**multi_index:**
- Edges from this module: 22
- Dependents Relations: Primary = 16, All = 28
- Dependencies Relations: Primary = 6, All = 15

**property_tree:**
- Edges from this module: 17
- Dependents Relations: Primary = 14, All = 60
- Dependencies Relations: Primary = 3, All = 11

**xpressive:**
- Edges from this module: 24
- Dependents Relations: Primary = 22, All = 39
- Dependencies Relations: Primary = 2, All = 8

### Summary

After merge, the combined module would have:
- **35** total outgoing edges (reduced from 63)
- Redundancy saved: 23 Dependents, 3 Dependencies
- Edges saved: **28** (44.44%)

---

## Rank 10: integer + random + variant

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 61 |
| Internal edges (removed) | 4 |
| Merged edges (unique) | 35 |
| Edge reduction | 26 (42.62%) |

### Individual Module Details

**integer:**
- Edges from this module: 26
- Dependents Relations: Primary = 6, All = 6
- Dependencies Relations: Primary = 20, All = 54

**random:**
- Edges from this module: 17
- Dependents Relations: Primary = 11, All = 19
- Dependencies Relations: Primary = 6, All = 15

**variant:**
- Edges from this module: 18
- Dependents Relations: Primary = 13, All = 17
- Dependencies Relations: Primary = 5, All = 21

### Summary

After merge, the combined module would have:
- **35** total outgoing edges (reduced from 61)
- Redundancy saved: 14 Dependents, 8 Dependencies
- Edges saved: **26** (42.62%)

---

