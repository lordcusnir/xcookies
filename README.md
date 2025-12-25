# XCookies

Extract cookies from X (Twitter) accounts using existing auth tokens.

## How It Works

This tool injects an existing `auth_token` into a headless browser session, navigates to X.com, and extracts the complete set of session cookies (`auth_token`, `ct0`, `twid`, `guest_id`).

## Installation

```bash
# Clone the repo
git clone https://github.com/lordcusnir/xcookies.git
cd xcookies

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install
pip install -e .
playwright install chromium
```

## Usage

```bash
# Default: reads credentials.txt → outputs cookies.json
xcookie

# Custom files
xcookie accounts.txt -o output.json
```

## Input Format

Create `credentials.txt` with one account per line (tab-separated):

```
username1	a5c1fdc5af83b379169f2b7a68e694f33284a5f9
username2	b825622d204def30619395844a4b1c5b1951201e
```

See `credentials.example.txt` for a template.

## Output

`cookies.json`:

```json
[
  {
    "username": "username1",
    "auth_token": "a5c1fdc5...",
    "ct0": "generated_ct0_value...",
    "twid": "u%3D123456789...",
    "guest_id": "v1%3A..."
  }
]
```

## Security

**Never commit your credentials or cookies!**

- `credentials.txt` is gitignored
- `cookies.json` is gitignored
- Only `credentials.example.txt` (a blank template) is tracked

## Requirements

- Python 3.11+
- Playwright (Chromium)

## License

MIT
