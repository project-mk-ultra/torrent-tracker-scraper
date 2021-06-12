# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Return scrape errors as value of `error` key inside result `dict` instead of as a single `list` item by [@zawi99](https://github.com/zawi99)
- `ConnectionRefusedError` handled gracefully from [@zrthstr](https://github.com/zrthstr)
- Migrated from Jenkins to GitHub Actions
- Upgrade `black` from 19.10b0 to 21.6b0

### Removed

- Drop support for Python 3.5 and below
