import json
from .audit import build_audit


def main() -> None:
    print(json.dumps(build_audit(), indent=2))


if __name__ == "__main__":
    main()
