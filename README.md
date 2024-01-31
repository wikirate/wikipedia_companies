# Wikirate

## Description

Python script to extract official company websites from Wikipedia and insert them into Wikrate.

## Installation

### Prerequisites

Before setting up the project, make sure you have Python installed on your system. You can download Python from [python.org](https://www.python.org/).

### Setting Up a Virtual Environment

To avoid conflicts with other projects or system-wide Python packages, it's a good practice to use a virtual environment. Here's how you can set it up:

1. **Create a Virtual Environment:** Navigate to your project's root directory in your command line and run:

    ```bash
    python -m venv venv
    ```

    This command creates a new directory `venv` in your project where all dependencies will be installed.

2. **Activate the Virtual Environment:** 

    - On Windows, run:

        ```bash
        .\venv\Scripts\activate
        ```

    - On macOS and Linux, run:

        ```bash
        source venv/bin/activate
        ```

    You should now see the name of your virtual environment in the command prompt.

### Installing Dependencies

With the virtual environment activated, install the project dependencies:

```bash
pip install -r requirements.txt
```

### Create a .env in the root directory
```
API_KEY=yourapikey
# for staging (optional)
URL=wikiratestagingwebsite
USER=wikiratestaginguser
PASSWORD=wikiratestagingpassword
```
