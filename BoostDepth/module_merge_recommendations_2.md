# Module Merge Recommendations

**Merge Count:** 2 modules per combination
**Top Recommendations:** 10
**Sorting:** By Edge Reduction (highest first)

## Overall Impact
| Metric | Value |
|--------|-------|
| Original total edges | 2764 |
| Reduced total edges | 2382 |
| Edge reduction | 382 (13.82%) |
| Modules merged | 20 |

---

## Rank 1: config + core

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 239 |
| Internal edges (removed) | 2 |
| Merged edges (unique) | 137 |
| Edge reduction | 102 (42.68%) |

### Individual Module Details

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
- **137** total outgoing edges (reduced from 239)
- Redundancy saved: 0 Dependents, 97 Dependencies
- Edges saved: **102** (42.68%)

---

## Rank 2: assert + throw_exception

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 166 |
| Internal edges (removed) | 2 |
| Merged edges (unique) | 102 |
| Edge reduction | 64 (38.55%) |

### Individual Module Details

**assert:**
- Edges from this module: 95
- Dependents Relations: Primary = 1, All = 1
- Dependencies Relations: Primary = 94, All = 129

**throw_exception:**
- Edges from this module: 71
- Dependents Relations: Primary = 2, All = 2
- Dependencies Relations: Primary = 69, All = 122

### Summary

After merge, the combined module would have:
- **102** total outgoing edges (reduced from 166)
- Redundancy saved: 1 Dependents, 61 Dependencies
- Edges saved: **64** (38.55%)

---

## Rank 3: mpl + type_traits

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 145 |
| Internal edges (removed) | 2 |
| Merged edges (unique) | 90 |
| Edge reduction | 55 (37.93%) |

### Individual Module Details

**mpl:**
- Edges from this module: 59
- Dependents Relations: Primary = 7, All = 10
- Dependencies Relations: Primary = 52, All = 76

**type_traits:**
- Edges from this module: 86
- Dependents Relations: Primary = 2, All = 2
- Dependencies Relations: Primary = 84, All = 107

### Summary

After merge, the combined module would have:
- **90** total outgoing edges (reduced from 145)
- Redundancy saved: 2 Dependents, 50 Dependencies
- Edges saved: **55** (37.93%)

---

## Rank 4: iterator + static_assert

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 107 |
| Internal edges (removed) | 0 |
| Merged edges (unique) | 74 |
| Edge reduction | 33 (30.84%) |

### Individual Module Details

**iterator:**
- Edges from this module: 47
- Dependents Relations: Primary = 10, All = 24
- Dependencies Relations: Primary = 37, All = 61

**static_assert:**
- Edges from this module: 60
- Dependents Relations: Primary = 1, All = 1
- Dependencies Relations: Primary = 59, All = 121

### Summary

After merge, the combined module would have:
- **74** total outgoing edges (reduced from 107)
- Redundancy saved: 1 Dependents, 26 Dependencies
- Edges saved: **33** (30.84%)

---

## Rank 5: preprocessor + utility

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 91 |
| Internal edges (removed) | 2 |
| Merged edges (unique) | 65 |
| Edge reduction | 26 (28.57%) |

### Individual Module Details

**preprocessor:**
- Edges from this module: 47
- Dependents Relations: Primary = 0, All = 0
- Dependencies Relations: Primary = 47, All = 94

**utility:**
- Edges from this module: 44
- Dependents Relations: Primary = 7, All = 8
- Dependencies Relations: Primary = 37, All = 84

### Summary

After merge, the combined module would have:
- **65** total outgoing edges (reduced from 91)
- Redundancy saved: 0 Dependents, 24 Dependencies
- Edges saved: **26** (28.57%)

---

## Rank 6: graph + range

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 85 |
| Internal edges (removed) | 2 |
| Merged edges (unique) | 60 |
| Edge reduction | 25 (29.41%) |

### Individual Module Details

**graph:**
- Edges from this module: 46
- Dependents Relations: Primary = 42, All = 71
- Dependencies Relations: Primary = 3, All = 6

**range:**
- Edges from this module: 39
- Dependents Relations: Primary = 17, All = 30
- Dependencies Relations: Primary = 22, All = 45

### Summary

After merge, the combined module would have:
- **60** total outgoing edges (reduced from 85)
- Redundancy saved: 17 Dependents, 0 Dependencies
- Edges saved: **25** (29.41%)

---

## Rank 7: serialization + spirit

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 70 |
| Internal edges (removed) | 2 |
| Merged edges (unique) | 48 |
| Edge reduction | 22 (31.43%) |

### Individual Module Details

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
- **48** total outgoing edges (reduced from 70)
- Redundancy saved: 18 Dependents, 2 Dependencies
- Edges saved: **22** (31.43%)

---

## Rank 8: function + smart_ptr

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 67 |
| Internal edges (removed) | 0 |
| Merged edges (unique) | 46 |
| Edge reduction | 21 (31.34%) |

### Individual Module Details

**function:**
- Edges from this module: 27
- Dependents Relations: Primary = 5, All = 6
- Dependencies Relations: Primary = 22, All = 71

**smart_ptr:**
- Edges from this module: 40
- Dependents Relations: Primary = 4, All = 5
- Dependencies Relations: Primary = 36, All = 64

### Summary

After merge, the combined module would have:
- **46** total outgoing edges (reduced from 67)
- Redundancy saved: 4 Dependents, 17 Dependencies
- Edges saved: **21** (31.34%)

---

## Rank 9: compute + xpressive

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 55 |
| Internal edges (removed) | 0 |
| Merged edges (unique) | 37 |
| Edge reduction | 18 (32.73%) |

### Individual Module Details

**compute:**
- Edges from this module: 31
- Dependents Relations: Primary = 29, All = 64
- Dependencies Relations: Primary = 2, All = 3

**xpressive:**
- Edges from this module: 24
- Dependents Relations: Primary = 22, All = 39
- Dependencies Relations: Primary = 2, All = 8

### Summary

After merge, the combined module would have:
- **37** total outgoing edges (reduced from 55)
- Redundancy saved: 18 Dependents, 0 Dependencies
- Edges saved: **18** (32.73%)

---

## Rank 10: fusion + proto

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 44 |
| Internal edges (removed) | 2 |
| Merged edges (unique) | 28 |
| Edge reduction | 16 (36.36%) |

### Individual Module Details

**fusion:**
- Edges from this module: 28
- Dependents Relations: Primary = 12, All = 21
- Dependencies Relations: Primary = 16, All = 67

**proto:**
- Edges from this module: 16
- Dependents Relations: Primary = 10, All = 31
- Dependencies Relations: Primary = 6, All = 22

### Summary

After merge, the combined module would have:
- **28** total outgoing edges (reduced from 44)
- Redundancy saved: 8 Dependents, 6 Dependencies
- Edges saved: **16** (36.36%)

---

