# Database Access

The production database is a PostgreSQL instance hosted on Render (free tier).

## How to Connect

To connect with any PostgreSQL client (psql, TablePlus, DBeaver, pgAdmin):

1. Go to https://render.com → your **moveo-db** Postgres service → **Connect** tab
2. Copy the **External Database URL** — it looks like:
   ```
   postgresql://user:password@host/dbname
   ```
3. Paste it into your preferred client as the connection string

> The External Database URL will be provided separately upon request.

## Tables

| Table | Description |
|---|---|
| `users` | Registered accounts (id, name, email, password_hash, is_onboarded, created_at) |
| `user_preferences` | Onboarding answers per user (crypto_assets, investor_type, content_types) |
| `content_votes` | Thumbs up/down votes per user per content item |

## Useful Queries

```sql
-- All registered users
SELECT id, name, email, is_onboarded, created_at FROM users;

-- Onboarding preferences per user
SELECT u.email, p.crypto_assets, p.investor_type, p.content_types
FROM user_preferences p
JOIN users u ON u.id = p.user_id;

-- Voting history
SELECT u.email, v.content_type, v.content_id, v.vote, v.updated_at
FROM content_votes v
JOIN users u ON u.id = v.user_id
ORDER BY v.updated_at DESC;
```
