# Module Merge Recommendations

**Top Recommendations:** 10
**Sorting:** By Edge Reduction (highest first)
**Strategy:** Best merges across all merge counts (2-5 modules)

---

## Rank 1: assert + config + core + throw_exception + type_traits

**Merge Count:** 5 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 491 |
| Internal edges (removed) | 7 |
| Merged edges (unique) | 135 |
| Edge reduction | 356 |

### Individual Module Details

**assert:**
- Edges from this module: 95
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 94, All = 129

**config:**
- Edges from this module: 137
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 137, All = 141

**core:**
- Edges from this module: 102
- Dependencies Relations: Primary = 4, All = 4
- Dependents Relations: Primary = 98, All = 115

**throw_exception:**
- Edges from this module: 71
- Dependencies Relations: Primary = 2, All = 2
- Dependents Relations: Primary = 69, All = 122

**type_traits:**
- Edges from this module: 86
- Dependencies Relations: Primary = 2, All = 2
- Dependents Relations: Primary = 84, All = 107

### Summary

After merge, the combined module would have:
- **135** total outgoing edges (reduced from 491)
- Redundancy saved: 5 Dependents, 343 Dependencies
- Edges saved: **356**

---

## Rank 2: assert + config + core + static_assert + type_traits

**Merge Count:** 5 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 480 |
| Internal edges (removed) | 7 |
| Merged edges (unique) | 135 |
| Edge reduction | 345 |

### Individual Module Details

**assert:**
- Edges from this module: 95
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 94, All = 129

**config:**
- Edges from this module: 137
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 137, All = 141

**core:**
- Edges from this module: 102
- Dependencies Relations: Primary = 4, All = 4
- Dependents Relations: Primary = 98, All = 115

**static_assert:**
- Edges from this module: 60
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 59, All = 121

**type_traits:**
- Edges from this module: 86
- Dependencies Relations: Primary = 2, All = 2
- Dependents Relations: Primary = 84, All = 107

### Summary

After merge, the combined module would have:
- **135** total outgoing edges (reduced from 480)
- Redundancy saved: 4 Dependents, 333 Dependencies
- Edges saved: **345**

---

## Rank 3: assert + config + core + mpl + type_traits

**Merge Count:** 5 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 479 |
| Internal edges (removed) | 7 |
| Merged edges (unique) | 138 |
| Edge reduction | 341 |

### Individual Module Details

**assert:**
- Edges from this module: 95
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 94, All = 129

**config:**
- Edges from this module: 137
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 137, All = 141

**core:**
- Edges from this module: 102
- Dependencies Relations: Primary = 4, All = 4
- Dependents Relations: Primary = 98, All = 115

**mpl:**
- Edges from this module: 59
- Dependencies Relations: Primary = 7, All = 10
- Dependents Relations: Primary = 52, All = 76

**type_traits:**
- Edges from this module: 86
- Dependencies Relations: Primary = 2, All = 2
- Dependents Relations: Primary = 84, All = 107

### Summary

After merge, the combined module would have:
- **138** total outgoing edges (reduced from 479)
- Redundancy saved: 5 Dependents, 325 Dependencies
- Edges saved: **341**

---

## Rank 4: assert + config + core + iterator + type_traits

**Merge Count:** 5 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 467 |
| Internal edges (removed) | 7 |
| Merged edges (unique) | 136 |
| Edge reduction | 331 |

### Individual Module Details

**assert:**
- Edges from this module: 95
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 94, All = 129

**config:**
- Edges from this module: 137
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 137, All = 141

**core:**
- Edges from this module: 102
- Dependencies Relations: Primary = 4, All = 4
- Dependents Relations: Primary = 98, All = 115

**iterator:**
- Edges from this module: 47
- Dependencies Relations: Primary = 10, All = 24
- Dependents Relations: Primary = 37, All = 61

**type_traits:**
- Edges from this module: 86
- Dependencies Relations: Primary = 2, All = 2
- Dependents Relations: Primary = 84, All = 107

### Summary

After merge, the combined module would have:
- **136** total outgoing edges (reduced from 467)
- Redundancy saved: 4 Dependents, 311 Dependencies
- Edges saved: **331**

---

## Rank 5: assert + config + core + static_assert + throw_exception

**Merge Count:** 5 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 465 |
| Internal edges (removed) | 8 |
| Merged edges (unique) | 135 |
| Edge reduction | 330 |

### Individual Module Details

**assert:**
- Edges from this module: 95
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 94, All = 129

**config:**
- Edges from this module: 137
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 137, All = 141

**core:**
- Edges from this module: 102
- Dependencies Relations: Primary = 4, All = 4
- Dependents Relations: Primary = 98, All = 115

**static_assert:**
- Edges from this module: 60
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 59, All = 121

**throw_exception:**
- Edges from this module: 71
- Dependencies Relations: Primary = 2, All = 2
- Dependents Relations: Primary = 69, All = 122

### Summary

After merge, the combined module would have:
- **135** total outgoing edges (reduced from 465)
- Redundancy saved: 4 Dependents, 318 Dependencies
- Edges saved: **330**

---

## Rank 6: assert + config + core + preprocessor + type_traits

**Merge Count:** 5 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 467 |
| Internal edges (removed) | 4 |
| Merged edges (unique) | 139 |
| Edge reduction | 328 |

### Individual Module Details

**assert:**
- Edges from this module: 95
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 94, All = 129

**config:**
- Edges from this module: 137
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 137, All = 141

**core:**
- Edges from this module: 102
- Dependencies Relations: Primary = 4, All = 4
- Dependents Relations: Primary = 98, All = 115

**preprocessor:**
- Edges from this module: 47
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 47, All = 94

**type_traits:**
- Edges from this module: 86
- Dependencies Relations: Primary = 2, All = 2
- Dependents Relations: Primary = 84, All = 107

### Summary

After merge, the combined module would have:
- **139** total outgoing edges (reduced from 467)
- Redundancy saved: 3 Dependents, 318 Dependencies
- Edges saved: **328**

---

## Rank 7: assert + config + core + type_traits + utility

**Merge Count:** 5 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 464 |
| Internal edges (removed) | 8 |
| Merged edges (unique) | 136 |
| Edge reduction | 328 |

### Individual Module Details

**assert:**
- Edges from this module: 95
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 94, All = 129

**config:**
- Edges from this module: 137
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 137, All = 141

**core:**
- Edges from this module: 102
- Dependencies Relations: Primary = 4, All = 4
- Dependents Relations: Primary = 98, All = 115

**type_traits:**
- Edges from this module: 86
- Dependencies Relations: Primary = 2, All = 2
- Dependents Relations: Primary = 84, All = 107

**utility:**
- Edges from this module: 44
- Dependencies Relations: Primary = 7, All = 8
- Dependents Relations: Primary = 37, All = 84

### Summary

After merge, the combined module would have:
- **136** total outgoing edges (reduced from 464)
- Redundancy saved: 6 Dependents, 311 Dependencies
- Edges saved: **328**

---

## Rank 8: assert + config + core + mpl + throw_exception

**Merge Count:** 5 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 464 |
| Internal edges (removed) | 8 |
| Merged edges (unique) | 138 |
| Edge reduction | 326 |

### Individual Module Details

**assert:**
- Edges from this module: 95
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 94, All = 129

**config:**
- Edges from this module: 137
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 137, All = 141

**core:**
- Edges from this module: 102
- Dependencies Relations: Primary = 4, All = 4
- Dependents Relations: Primary = 98, All = 115

**mpl:**
- Edges from this module: 59
- Dependencies Relations: Primary = 7, All = 10
- Dependents Relations: Primary = 52, All = 76

**throw_exception:**
- Edges from this module: 71
- Dependencies Relations: Primary = 2, All = 2
- Dependents Relations: Primary = 69, All = 122

### Summary

After merge, the combined module would have:
- **138** total outgoing edges (reduced from 464)
- Redundancy saved: 5 Dependents, 310 Dependencies
- Edges saved: **326**

---

## Rank 9: assert + config + core + smart_ptr + type_traits

**Merge Count:** 5 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 460 |
| Internal edges (removed) | 7 |
| Merged edges (unique) | 135 |
| Edge reduction | 325 |

### Individual Module Details

**assert:**
- Edges from this module: 95
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 94, All = 129

**config:**
- Edges from this module: 137
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 137, All = 141

**core:**
- Edges from this module: 102
- Dependencies Relations: Primary = 4, All = 4
- Dependents Relations: Primary = 98, All = 115

**smart_ptr:**
- Edges from this module: 40
- Dependencies Relations: Primary = 4, All = 5
- Dependents Relations: Primary = 36, All = 64

**type_traits:**
- Edges from this module: 86
- Dependencies Relations: Primary = 2, All = 2
- Dependents Relations: Primary = 84, All = 107

### Summary

After merge, the combined module would have:
- **135** total outgoing edges (reduced from 460)
- Redundancy saved: 6 Dependents, 310 Dependencies
- Edges saved: **325**

---

## Rank 10: assert + config + core + range + type_traits

**Merge Count:** 5 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 459 |
| Internal edges (removed) | 8 |
| Merged edges (unique) | 136 |
| Edge reduction | 323 |

### Individual Module Details

**assert:**
- Edges from this module: 95
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 94, All = 129

**config:**
- Edges from this module: 137
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 137, All = 141

**core:**
- Edges from this module: 102
- Dependencies Relations: Primary = 4, All = 4
- Dependents Relations: Primary = 98, All = 115

**range:**
- Edges from this module: 39
- Dependencies Relations: Primary = 17, All = 30
- Dependents Relations: Primary = 22, All = 45

**type_traits:**
- Edges from this module: 86
- Dependencies Relations: Primary = 2, All = 2
- Dependents Relations: Primary = 84, All = 107

### Summary

After merge, the combined module would have:
- **136** total outgoing edges (reduced from 459)
- Redundancy saved: 6 Dependents, 296 Dependencies
- Edges saved: **323**

---

## Rank 11: assert + config + core + type_traits

**Merge Count:** 4 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 420 |
| Internal edges (removed) | 4 |
| Merged edges (unique) | 136 |
| Edge reduction | 284 |

### Individual Module Details

**assert:**
- Edges from this module: 95
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 94, All = 129

**config:**
- Edges from this module: 137
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 137, All = 141

**core:**
- Edges from this module: 102
- Dependencies Relations: Primary = 4, All = 4
- Dependents Relations: Primary = 98, All = 115

**type_traits:**
- Edges from this module: 86
- Dependencies Relations: Primary = 2, All = 2
- Dependents Relations: Primary = 84, All = 107

### Summary

After merge, the combined module would have:
- **136** total outgoing edges (reduced from 420)
- Redundancy saved: 3 Dependents, 274 Dependencies
- Edges saved: **284**

---

## Rank 12: assert + config + core + throw_exception

**Merge Count:** 4 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 405 |
| Internal edges (removed) | 6 |
| Merged edges (unique) | 136 |
| Edge reduction | 269 |

### Individual Module Details

**assert:**
- Edges from this module: 95
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 94, All = 129

**config:**
- Edges from this module: 137
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 137, All = 141

**core:**
- Edges from this module: 102
- Dependencies Relations: Primary = 4, All = 4
- Dependents Relations: Primary = 98, All = 115

**throw_exception:**
- Edges from this module: 71
- Dependencies Relations: Primary = 2, All = 2
- Dependents Relations: Primary = 69, All = 122

### Summary

After merge, the combined module would have:
- **136** total outgoing edges (reduced from 405)
- Redundancy saved: 3 Dependents, 259 Dependencies
- Edges saved: **269**

---

## Rank 13: config + core + throw_exception + type_traits

**Merge Count:** 4 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 396 |
| Internal edges (removed) | 4 |
| Merged edges (unique) | 135 |
| Edge reduction | 261 |

### Individual Module Details

**config:**
- Edges from this module: 137
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 137, All = 141

**core:**
- Edges from this module: 102
- Dependencies Relations: Primary = 4, All = 4
- Dependents Relations: Primary = 98, All = 115

**throw_exception:**
- Edges from this module: 71
- Dependencies Relations: Primary = 2, All = 2
- Dependents Relations: Primary = 69, All = 122

**type_traits:**
- Edges from this module: 86
- Dependencies Relations: Primary = 2, All = 2
- Dependents Relations: Primary = 84, All = 107

### Summary

After merge, the combined module would have:
- **135** total outgoing edges (reduced from 396)
- Redundancy saved: 4 Dependents, 250 Dependencies
- Edges saved: **261**

---

## Rank 14: assert + config + core + static_assert

**Merge Count:** 4 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 394 |
| Internal edges (removed) | 5 |
| Merged edges (unique) | 136 |
| Edge reduction | 258 |

### Individual Module Details

**assert:**
- Edges from this module: 95
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 94, All = 129

**config:**
- Edges from this module: 137
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 137, All = 141

**core:**
- Edges from this module: 102
- Dependencies Relations: Primary = 4, All = 4
- Dependents Relations: Primary = 98, All = 115

**static_assert:**
- Edges from this module: 60
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 59, All = 121

### Summary

After merge, the combined module would have:
- **136** total outgoing edges (reduced from 394)
- Redundancy saved: 2 Dependents, 249 Dependencies
- Edges saved: **258**

---

## Rank 15: assert + config + core + mpl

**Merge Count:** 4 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 393 |
| Internal edges (removed) | 5 |
| Merged edges (unique) | 139 |
| Edge reduction | 254 |

### Individual Module Details

**assert:**
- Edges from this module: 95
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 94, All = 129

**config:**
- Edges from this module: 137
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 137, All = 141

**core:**
- Edges from this module: 102
- Dependencies Relations: Primary = 4, All = 4
- Dependents Relations: Primary = 98, All = 115

**mpl:**
- Edges from this module: 59
- Dependencies Relations: Primary = 7, All = 10
- Dependents Relations: Primary = 52, All = 76

### Summary

After merge, the combined module would have:
- **139** total outgoing edges (reduced from 393)
- Redundancy saved: 3 Dependents, 241 Dependencies
- Edges saved: **254**

---

## Rank 16: assert + config + throw_exception + type_traits

**Merge Count:** 4 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 389 |
| Internal edges (removed) | 4 |
| Merged edges (unique) | 136 |
| Edge reduction | 253 |

### Individual Module Details

**assert:**
- Edges from this module: 95
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 94, All = 129

**config:**
- Edges from this module: 137
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 137, All = 141

**throw_exception:**
- Edges from this module: 71
- Dependencies Relations: Primary = 2, All = 2
- Dependents Relations: Primary = 69, All = 122

**type_traits:**
- Edges from this module: 86
- Dependencies Relations: Primary = 2, All = 2
- Dependents Relations: Primary = 84, All = 107

### Summary

After merge, the combined module would have:
- **136** total outgoing edges (reduced from 389)
- Redundancy saved: 2 Dependents, 245 Dependencies
- Edges saved: **253**

---

## Rank 17: config + core + static_assert + type_traits

**Merge Count:** 4 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 385 |
| Internal edges (removed) | 5 |
| Merged edges (unique) | 135 |
| Edge reduction | 250 |

### Individual Module Details

**config:**
- Edges from this module: 137
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 137, All = 141

**core:**
- Edges from this module: 102
- Dependencies Relations: Primary = 4, All = 4
- Dependents Relations: Primary = 98, All = 115

**static_assert:**
- Edges from this module: 60
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 59, All = 121

**type_traits:**
- Edges from this module: 86
- Dependencies Relations: Primary = 2, All = 2
- Dependents Relations: Primary = 84, All = 107

### Summary

After merge, the combined module would have:
- **135** total outgoing edges (reduced from 385)
- Redundancy saved: 3 Dependents, 240 Dependencies
- Edges saved: **250**

---

## Rank 18: config + core + mpl + type_traits

**Merge Count:** 4 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 384 |
| Internal edges (removed) | 5 |
| Merged edges (unique) | 138 |
| Edge reduction | 246 |

### Individual Module Details

**config:**
- Edges from this module: 137
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 137, All = 141

**core:**
- Edges from this module: 102
- Dependencies Relations: Primary = 4, All = 4
- Dependents Relations: Primary = 98, All = 115

**mpl:**
- Edges from this module: 59
- Dependencies Relations: Primary = 7, All = 10
- Dependents Relations: Primary = 52, All = 76

**type_traits:**
- Edges from this module: 86
- Dependencies Relations: Primary = 2, All = 2
- Dependents Relations: Primary = 84, All = 107

### Summary

After merge, the combined module would have:
- **138** total outgoing edges (reduced from 384)
- Redundancy saved: 4 Dependents, 232 Dependencies
- Edges saved: **246**

---

## Rank 19: assert + config + core + iterator

**Merge Count:** 4 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 381 |
| Internal edges (removed) | 5 |
| Merged edges (unique) | 137 |
| Edge reduction | 244 |

### Individual Module Details

**assert:**
- Edges from this module: 95
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 94, All = 129

**config:**
- Edges from this module: 137
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 137, All = 141

**core:**
- Edges from this module: 102
- Dependencies Relations: Primary = 4, All = 4
- Dependents Relations: Primary = 98, All = 115

**iterator:**
- Edges from this module: 47
- Dependencies Relations: Primary = 10, All = 24
- Dependents Relations: Primary = 37, All = 61

### Summary

After merge, the combined module would have:
- **137** total outgoing edges (reduced from 381)
- Redundancy saved: 2 Dependents, 227 Dependencies
- Edges saved: **244**

---

## Rank 20: assert + config + static_assert + type_traits

**Merge Count:** 4 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 378 |
| Internal edges (removed) | 4 |
| Merged edges (unique) | 136 |
| Edge reduction | 242 |

### Individual Module Details

**assert:**
- Edges from this module: 95
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 94, All = 129

**config:**
- Edges from this module: 137
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 137, All = 141

**static_assert:**
- Edges from this module: 60
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 59, All = 121

**type_traits:**
- Edges from this module: 86
- Dependencies Relations: Primary = 2, All = 2
- Dependents Relations: Primary = 84, All = 107

### Summary

After merge, the combined module would have:
- **136** total outgoing edges (reduced from 378)
- Redundancy saved: 2 Dependents, 235 Dependencies
- Edges saved: **242**

---

## Rank 21: assert + config + core

**Merge Count:** 3 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 334 |
| Internal edges (removed) | 3 |
| Merged edges (unique) | 137 |
| Edge reduction | 197 |

### Individual Module Details

**assert:**
- Edges from this module: 95
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 94, All = 129

**config:**
- Edges from this module: 137
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 137, All = 141

**core:**
- Edges from this module: 102
- Dependencies Relations: Primary = 4, All = 4
- Dependents Relations: Primary = 98, All = 115

### Summary

After merge, the combined module would have:
- **137** total outgoing edges (reduced from 334)
- Redundancy saved: 1 Dependents, 190 Dependencies
- Edges saved: **197**

---

## Rank 22: config + core + type_traits

**Merge Count:** 3 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 325 |
| Internal edges (removed) | 2 |
| Merged edges (unique) | 136 |
| Edge reduction | 189 |

### Individual Module Details

**config:**
- Edges from this module: 137
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 137, All = 141

**core:**
- Edges from this module: 102
- Dependencies Relations: Primary = 4, All = 4
- Dependents Relations: Primary = 98, All = 115

**type_traits:**
- Edges from this module: 86
- Dependencies Relations: Primary = 2, All = 2
- Dependents Relations: Primary = 84, All = 107

### Summary

After merge, the combined module would have:
- **136** total outgoing edges (reduced from 325)
- Redundancy saved: 2 Dependents, 181 Dependencies
- Edges saved: **189**

---

## Rank 23: assert + config + type_traits

**Merge Count:** 3 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 318 |
| Internal edges (removed) | 2 |
| Merged edges (unique) | 137 |
| Edge reduction | 181 |

### Individual Module Details

**assert:**
- Edges from this module: 95
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 94, All = 129

**config:**
- Edges from this module: 137
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 137, All = 141

**type_traits:**
- Edges from this module: 86
- Dependencies Relations: Primary = 2, All = 2
- Dependents Relations: Primary = 84, All = 107

### Summary

After merge, the combined module would have:
- **137** total outgoing edges (reduced from 318)
- Redundancy saved: 1 Dependents, 176 Dependencies
- Edges saved: **181**

---

## Rank 24: config + core + throw_exception

**Merge Count:** 3 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 310 |
| Internal edges (removed) | 3 |
| Merged edges (unique) | 136 |
| Edge reduction | 174 |

### Individual Module Details

**config:**
- Edges from this module: 137
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 137, All = 141

**core:**
- Edges from this module: 102
- Dependencies Relations: Primary = 4, All = 4
- Dependents Relations: Primary = 98, All = 115

**throw_exception:**
- Edges from this module: 71
- Dependencies Relations: Primary = 2, All = 2
- Dependents Relations: Primary = 69, All = 122

### Summary

After merge, the combined module would have:
- **136** total outgoing edges (reduced from 310)
- Redundancy saved: 2 Dependents, 166 Dependencies
- Edges saved: **174**

---

## Rank 25: assert + config + throw_exception

**Merge Count:** 3 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 303 |
| Internal edges (removed) | 3 |
| Merged edges (unique) | 137 |
| Edge reduction | 166 |

### Individual Module Details

**assert:**
- Edges from this module: 95
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 94, All = 129

**config:**
- Edges from this module: 137
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 137, All = 141

**throw_exception:**
- Edges from this module: 71
- Dependencies Relations: Primary = 2, All = 2
- Dependents Relations: Primary = 69, All = 122

### Summary

After merge, the combined module would have:
- **137** total outgoing edges (reduced from 303)
- Redundancy saved: 1 Dependents, 161 Dependencies
- Edges saved: **166**

---

## Rank 26: config + core + static_assert

**Merge Count:** 3 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 299 |
| Internal edges (removed) | 3 |
| Merged edges (unique) | 136 |
| Edge reduction | 163 |

### Individual Module Details

**config:**
- Edges from this module: 137
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 137, All = 141

**core:**
- Edges from this module: 102
- Dependencies Relations: Primary = 4, All = 4
- Dependents Relations: Primary = 98, All = 115

**static_assert:**
- Edges from this module: 60
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 59, All = 121

### Summary

After merge, the combined module would have:
- **136** total outgoing edges (reduced from 299)
- Redundancy saved: 1 Dependents, 156 Dependencies
- Edges saved: **163**

---

## Rank 27: config + core + mpl

**Merge Count:** 3 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 298 |
| Internal edges (removed) | 3 |
| Merged edges (unique) | 139 |
| Edge reduction | 159 |

### Individual Module Details

**config:**
- Edges from this module: 137
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 137, All = 141

**core:**
- Edges from this module: 102
- Dependencies Relations: Primary = 4, All = 4
- Dependents Relations: Primary = 98, All = 115

**mpl:**
- Edges from this module: 59
- Dependencies Relations: Primary = 7, All = 10
- Dependents Relations: Primary = 52, All = 76

### Summary

After merge, the combined module would have:
- **139** total outgoing edges (reduced from 298)
- Redundancy saved: 2 Dependents, 148 Dependencies
- Edges saved: **159**

---

## Rank 28: config + throw_exception + type_traits

**Merge Count:** 3 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 294 |
| Internal edges (removed) | 2 |
| Merged edges (unique) | 136 |
| Edge reduction | 158 |

### Individual Module Details

**config:**
- Edges from this module: 137
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 137, All = 141

**throw_exception:**
- Edges from this module: 71
- Dependencies Relations: Primary = 2, All = 2
- Dependents Relations: Primary = 69, All = 122

**type_traits:**
- Edges from this module: 86
- Dependencies Relations: Primary = 2, All = 2
- Dependents Relations: Primary = 84, All = 107

### Summary

After merge, the combined module would have:
- **136** total outgoing edges (reduced from 294)
- Redundancy saved: 1 Dependents, 152 Dependencies
- Edges saved: **158**

---

## Rank 29: assert + core + type_traits

**Merge Count:** 3 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 283 |
| Internal edges (removed) | 1 |
| Merged edges (unique) | 126 |
| Edge reduction | 157 |

### Individual Module Details

**assert:**
- Edges from this module: 95
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 94, All = 129

**core:**
- Edges from this module: 102
- Dependencies Relations: Primary = 4, All = 4
- Dependents Relations: Primary = 98, All = 115

**type_traits:**
- Edges from this module: 86
- Dependencies Relations: Primary = 2, All = 2
- Dependents Relations: Primary = 84, All = 107

### Summary

After merge, the combined module would have:
- **126** total outgoing edges (reduced from 283)
- Redundancy saved: 3 Dependents, 151 Dependencies
- Edges saved: **157**

---

## Rank 30: assert + config + static_assert

**Merge Count:** 3 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 292 |
| Internal edges (removed) | 2 |
| Merged edges (unique) | 137 |
| Edge reduction | 155 |

### Individual Module Details

**assert:**
- Edges from this module: 95
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 94, All = 129

**config:**
- Edges from this module: 137
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 137, All = 141

**static_assert:**
- Edges from this module: 60
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 59, All = 121

### Summary

After merge, the combined module would have:
- **137** total outgoing edges (reduced from 292)
- Redundancy saved: 1 Dependents, 151 Dependencies
- Edges saved: **155**

---

## Rank 31: config + core

**Merge Count:** 2 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 239 |
| Internal edges (removed) | 1 |
| Merged edges (unique) | 137 |
| Edge reduction | 102 |

### Individual Module Details

**config:**
- Edges from this module: 137
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 137, All = 141

**core:**
- Edges from this module: 102
- Dependencies Relations: Primary = 4, All = 4
- Dependents Relations: Primary = 98, All = 115

### Summary

After merge, the combined module would have:
- **137** total outgoing edges (reduced from 239)
- Redundancy saved: 0 Dependents, 97 Dependencies
- Edges saved: **102**

---

## Rank 32: assert + config

**Merge Count:** 2 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 232 |
| Internal edges (removed) | 1 |
| Merged edges (unique) | 138 |
| Edge reduction | 94 |

### Individual Module Details

**assert:**
- Edges from this module: 95
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 94, All = 129

**config:**
- Edges from this module: 137
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 137, All = 141

### Summary

After merge, the combined module would have:
- **138** total outgoing edges (reduced from 232)
- Redundancy saved: 0 Dependents, 92 Dependencies
- Edges saved: **94**

---

## Rank 33: config + type_traits

**Merge Count:** 2 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 223 |
| Internal edges (removed) | 1 |
| Merged edges (unique) | 137 |
| Edge reduction | 86 |

### Individual Module Details

**config:**
- Edges from this module: 137
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 137, All = 141

**type_traits:**
- Edges from this module: 86
- Dependencies Relations: Primary = 2, All = 2
- Dependents Relations: Primary = 84, All = 107

### Summary

After merge, the combined module would have:
- **137** total outgoing edges (reduced from 223)
- Redundancy saved: 0 Dependents, 83 Dependencies
- Edges saved: **86**

---

## Rank 34: assert + core

**Merge Count:** 2 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 197 |
| Internal edges (removed) | 1 |
| Merged edges (unique) | 121 |
| Edge reduction | 76 |

### Individual Module Details

**assert:**
- Edges from this module: 95
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 94, All = 129

**core:**
- Edges from this module: 102
- Dependencies Relations: Primary = 4, All = 4
- Dependents Relations: Primary = 98, All = 115

### Summary

After merge, the combined module would have:
- **121** total outgoing edges (reduced from 197)
- Redundancy saved: 1 Dependents, 72 Dependencies
- Edges saved: **76**

---

## Rank 35: core + type_traits

**Merge Count:** 2 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 188 |
| Internal edges (removed) | 0 |
| Merged edges (unique) | 113 |
| Edge reduction | 75 |

### Individual Module Details

**core:**
- Edges from this module: 102
- Dependencies Relations: Primary = 4, All = 4
- Dependents Relations: Primary = 98, All = 115

**type_traits:**
- Edges from this module: 86
- Dependencies Relations: Primary = 2, All = 2
- Dependents Relations: Primary = 84, All = 107

### Summary

After merge, the combined module would have:
- **113** total outgoing edges (reduced from 188)
- Redundancy saved: 2 Dependents, 73 Dependencies
- Edges saved: **75**

---

## Rank 36: config + throw_exception

**Merge Count:** 2 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 208 |
| Internal edges (removed) | 1 |
| Merged edges (unique) | 136 |
| Edge reduction | 72 |

### Individual Module Details

**config:**
- Edges from this module: 137
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 137, All = 141

**throw_exception:**
- Edges from this module: 71
- Dependencies Relations: Primary = 2, All = 2
- Dependents Relations: Primary = 69, All = 122

### Summary

After merge, the combined module would have:
- **136** total outgoing edges (reduced from 208)
- Redundancy saved: 0 Dependents, 69 Dependencies
- Edges saved: **72**

---

## Rank 37: assert + throw_exception

**Merge Count:** 2 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 166 |
| Internal edges (removed) | 1 |
| Merged edges (unique) | 102 |
| Edge reduction | 64 |

### Individual Module Details

**assert:**
- Edges from this module: 95
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 94, All = 129

**throw_exception:**
- Edges from this module: 71
- Dependencies Relations: Primary = 2, All = 2
- Dependents Relations: Primary = 69, All = 122

### Summary

After merge, the combined module would have:
- **102** total outgoing edges (reduced from 166)
- Redundancy saved: 1 Dependents, 61 Dependencies
- Edges saved: **64**

---

## Rank 38: config + static_assert

**Merge Count:** 2 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 197 |
| Internal edges (removed) | 1 |
| Merged edges (unique) | 136 |
| Edge reduction | 61 |

### Individual Module Details

**config:**
- Edges from this module: 137
- Dependencies Relations: Primary = 0, All = 0
- Dependents Relations: Primary = 137, All = 141

**static_assert:**
- Edges from this module: 60
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 59, All = 121

### Summary

After merge, the combined module would have:
- **136** total outgoing edges (reduced from 197)
- Redundancy saved: 0 Dependents, 59 Dependencies
- Edges saved: **61**

---

## Rank 39: core + throw_exception

**Merge Count:** 2 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 173 |
| Internal edges (removed) | 1 |
| Merged edges (unique) | 112 |
| Edge reduction | 61 |

### Individual Module Details

**core:**
- Edges from this module: 102
- Dependencies Relations: Primary = 4, All = 4
- Dependents Relations: Primary = 98, All = 115

**throw_exception:**
- Edges from this module: 71
- Dependencies Relations: Primary = 2, All = 2
- Dependents Relations: Primary = 69, All = 122

### Summary

After merge, the combined module would have:
- **112** total outgoing edges (reduced from 173)
- Redundancy saved: 2 Dependents, 57 Dependencies
- Edges saved: **61**

---

## Rank 40: assert + type_traits

**Merge Count:** 2 modules

### Edge Count Impact

| Metric | Value |
|--------|-------|
| Original edges (sum) | 181 |
| Internal edges (removed) | 0 |
| Merged edges (unique) | 120 |
| Edge reduction | 61 |

### Individual Module Details

**assert:**
- Edges from this module: 95
- Dependencies Relations: Primary = 1, All = 1
- Dependents Relations: Primary = 94, All = 129

**type_traits:**
- Edges from this module: 86
- Dependencies Relations: Primary = 2, All = 2
- Dependents Relations: Primary = 84, All = 107

### Summary

After merge, the combined module would have:
- **120** total outgoing edges (reduced from 181)
- Redundancy saved: 1 Dependents, 60 Dependencies
- Edges saved: **61**

---

