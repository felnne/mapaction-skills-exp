# MapAction Volunteer Skills Experiment

Experiment to manage a database of skills and competencies held by MapAction volunteers.

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
```

**Note:** UV will automatically create a Python virtual environment for the project at runtime.

Setup local database:

```sql
CREATE USER ma_skills_owner WITH PASSWORD 'xxx';
CREATE DATABASE ma_skills OWNER ma_skills_owner;
```

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
