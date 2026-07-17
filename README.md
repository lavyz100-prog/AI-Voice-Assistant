# AI Voice Assistant

A lightweight AI-powered voice assistant for local experimentation and development. This project demonstrates capturing audio, performing speech processing, and connecting simple command/response logic so you can prototype voice-driven features.

**Features**

- Capture and process microphone audio
- Convert speech to text and act on commands (prototype integrations)
- Minimal, easy-to-extend codebase for experimentation

**Files of Interest**

- [audio.py](/Users/cat/Projects/AI-Voice-Assistant/audio.py) — main audio capture / assistant entry point
- [test.py](/Users/cat/Projects/AI-Voice-Assistant/test.py) — example test / demo runner
- [requirements.txt](/Users/cat/Projects/AI-Voice-Assistant/requirements.txt) — Python dependencies
- [src/](src/) — supporting modules and helper code

**Requirements**

- Python 3.8+ recommended
- A working microphone (for live audio capture)
- Install dependencies with pip

Installation

1. Create and activate a virtual environment (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

Usage

- Run the assistant (quick start):

```bash
python3 audio.py
```

- Run the demo/test harness:

```bash
python3 test.py
```

Notes

- The project is intentionally minimal — extend `src/` and `audio.py` to add model integrations, command handlers, and improved audio pipelines.
- If you plan to use external speech or LLM APIs, store keys securely (environment variables or a secrets manager).

Development

- Follow normal Python practices: use a virtualenv, run tests in `test.py`, and add new modules under `src/`.
- Consider formatting with `black` and linting with `flake8` for consistent style.

Contributing

- Open an issue to discuss larger changes before sending a pull request.
- Keep changes focused and include tests or a small demo in `test.py` when possible.

License

This repository does not contain a LICENSE file. Add one (MIT/Apache-2.0/etc.) if you plan to open-source the project.

Contact

Open issues or PRs on the repository for questions and contributions.
