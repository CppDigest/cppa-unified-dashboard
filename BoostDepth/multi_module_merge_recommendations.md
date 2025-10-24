# Module Merge Recommendations

**Top Recommendations:** 10
**Sorting:** By Edge Reduction (highest first)
**Strategy:** Best merges across all merge counts (2-5 modules)

## Overall Impact
| Metric | Value |
|--------|-------|
| Original total edges | 2764 |
| Reduced total edges | 2504 |
| Edge reduction | 260 |
| Modules merged | 32 |

---

## Rank 1: mp11 + range

**Merge Count:** 2 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 59 |
| Internal edges (removed) | 0 |
| Merged edges (unique) | 57 |
| Edge reduction | 2 |

### Individual Module Details

**mp11:**
- Edges from this module: 20
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 20, All = 92

**range:**
- Edges from this module: 39
- Dependencies Relations: Primary = 17, All = 30
- Dependents Relations: Primary = 22, All = 45

### Summary

After merge, the combined module would have:
- **57** total outgoing edges (reduced from 59)
- Redundancy saved: 0 Dependents, 0 Dependencies
- Edges saved: **2**

---

## Rank 2: predef + serialization

**Merge Count:** 2 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 55 |
| Internal edges (removed) | 1 |
| Merged edges (unique) | 52 |
| Edge reduction | 3 |

### Individual Module Details

**predef:**
- Edges from this module: 21
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 21, All = 95

**serialization:**
- Edges from this module: 34
- Dependencies Relations: Primary = 23, All = 57
- Dependents Relations: Primary = 11, All = 16

### Summary

After merge, the combined module would have:
- **52** total outgoing edges (reduced from 55)
- Redundancy saved: 0 Dependents, 0 Dependencies
- Edges saved: **3**

---

## Rank 3: container_hash + fusion

**Merge Count:** 2 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 51 |
| Internal edges (removed) | 1 |
| Merged edges (unique) | 48 |
| Edge reduction | 3 |

### Individual Module Details

**container_hash:**
- Edges from this module: 23
- Dependencies Relations: Primary = 3, All = 3
- Dependents Relations: Primary = 20, All = 81

**fusion:**
- Edges from this module: 28
- Dependencies Relations: Primary = 12, All = 21
- Dependents Relations: Primary = 16, All = 67

### Summary

After merge, the combined module would have:
- **48** total outgoing edges (reduced from 51)
- Redundancy saved: 1 Dependents, 0 Dependencies
- Edges saved: **3**

---

## Rank 4: detail + intrusive + typeof

**Merge Count:** 3 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 50 |
| Internal edges (removed) | 0 |
| Merged edges (unique) | 47 |
| Edge reduction | 3 |

### Individual Module Details

**detail:**
- Edges from this module: 22
- Dependencies Relations: Primary = 5, All = 7
- Dependents Relations: Primary = 17, All = 73

**intrusive:**
- Edges from this module: 11
- Dependencies Relations: Primary = 3, All = 3
- Dependents Relations: Primary = 8, All = 47

**typeof:**
- Edges from this module: 17
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 16, All = 72

### Summary

After merge, the combined module would have:
- **47** total outgoing edges (reduced from 50)
- Redundancy saved: 2 Dependents, 1 Dependencies
- Edges saved: **3**

---

## Rank 5: algorithm + config + preprocessor

**Merge Count:** 3 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 209 |
| Internal edges (removed) | 1 |
| Merged edges (unique) | 139 |
| Edge reduction | 70 |

### Individual Module Details

**algorithm:**
- Edges from this module: 25
- Dependencies Relations: Primary = 17, All = 33
- Dependents Relations: Primary = 8, All = 36

**config:**
- Edges from this module: 137
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 137, All = 141

**preprocessor:**
- Edges from this module: 47
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 47, All = 94

### Summary

After merge, the combined module would have:
- **139** total outgoing edges (reduced from 209)
- Redundancy saved: 0 Dependents, 52 Dependencies
- Edges saved: **70**

---

## Rank 6: container + filesystem + parameter

**Merge Count:** 3 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 57 |
| Internal edges (removed) | 0 |
| Merged edges (unique) | 51 |
| Edge reduction | 6 |

### Individual Module Details

**container:**
- Edges from this module: 14
- Dependencies Relations: Primary = 4, All = 4
- Dependents Relations: Primary = 10, All = 44

**filesystem:**
- Edges from this module: 23
- Dependencies Relations: Primary = 14, All = 32
- Dependents Relations: Primary = 9, All = 12

**parameter:**
- Edges from this module: 20
- Dependencies Relations: Primary = 10, All = 23
- Dependents Relations: Primary = 10, All = 15

### Summary

After merge, the combined module would have:
- **51** total outgoing edges (reduced from 57)
- Redundancy saved: 5 Dependents, 1 Dependencies
- Edges saved: **6**

---

## Rank 7: io + iterator + system + winapi

**Merge Count:** 4 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 97 |
| Internal edges (removed) | 1 |
| Merged edges (unique) | 72 |
| Edge reduction | 25 |

### Individual Module Details

**io:**
- Edges from this module: 13
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 12, All = 86

**iterator:**
- Edges from this module: 47
- Dependencies Relations: Primary = 10, All = 24
- Dependents Relations: Primary = 37, All = 61

**system:**
- Edges from this module: 22
- Dependencies Relations: Primary = 5, All = 7
- Dependents Relations: Primary = 17, All = 47

**winapi:**
- Edges from this module: 15
- Dependencies Relations: Primary = 2, All = 2
- Dependents Relations: Primary = 13, All = 58

### Summary

After merge, the combined module would have:
- **72** total outgoing edges (reduced from 97)
- Redundancy saved: 3 Dependents, 19 Dependencies
- Edges saved: **25**

---

## Rank 8: function_types + move + throw_exception + type_index

**Merge Count:** 4 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 117 |
| Internal edges (removed) | 1 |
| Merged edges (unique) | 87 |
| Edge reduction | 30 |

### Individual Module Details

**function_types:**
- Edges from this module: 15
- Dependencies Relations: Primary = 6, All = 12
- Dependents Relations: Primary = 9, All = 70

**move:**
- Edges from this module: 18
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 17, All = 59

**throw_exception:**
- Edges from this module: 71
- Dependencies Relations: Primary = 2, All = 2
- Dependents Relations: Primary = 69, All = 122

**type_index:**
- Edges from this module: 13
- Dependencies Relations: Primary = 3, All = 6
- Dependents Relations: Primary = 10, All = 31

### Summary

After merge, the combined module would have:
- **87** total outgoing edges (reduced from 117)
- Redundancy saved: 3 Dependents, 24 Dependencies
- Edges saved: **30**

---

## Rank 9: array + assert + lexical_cast + numeric~conversion

**Merge Count:** 4 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 143 |
| Internal edges (removed) | 1 |
| Merged edges (unique) | 102 |
| Edge reduction | 41 |

### Individual Module Details

**array:**
- Edges from this module: 15
- Dependencies Relations: Primary = 4, All = 4
- Dependents Relations: Primary = 11, All = 47

**assert:**
- Edges from this module: 95
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 94, All = 129

**lexical_cast:**
- Edges from this module: 18
- Dependencies Relations: Primary = 4, All = 8
- Dependents Relations: Primary = 14, All = 40

**numeric~conversion:**
- Edges from this module: 15
- Dependencies Relations: Primary = 7, All = 13
- Dependents Relations: Primary = 8, All = 37

### Summary

After merge, the combined module would have:
- **102** total outgoing edges (reduced from 143)
- Redundancy saved: 6 Dependents, 29 Dependencies
- Edges saved: **41**

---

## Rank 10: bind + exception + function + smart_ptr + static_assert

**Merge Count:** 5 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 159 |
| Internal edges (removed) | 2 |
| Merged edges (unique) | 82 |
| Edge reduction | 77 |

### Individual Module Details

**bind:**
- Edges from this module: 17
- Dependencies Relations: Primary = 2, All = 5
- Dependents Relations: Primary = 15, All = 72

**exception:**
- Edges from this module: 15
- Dependencies Relations: Primary = 7, All = 8
- Dependents Relations: Primary = 8, All = 40

**function:**
- Edges from this module: 27
- Dependencies Relations: Primary = 5, All = 6
- Dependents Relations: Primary = 22, All = 71

**smart_ptr:**
- Edges from this module: 40
- Dependencies Relations: Primary = 4, All = 5
- Dependents Relations: Primary = 36, All = 64

**static_assert:**
- Edges from this module: 60
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 59, All = 121

### Summary

After merge, the combined module would have:
- **82** total outgoing edges (reduced from 159)
- Redundancy saved: 11 Dependents, 59 Dependencies
- Edges saved: **77**

---

