# VisionBoard HR Job Portal — V5 Final Deployment Package

This package is the clean deployment copy of the latest V5 application.

## Included final fixes

1. `database/db_service.py` — broad, word-aware database search for explicit searches.
2. `services/aggregators/technopark.py` — structural employer extraction from the Technopark detail page and corrected `_parse_detail()`.
3. `pages/home.py` — explicit searches use the search-validation path without the default technology-category gate; expiry and excluded-job rules remain active.
4. `assets/css/style.css` — glass-style UI enhancement. CSS is loaded through `utils.helpers.load_css()`, so the CSS is not rendered as visible HTML text.
5. Background synchronization files remain included.

## Required live-data step

Run one fresh synchronization after deployment so the database contains current source data:

```text
python -m services.sync_service
```

The synchronization must be performed in the environment where the API credentials are configured.

## Streamlit Cloud

The application entry point is:

```text
app.py
```

Do not manually edit individual files from older V4/V5 copies after deploying this package.
