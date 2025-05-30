# Changelog

## [Bulk Fit Projection Added] — YYYY-MM-DD

### Added
- Bulk fit evaluation: Projects future “bulk up” scenario (increased chest, shoulders, arms, etc.) based on constants in `models/bulk_params.py`.
- Output CSV now includes: `BulkFitScore`, `BulkConfidence`, `BulkTags`, `BulkRationale`.

### Changed
- Scoring model logic now called twice per shirt: once for current fit, once for bulk projection.
- Confidence for bulk scenario is reduced to reflect projection uncertainty.

### Not Included
- Margin of error output (planned for future increment)
- Integration of body weight or Renpho data into fit scoring
