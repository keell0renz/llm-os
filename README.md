# LLM-OS: A conversational interface to your OS

![Code Agent](codeagent.gif)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/keell0renz/llm-os.git
```

### 2. Set up `.env` file

Please copy `.env.example` into `.env` and substitute placeholders with your data and your preference about model asking you every time it wants to execute code.

### 3. Install dependencies

```bash
poetry install
```

### 4. Run chainlit app

```bash
cd llm-os/
```

```bash
poetry run chainlit run llm_os/app.py
```
