#!/usr/bin/env python3
"""Luca bootstrap: loads YAML config, checks the API key, and prints a readiness banner."""

import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

# Load .env so the key is available in os.environ
load_dotenv()

CONFIG_PATH = Path("config/assistant_config.yaml")

def main() -> None:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config not found: {CONFIG_PATH}")

    with CONFIG_PATH.open() as f:
        cfg = yaml.safe_load(f)

    model = cfg.get("model", "gpt-4o")
    temp  = cfg.get("temperature", 0.2)
    key_env = cfg.get("api_key_env", "OPENAI_API_KEY")
    has_key = bool(os.getenv(key_env))

    print(f"Luca ready — model={model} · temperature={temp} · key={'✔' if has_key else '✖'}")

if __name__ == "__main__":
    main()
