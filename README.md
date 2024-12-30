# MapAction Volunteer Skills Experiment

Experiment to manage a database of skills and competencies held by MapAction volunteers.

## Usage

https://felnne-ma-skills-exp.streamlit.app/

## Setup

1. create a Neon project
    - if necessary create a [Neon](https://console.neon.tech) account
    - create a new Neon project (`ma-skills-exp`)
    - use the provided connection string as the `connections.neon.url` value in Streamlit secrets
    - migrate database: `uv run scripts/db_migrate.py up`
    - seed database: `uv run scripts/db_seed.py`
1. create a Streamlit Community Cloud deployment
    - push code to GitHub
    - if needed, create a Streamlit Community Cloud account and authorise GitHub integration
    - create a new Streamlit app:
      - deployment type: *deploy a public app from GitHub*
      - repository: (as setup in GitHub)
      - branch: `main`
      - main file path: `main.py`
      - app URL: `felnne-ma-skills-exp`
      - (advanced settings) Python version: 3.12
      - (advanced settings) secrets:
        - as per `.streamlit/secrets.toml.example`

## Developing

### Local development environment

Requirements:

* [UV](https://docs.astral.sh/uv) (`brew install uv`)
* [Git](https://git-scm.com) (`brew install git`)
* [Pre-commit](https://pre-commit.com) (`uv tool install pre-commit`)
* [Postgres](https://www.postgresql.org) (`brew install postgresql`)

Setup project:

```
$ git clone https://github.com/felnne/mapaction-skills-exp
$ cd mapaction-skills-exp/
$ pre-commit install
$ cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

(Update any 'xxx' values in `.streamlit/secrets.toml`.)

**Note:** UV will automatically create a Python virtual environment for the project at runtime.

Setup local database:

```sql
CREATE USER ma_skills_owner WITH PASSWORD 'xxx';
CREATE DATABASE ma_skills OWNER ma_skills_owner;
```

(Update the 'xxx' value for a secure password and update connection string in `.streamlit/secrets.toml`.)

```
$ uv run scripts/db_migrate.py up
$ uv run scripts/db_seed.py
```

Run app:

```
$ uv run -- streamlit run main.py
```

## Releasing

To create a release:

```
$ scripts/release.sh [major|minor|patch]
```

Push `main` branch and created tag to GitHub.

## Deployment

The Streamlit GitHub integration will automatically deploy pushed commits to the Streamlit Community Cloud.

# License

Copyright (c) 2024 MapAction.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
