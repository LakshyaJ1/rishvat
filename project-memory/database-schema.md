# AI CFO — Database Schema

## Tables

### tenants
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK, gen_random_uuid() |
| name | VARCHAR(255) | NOT NULL |
| slug | VARCHAR(100) | UNIQUE, NOT NULL |
| jurisdiction | VARCHAR(10) | NOT NULL, default 'US' |
| shadow_mode_until | TIMESTAMPTZ | NOT NULL (NOW() + 30 days) |
| autopilot_level | VARCHAR(20) | NOT NULL, default 'advisory' |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

### users
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| tenant_id | UUID | FK → tenants.id, NOT NULL |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| password_hash | VARCHAR(255) | NOT NULL |
| full_name | VARCHAR(255) | NOT NULL |
| role | VARCHAR(20) | default 'founder' |
| is_active | BOOLEAN | default true |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

### financial_records
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| tenant_id | UUID | FK → tenants.id, NOT NULL |
| source | VARCHAR(50) | NOT NULL |
| source_id | VARCHAR(255) | NOT NULL |
| record_type | VARCHAR(50) | NOT NULL |
| category | VARCHAR(100) | nullable |
| amount_cents | BIGINT | NOT NULL |
| currency | VARCHAR(3) | NOT NULL, default 'USD' |
| description | TEXT | nullable |
| occurred_at | TIMESTAMPTZ | NOT NULL |
| metadata_json | JSONB | nullable |
| synced_at | TIMESTAMPTZ | NOT NULL |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

**Unique**: (tenant_id, source, source_id)
**Indexes**: (tenant_id, occurred_at), (tenant_id, source), (tenant_id, record_type), (tenant_id, category)

### connector_configs
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| tenant_id | UUID | FK → tenants.id |
| provider | VARCHAR(50) | NOT NULL |
| credentials_encrypted | TEXT | NOT NULL (AES-256) |
| permissions | VARCHAR(20) | default 'read_only' |
| status | VARCHAR(20) | default 'active' |
| last_synced_at | TIMESTAMPTZ | nullable |
| sync_error | TEXT | nullable |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

**Unique**: (tenant_id, provider)

### audit_logs (APPEND-ONLY)
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| tenant_id | UUID | FK → tenants.id |
| user_id | UUID | FK → users.id, nullable |
| action_type | VARCHAR(50) | NOT NULL |
| action_detail | JSONB | nullable |
| data_sources | JSONB | nullable |
| outcome | VARCHAR(20) | NOT NULL |
| ip_address | VARCHAR(45) | nullable |
| created_at | TIMESTAMPTZ | NOT NULL |

**No UPDATE/DELETE** — enforced by database trigger.

### autopilot_configs
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| tenant_id | UUID | FK to tenants.id, NOT NULL |
| category | VARCHAR(50) | NOT NULL |
| autonomy_level | VARCHAR(20) | NOT NULL, default 'advisory' |
| max_amount_cents | BIGINT | NOT NULL, default 0 |
| revenue_floor_cents | BIGINT | NOT NULL, default 0 |
| locked | BOOLEAN | NOT NULL, default false |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

**Unique**: (tenant_id, category)

### notifications
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| tenant_id | UUID | FK to tenants.id, NOT NULL |
| type | VARCHAR(50) | NOT NULL |
| severity | VARCHAR(20) | NOT NULL, default 'info' |
| title | VARCHAR(255) | NOT NULL |
| body | TEXT | nullable |
| data | JSONB | nullable |
| read | BOOLEAN | NOT NULL, default false |
| dismissed | BOOLEAN | NOT NULL, default false |
| created_at | TIMESTAMPTZ | NOT NULL |

### approval_actions
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| tenant_id | UUID | FK to tenants.id, NOT NULL |
| action_type | VARCHAR(50) | NOT NULL |
| action_payload | JSONB | nullable |
| reasoning | TEXT | nullable |
| data_sources | JSONB | nullable |
| expected_outcome | TEXT | nullable |
| status | VARCHAR(20) | NOT NULL, default 'pending' |
| reviewed_by | UUID | FK to users.id, nullable |
| reviewed_at | TIMESTAMPTZ | nullable |
| rejection_reason | TEXT | nullable |
| created_at | TIMESTAMPTZ | NOT NULL |

## Row-Level Security
Enabled on: financial_records, connector_configs, audit_logs, autopilot_configs, notifications, approval_actions
Policy: `tenant_id = current_setting('app.current_tenant_id')::uuid`

## Migrations
| Revision | Description | Date |
|----------|-------------|------|
| 001_initial | All 5 tables, indexes, RLS, audit trigger | 2026-05-17 |
| 002_stage2_tables | Autopilot configs, notifications, approval actions, category index, RLS policies | 2026-05-17 |
