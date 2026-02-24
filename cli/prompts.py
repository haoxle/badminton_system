def prompt_int(prompt: str, default: int | None = None) -> int:
    while True:
        raw = input(prompt).strip()
        if not raw and default is not None:
            return default
        try:
            val = int(raw)
            if val < 0:
                print("Please enter a non-negative number.")
                continue
            return val
        except ValueError:
            print("Please enter a valid integer.")


def prompt_choice(prompt: str, valid: set[str]) -> str:
    valid_lower = {v.lower() for v in valid}
    while True:
        raw = input(prompt).strip().lower()
        if raw in valid_lower:
            return raw
        print(f"Please enter one of: {', '.join(sorted(valid))}")