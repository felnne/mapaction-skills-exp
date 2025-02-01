# MapAction Volunteer Skills Experiment - Change log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

* Upgrading release script

## [0.4.1] - 2025-01-01

### Fixed

* Logic used for volunteers with skills filter (again!)

## [0.4.0] - 2025-01-01

### Added

* Created/updated at timestamps for database entities
* Queries for when a volunteer last updated their skills, and which skills have been added/changed since this
* Very experimental query builder support (as an example)
* Data export download

### Changed

* Refactor charts to a standalone stats page

## [0.3.0] - 2024-12-30

### Added

* Multi-page app
* Initial page for updating a volunteer's skills

### Fixed

* Logic used for volunteers with skills filter (from OR to AND)

## [0.2.0] - 2024-12-29

### Added

* Remote DB for data storage
* Chart for skill counts

## [0.1.0] - 2024-12-28

### Added

- Initial experiment with static skills and ephemeral volunteer and skill assignments
