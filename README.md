# auto-task (Python)

**auto-task** is a local automation tool that helps you run tasks on a schedule
(cron or interval) and automatically trigger tasks when files change.
It is designed to work reliably on **Windows**, Linux, and macOS.

## Features

- Cron-style scheduling (5-field crontab)
- Interval-based scheduling
- File watcher automation with debounce
- Supported task types:
  - `python_script` – run a Python file
  - `python_callable` – call a Python function using `module:function`
  - `shell` – execute shell commands (Windows-friendly)
- Simple CLI interface
- Clean logging output

## Requirements

- Python 3.10 or higher

## Installation

1. Create a virtual environment

   Windows:

       python -m venv .venv
       .venv\Scripts\activate

   Linux / macOS:

       python -m venv .venv
       source .venv/bin/activate

2. Install dependencies

       pip install -r requirements.txt

3. Install the project

       pip install -e .

## Usage

Run automation using a JSON configuration file:

    auto-task run path/to/config.json

Example:

    auto-task run examples/config.sample.json

Stop execution with **CTRL + C**.

## License

MIT License © Mukesh Bhople
