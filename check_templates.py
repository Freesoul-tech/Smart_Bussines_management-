from pathlib import Path

print("Checking templates...")

for p in Path("templates").rglob("*.html"):
    try:
        p.read_bytes().decode("utf-8")
        print("OK  ", p)
    except UnicodeDecodeError as e:
        print("BAD UTF-8:", p)
        print("ERROR:", e)
