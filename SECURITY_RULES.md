# Security Rules - Never Commit These Files

## Absolute Rule: NEVER Upload Sensitive Files to Repository

This is a mandatory security policy. Breaking this rule compromises the entire project.

---

## Files NEVER to Commit

### Environment Variables
- `.env` (any variant)
- `.env.local`
- `.env.production`
- `.env.staging`
- `.env.development`
- `.env.*.local`
- `.env.*.secret`

### Credentials and Secrets
- `secrets.json`
- `credentials.json`
- `*.key` (private keys)
- `*.pem` (certificates)
- `*.crt` (certificates)
- `*.cert`
- `*.p12`, `*.pfx`
- `.aws/`
- `.ssh/`

### Configuration with Secrets
- `MCP/configs/*.json`
- `MCP/configs/*.yaml`
- `MCP/configs/*.yml`
- `config/*.json` (if contains secrets)
- `config/secrets/`
- `config/*secret*`
- `config/*token*`
- `config/*key*`

### Database Credentials
- `database.conf`
- `db.conf`
- `db.password`
- `db.secret`

### Developer Settings
- `.claude/settings.local.json`
- `.vscode/settings.json`
- `.vscode/launch.json`
- `.idea/`
- IDE configurations with personal settings

### Sensitive Reports
- `AUDIT*.md` (security audit reports)
- `AUDIT*.json`
- `AUDIT*.txt`
- `*security*report*.json`
- `*vulnerability*.json`

### Compiled Artifacts (don't commit build outputs)
- `target/` (Rust)
- `build/`
- `dist/`
- `node_modules/`
- `*.so`, `*.dylib`, `*.dll`, `*.exe`

---

## How to Prevent Accidental Commits

### 1. Check .gitignore
Verify your `.gitignore` includes all sensitive patterns:
```bash
cat .gitignore | grep -A 20 "CRITICAL"
```

### 2. Before Every Commit
Run this to check for sensitive files:
```bash
git status
```

Never commit if you see:
- `.env` files
- Config files with secrets
- `MCP/configs/*.json`
- `.claude/settings.local.json`
- AUDIT reports

### 3. Test Git Ignores
```bash
git check-ignore -v <filename>
```

Should return the .gitignore rule if file is properly ignored.

---

## If You Accidentally Committed Secrets

**Immediate Actions:**

1. Rotate all exposed credentials immediately
2. Remove from git history (rewrite history):
```bash
git filter-branch --tree-filter 'rm -f <file>' HEAD
```

3. Force push:
```bash
git push origin --force --all
```

4. Alert the team
5. Audit GitHub access logs

---

## Security Checklist

Before committing anything:
- [ ] No `.env` files
- [ ] No `*.key` or `*.pem` files
- [ ] No JSON config files with api_key
- [ ] No `.claude/settings.local.json`
- [ ] No database credentials
- [ ] No AUDIT reports with sensitive data
- [ ] No compiled binaries
- [ ] No node_modules or dependencies
- [ ] No IDE settings with personal data

---

## Files That CAN Be Committed

- Source code
- Documentation
- `.gitignore` (keep it updated!)
- `.env.example` or `.env.template` (template only, no real values)
- Configuration templates without secrets
- Documentation about setup
- Build/deployment scripts (without embedded secrets)
- Tests (without test credentials)

---

## Continuous Verification

Every 30 days, scan the repository:
```bash
git log --all -p | grep -i "password\|secret\|api_key\|token" | head
```

If anything found, review commits and contact security team.

---

Last Updated: 2025-10-25
Enforcement: MANDATORY
Violation Consequences: Code review rejection, security incident
