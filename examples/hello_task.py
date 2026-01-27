from __future__ import annotations

import argparse
import time


def hello_callable(who: str, times: int = 1) -> int:
    for i in range(times):
        print(f"[callable] Hello, {who}! ({i+1}/{times})")
        time.sleep(0.2)
    return 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--name", default="World")
    args = p.parse_args()
    print(f"[script] Hello, {args.name}!")


if __name__ == "__main__":
    main()
