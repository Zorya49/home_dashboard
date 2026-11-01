# Personal Dashboard Server

A small, local-first personal data server that turns raw Apple Health data into a simple
always-on dashboard. It is built for privacy-conscious use at home, with SQLite
as the persistent source of truth.

## What it does

- Accepts Apple Health data exported through Health Exporter app and iPhone Shortcuts via authenticated
  API endpoints.
- Normalizes and stores daily steps and workouts in a local SQLite database.
- Serves a lightweight browser dashboard with current-year step progress,
  recent step totals, and yearly workout counts.

## Design

The application uses FastAPI and keeps ingestion, stored data, and presentation
separate. The dashboard reads summaries from the server; it does not access the
database directly. Repeated uploads are designed to update existing records
rather than create duplicates.

The initial display is a browser on a local network. The architecture is intended
to support additional data sources and displays without tying the core data model
to Apple Health or a particular screen.

See [PROJECT_SPEC.md](PROJECT_SPEC.md) for the project's architecture, constraints,
and planned scope.

## AI-assisted development

AI is used primarily for frontend development and documentation; elsewhere, I use it mainly as an advisory pair programmer, seeking guidance while leading implementation myself.