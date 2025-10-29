# Boost Website RAG Integration Guide

## Architecture Overview

**Existing Infrastructure**:

- ✅ **RAG Service**: FastAPI running at `localhost:8080` (provides processed mailing list intelligence)
- ✅ **Django Website**: `website-v2` with existing library pages, mailing list app
- ✅ **HyperKitty Database**: Read access from Django for email sync

**Integration Pattern**:

```
User → Django View → RAG Service API (localhost:8080)
                    ↓
        Cache Result → Render Template
```

**Django Components to Build**:

1. **RAGServiceClient** (`mailing_list/rag_client.py`) - HTTP client calling RAG service
2. **API ViewSet** (`mailing_list/api.py`) - Endpoints that proxy to RAG + caching
3. **Templates** - Display processed content with HTMX
4. **Celery Tasks** - Daily HyperKitty sync, weekly digest
5. **Models** - Cache RAG results, track sync status

---

## Common Integration Pattern

All features follow this pattern:

### Step 1: Django Calls RAG Service

```python
# Django view calls RAG service API
rag_client = RAGServiceClient(base_url="http://localhost:8080")
response = rag_client.query(
    question="semantic query here",
    search_scopes=["mail"],
    search_limit=50,
    date_start="2024-01-01",
    date_end="2024-12-31",
    library_filter="Boost.Asio",
    process_type="discussion_summary"  # or "architecture", "security", etc.
)

# RAG returns processed, display-ready data:
# {
#   'summary': {...},
#   'categories': {...},
#   'sentiment': {...},
#   'sources': [...]
# }
```

### Step 2: Display in Django Template

```django
<div hx-get="/api/library/{{ library.slug }}/summary?timeframe=7d"
     hx-trigger="load">
    Loading discussions...
</div>
```

---

## Library Features Integration

---

### 1-3. Discussion Summaries (Temporal)

**Client Request**:

> 1. Summary of discussions for the last 7 days.
> 2. Summary of discussions since last release, or for a version on a selected version.
> 3. Latest: Summary of discussions in previous release - may be redundant.

#### Integration Approach

**Django API Endpoint** (Simple proxy + caching):

```python
# mailing_list/api.py
@action(detail=False, methods=['get'],
        url_path='library/(?P<library_slug>[-\\w]+)/summary')
def library_summary(self, request, library_slug=None):
    library = get_object_or_404(Library, slug=library_slug)
    timeframe = request.query_params.get('timeframe', '7d')

    # Calculate date range
    date_start, date_end = calculate_date_range(timeframe)

    # Call RAG service - it handles retrieval AND post-processing
    summary = self.rag_client.query(
        question=f"discussions about {library.name} bug reports features design",
        search_scopes=["mail"],
        search_limit=50,
        date_start=date_start,
        date_end=date_end,
        library_filter=library.name,
        process_type="discussion_summary"  # RAG returns categorized summary
    )

    # Cache the result (24 hours for summaries)
    cache.set(f"summary_{library.slug}_{timeframe}", summary, timeout=86400)

    return Response(summary)
```

**RAG Service API Response**:

```json
{
  "categories": {
    "Bug": [
      {
        "subject": "Memory leak in Beast HTTP parser",
        "sentiment": "Negative",
        "url": "https://lists.boost.org/...",
        "date": "2024-01-15",
        "participants": ["user1@example.com", "maintainer@boost.org"]
      }
    ],
    "Feature": [...],
    "Design": [...]
  },
  "stats": {
    "total_emails": 42,
    "participants": 15,
    "by_sentiment": {
      "Positive": 10,
      "Neutral": 25,
      "Negative": 5,
      "Urgent": 2
    }
  },
  "summary": "42 discussions from 15 participants. Key issues: 2 urgent bugs, 3 feature requests..."
}
```

**Frontend Display**:

```django
<!-- templates/libraries/detail.html -->
<div class="card">
    <div class="tabs">
        <button data-timeframe="7d">Last 7 Days</button>
        <button data-timeframe="30d">Last 30 Days</button>
        <button data-timeframe="release_latest">Since Last Release</button>
    </div>
    <div id="summary"
         hx-get="/api/mailing-list-ai/library/{{ library.slug }}/summary?timeframe=7d"
         hx-trigger="load">
        Loading...
    </div>
</div>
```

**Auto-Update**: Daily Celery task refreshes cache for active libraries

---

### 4. Architectural Decisions

**Client Request**:

> Summary of significant architectural decisions made, implemented, and justifications for those changes, since the library was created or some other timeframe.

#### Integration Approach

**Django API Endpoint** (Simple proxy with timeframe support):

```python
@action(detail=False, methods=['get'],
        url_path='library/(?P<library_slug>[-\\w]+)/architecture')
def architectural_decisions(self, request, library_slug=None):
    library = get_object_or_404(Library, slug=library_slug)
    timeframe = request.query_params.get('timeframe', 'all')  # 'all', '1y', '5y', 'since_creation'

    # Calculate date range based on timeframe
    if timeframe == 'all' or timeframe == 'since_creation':
        date_start = library.created_at  # Library creation date
        date_end = None
    else:
        date_start, date_end = calculate_date_range(timeframe)

    # RAG service returns chronological summary (organized as timeline)
    summary = self.rag_client.query(
        question=f"architectural decisions design consensus {library.name}",
        search_scopes=["mail"],
        search_limit=100,
        date_start=date_start,
        date_end=date_end,
        library_filter=library.name,
        process_type="architecture"  # RAG returns chronological summary
    )

    return Response({'summary': summary, 'timeframe': timeframe, 'review_required': True})
```

**Display**: Chronological summary organized as timeline for easy scanning, with expandable decision cards and maintainer review badge. Add timeframe selector: "Since Creation (default)" / "Last 5 Years" / "Last Year"

**Note**: Timeline format preserves temporal context showing how architecture evolved over time, while each decision is summarized with what/when/who/why

---

### 5. Deprecations and Removals

**Client Request**:

> Latest: Deprecations and removals that were agreed upon since last release.

**Integration**: RAG query: `"deprecate remove breaking change {library}"` with `process_type="deprecations"` → RAG returns grouped by feature with what/why/replacement/timeline → Might display as warning cards on library page

---

### 6. Future Roadmap

**Client Request**:

> Latest: Future road map discussions/decisions.

**Integration**: RAG query: `"roadmap future plan proposal {library}"` with `process_type="roadmap"` → RAG returns classified by status (Idea/Discussion/Approved/InProgress/Blocked) → Might display as roadmap board with contributor opportunities highlighted

**Note**: Requires maintainer review before publication

---

### 7. Maintainer History

**Client Request**:

> Maintainer change history/updates since library creation and/or some other timeframe.

**Integration**:

```python
@action(detail=False, methods=['get'],
        url_path='library/(?P<library_slug>[-\\w]+)/maintainers')
def maintainer_history(self, request, library_slug=None):
    library = get_object_or_404(Library, slug=library_slug)
    timeframe = request.query_params.get('timeframe', 'all')  # 'all', '5y', '10y', 'since_creation'

    # Calculate date range
    if timeframe == 'all' or timeframe == 'since_creation':
        date_start = library.created_at
        date_end = None
    else:
        date_start, date_end = calculate_date_range(timeframe)

    history = self.rag_client.query(
        question=f"maintainer taking over stepping down {library.name}",
        search_scopes=["mail"],
        search_limit=50,
        date_start=date_start,
        date_end=date_end,
        library_filter=library.name,
        process_type="maintainer_history"
    )

    return Response({'history': history, 'timeframe': timeframe})
```

**Display**: Chronological timeline with role transitions on library "About" tab. Timeframe options: "Since Creation" / "Last 10 Years" / "Last 5 Years"

**Note**: Requires C++ Alliance administrator verification before publication

---

### 8. Security Issues

**Client Request**:

> Summary of security related discussions that resulted in changes (timeframe?) - may be a useful justification for upgrading.

**Integration**:

```python
@action(detail=False, methods=['get'],
        url_path='library/(?P<library_slug>[-\\w]+)/security')
def security_issues(self, request, library_slug=None):
    library = get_object_or_404(Library, slug=library_slug)
    timeframe = request.query_params.get('timeframe', '5y')  # Default: last 5 years

    # Calculate date range
    date_start, date_end = calculate_date_range(timeframe)

    security_data = self.rag_client.query(
        question=f"security vulnerability CVE {library.name}",
        search_scopes=["mail"],
        search_limit=100,
        date_start=date_start,
        date_end=date_end,
        library_filter=library.name,
        process_type="security"
    )

    return Response({'security_issues': security_data, 'timeframe': timeframe})
```

**Display**: Security tab with CVE badges, severity indicators, affected versions, and fix timelines. Timeframe options: "Last 5 Years (default)" / "Last 10 Years" / "All Time"

**Use Case**: Users deciding whether to upgrade can see security fixes in their timeframe of interest (e.g., "What security issues were fixed in the last 2 years?")

**Critical**: Never auto-publish. Coordinate with security team. Hide unpatched vulnerabilities.

---

### 9. Migration Guides

**Client Request**:

> Library specific upgrade migration processes/walkthroughs? Generated info may be too vague/hallucinated, we should probably loop library developers into this before publication?

#### What This Is

Help users **upgrade** from one library version to another by documenting breaking changes, API changes, and migration steps discussed in mailing lists.

#### Integration Approach

**Django API Endpoint**:

```python
@action(detail=False, methods=['get'],
        url_path='library/(?P<library_slug>[-\\w]+)/migration')
def migration_guide(self, request, library_slug=None):
    library = get_object_or_404(Library, slug=library_slug)
    from_version = request.query_params.get('from_version')  # e.g., "1.75"
    to_version = request.query_params.get('to_version', 'latest')  # e.g., "1.82"

    if not from_version:
        return Response({'error': 'from_version required'}, status=400)

    # Get version date ranges
    from_date = get_version_release_date(from_version)
    to_date = get_version_release_date(to_version) if to_version != 'latest' else None

    guide = self.rag_client.query(
        question=f"breaking change API change migration {library.name} version {from_version} {to_version}",
        search_scopes=["mail"],
        search_limit=100,
        date_start=from_date,
        date_end=to_date,
        library_filter=library.name,
        process_type="migration"
    )

    return Response({
        'guide': guide,
        'from_version': from_version,
        'to_version': to_version,
        'status': 'draft',  # ALWAYS draft until maintainer approves
        'requires_review': True
    })
```

#### RAG Output Format

RAG returns breaking changes organized by category:

```json
{
  "breaking_changes": [
    {
      "category": "API Change",
      "api_name": "async_read()",
      "description": "Parameters changed in version 1.78",
      "old_usage": "async_read(socket, buffer, handler);",
      "new_usage": "async_read(socket, buffer, completion_token);",
      "migration_steps": [
        "Replace handler parameter with completion_token",
        "Update callback signature to use error_code"
      ],
      "discussion_links": ["https://lists.boost.org/..."]
    }
  ],
  "deprecations": [...],
  "new_features": [...],
  "confidence": "medium"
}
```

#### Display

**Migration Guide Page** (accessible from library detail page):

- Version selector: "From Version" and "To Version" dropdowns
- Breaking changes organized by category (API Changes, Deprecations, Removals)
- Each change shows:
  - **Before** code example (highlighted in red)
  - **After** code example (highlighted in green)
  - Migration steps (numbered list)
  - Links to mailing list discussions
- **⚠️ DRAFT Banner**: "This guide was generated from mailing list discussions. Maintainer review pending."

#### Anti-Hallucination Strategy

**Our safeguards**:

1. ✅ **Retrieval-only**: RAG only extracts information explicitly discussed in emails (no generation)
2. ✅ **Source links**: Every change links back to the original mailing list discussion (users can verify)
3. ✅ **Confidence scores**: Low-confidence items flagged for review
4. ✅ **Maintainer approval required**: Content NEVER published without maintainer verification
5. ✅ **Draft-only status**: Always marked as "DRAFT" until approved

**Workflow**:

```
RAG generates → Mark as DRAFT → Email maintainer for review → Maintainer edits/approves → Publish
```

---

### 10. Review Process Links

**Client Request**:

> Provide links to related threads of the review process.

**Integration**: RAG query: `"FORMAL REVIEW {library} ACCEPTED REJECTED"` with `process_type="review"` → RAG returns review metadata and categorized feedback → Display as "Review History" section with links to all review threads

---

### Source Linking (Cross-Cutting)

**Client Request**:

> Add links to relevant threads/messages for above items.

**Implementation**: RAG service returns email metadata with URLs. Display source links in all generated content:

```python
# Email metadata from RAG includes:
{
    'url': 'https://lists.boost.org/Archives/boost/2024/01/message_id',
    'message_id': '<...>',
    'date': '2024-01-15',
    'sender_address': 'author@example.com'
}
```

**Frontend Display**: Add "View Discussion →" links, citation footnotes `[[1]]`, confidence badges (✅ High/⚠️ Medium/🔍 Low)

---

## Organization Features (Standard Website Content)

**Client Request**:

> 1. Boost history, leadership changes.
> 2. Upcoming events.
> 3. Ongoing Funding discussions.
> 4. Index of libraries, mark accepted or...

**Integration**: Standard Django pages/models. **No RAG needed** - use official C++ Alliance data:

1. **Boost History**: Static page managed via Django admin
2. **Events Calendar**: `Event` model with upcoming conferences, release dates, review deadlines
3. **Funding Page**: Links to C++ Alliance grants/sponsorship info
4. **Library Index**: Already exists in `website-v2/libraries/` - add acceptance status field

---

## Additional AI-Powered Features

### 1. Intelligent Search

**Integration**: Direct pass-through to RAG service `/query` endpoint. Add search bar in navbar:

```python
@action(detail=False, methods=['post'], url_path='search')
def intelligent_search(self, request):
    query = request.data.get('query')
    results = self.rag_client.query(
        question=query,
        search_scopes=["mail", "documentation"],
        search_limit=20
    )
    return Response(results)
```

### 2. Smart FAQ Assistant

**Integration**: Same as Intelligent Search but with conversational UI. Add chat widget to library pages.

### 3. Weekly Community Digest

**Integration**: Celery weekly task calls Items 1-3 for all active libraries → RAG summarizes top items → Email via Django's email backend

### 4. Duplicate Question Detection

**Integration**: On mailing list compose page, use RAG search to find similar questions as user types → Display "Similar discussions" suggestion panel

---

## Django Implementation Details

### 1. RAG Service Client

```python
# mailing_list/rag_client.py
import requests

class RAGServiceClient:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url

    def query(self, question, search_scopes, search_limit,
              date_start=None, date_end=None, library_filter=None,
              process_type=None):
        response = requests.post(
            f"{self.base_url}/query",
            json={
                "question": question,
                "search_scopes": search_scopes,
                "search_limit": search_limit,
                "date_start": date_start,
                "date_end": date_end,
                "library_filter": library_filter,
                "process_type": process_type
            },
            timeout=30
        )
        return response.json()
```

### 2. Django Models

```python
# mailing_list/models.py
class RAGQueryCache(models.Model):
    """Cache for RAG query results"""
    query_hash = models.CharField(max_length=64, unique=True, db_index=True)
    library = models.ForeignKey('libraries.Library', on_delete=models.CASCADE)
    content_type = models.CharField(max_length=50)  # discussion_summary, architecture, etc.
    processed_content = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

class EmailSyncStatus(models.Model):
    """Track HyperKitty email sync status"""
    message_id = models.CharField(max_length=255, unique=True)
    synced_to_rag = models.BooleanField(default=False)
    synced_at = models.DateTimeField(null=True)
```

### 3. Celery Tasks

```python
# mailing_list/tasks.py
from celery import shared_task

@shared_task
def sync_hyperkitty_to_rag():
    """Daily task: sync new emails from HyperKitty to RAG service"""
    # Query HyperKitty for new emails
    # POST to RAG service /maillist/messages/new
    pass

@shared_task
def generate_weekly_digest():
    """Weekly task: generate community digest"""
    # Call RAG for all active libraries
    # Email results
    pass
```

---
