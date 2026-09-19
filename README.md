# github-sparkle

Random activity repo — backdated commits that make the GitHub contribution
graph look busy and randomly sparkly.

## Usage

```powershell
python generate.py --days 365              # at least 1 commit every day
python generate.py --days 365 --seed 42    # reproducible
python generate.py --min-per-day 0         # allow empty days
python generate.py --dry-run               # preview counts only
```

Delete `.git` and re-run to regenerate from scratch.
