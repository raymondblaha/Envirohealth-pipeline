# Release Checklist

## Milestone 9: GitHub Actions CI/CD

- [x] GitHub Actions workflow exists at `.github/workflows/ci.yml`
- [x] Workflow runs on push
- [x] Workflow runs on pull request
- [x] Ruff runs automatically
- [x] pytest runs automatically
- [x] PostgreSQL integration behavior is covered in CI
- [x] Docker image build is verified in CI
- [ ] Workflow passes on GitHub after a real push or pull request
- [ ] README CI badge shows a passing workflow

## Milestone 10: Portfolio Release

- [x] README leads with problem, architecture, data, pipeline, results, reproducibility, testing, and limitations
- [x] Architecture diagram included
- [x] Selected portfolio figures included under `docs/assets/`
- [x] Statistical and ML results summarized in resume-ready language
- [x] Reproduction commands documented
- [x] LICENSE present
- [x] `.env.example` contains safe placeholders
- [x] Raw data and generated outputs are ignored by Git
- [ ] GitHub repository description added
- [ ] GitHub repository topics added
- [ ] `v1.0.0` tag created after CI passes

## Suggested Repository Topics

```text
data-engineering
postgresql
etl
public-health
environmental-data
python
sql
docker
github-actions
machine-learning
```

## Suggested GitHub Description

```text
Reproducible Python/PostgreSQL pipeline integrating EPA air quality and CDC PLACES data for county-level environmental health analysis, validation, statistics, and ML benchmarking.
```
