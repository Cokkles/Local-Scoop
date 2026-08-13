# ADR 0004 — Event source strategy

Status: Accepted for Phase 0 POC.

Local Scoop will build **adapter families around publishing platforms**, not one bespoke crawler per website. Phase 0.4 identified reusable families including CivicEngage/iCalendar, Localist/feed-based university calendars, Simpleview-style tourism calendars, custom municipal HTML, and structured commercial APIs.

Authority and ingestion readiness remain independent dimensions. Official sources are preferred for factual conflicts; broad aggregators and community calendars are used to improve discovery recall. A lower-tier discovery source may surface an event, but Local Scoop should retain and prefer corroborating first-party evidence when available.

Eventbrite is not approved as a broad discovery adapter in this checkpoint because its public Event Search API was retired. PredictHQ remains a licensed option rather than a required dependency. Ticketmaster is an initial structured API candidate for major ticketed events.
