# Contributing

Thank you for your interest in improving this project!

---

## Quick Start

```bash
# Fork on GitHub, then:
git clone https://github.com/YOUR_USERNAME/smart-hostel-complaint-system.git
cd smart-hostel-complaint-system

git checkout -b feature/your-feature-name

python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Fill in your own credentials

# Make changes, then:
python -m pytest tests/ -v
git add .
git commit -m "feat: your description"
git push origin feature/your-feature-name
# Open a Pull Request on GitHub
```

---

## Good First Issues

Look for the `good first issue` label in GitHub Issues. Current ones:
- Add Hindi language keywords to `ai_classifier_simple.py`
- Add screenshots of the WhatsApp flow to README
- Write tests for FOOD and CLEANLINESS categories
- Implement LOW priority detection

---

## Branch Naming

```
feature/add-hindi-keywords
fix/room-number-4-digit-regex
docs/add-architecture-diagram
test/add-food-category-tests
```

---

## Commit Format

We use [Conventional Commits](https://www.conventionalcommits.org):

```
feat: add Hindi keyword support to classifier
fix: fix room number not extracting 4-digit values
docs: add WhatsApp demo screenshots to README
test: add 5 new tests for SECURITY category
chore: update requirements.txt
```

---

## Code Rules

- Follow PEP 8
- Add docstrings to every function (see existing code for format)
- Never hardcode credentials — always use `os.getenv()`
- Never commit `.env` — the CI pipeline will catch this and fail

---

## Security Rule

The `.gitignore` already blocks `.env`. But double check before pushing:
```bash
git status   # .env should NOT appear here
```

---

## Pull Request Process

1. Open a PR
2. CI runs automatically (must pass)
3. Team member reviews within 48 hours
4. Address feedback
5. Merge after approval
