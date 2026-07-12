-- PSERS / LMR ontology schema (Sprint 0)
-- Postgres 14+

CREATE TABLE IF NOT EXISTS vendor (
  id          TEXT PRIMARY KEY,
  name        TEXT NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS document (
  id          TEXT PRIMARY KEY,
  title       TEXT NOT NULL,
  source_url  TEXT,
  doc_type    TEXT NOT NULL CHECK (doc_type IN ('rfp', 'standard', 'brochure', 'other')),
  notes       TEXT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS capability (
  id            TEXT PRIMARY KEY,          -- PSERS.INFRA.LMR....
  alias         TEXT UNIQUE,               -- optional short LMR.*
  name          TEXT NOT NULL,
  definition    TEXT NOT NULL,
  stack_class   TEXT NOT NULL CHECK (stack_class IN ('INFRA','SENS','PLAT','APP','SVC','XCUT')),
  domain        TEXT NOT NULL,
  mission_tags  TEXT[] NOT NULL DEFAULT '{}',
  status        TEXT NOT NULL DEFAULT 'draft'
                  CHECK (status IN ('draft','published','deprecated','stub')),
  p25_ref       TEXT,
  vertical      TEXT NOT NULL DEFAULT 'LMR',
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_capability_stack ON capability (stack_class);
CREATE INDEX IF NOT EXISTS idx_capability_domain ON capability (domain);
CREATE INDEX IF NOT EXISTS idx_capability_status ON capability (status);

CREATE TABLE IF NOT EXISTS synonym (
  id            BIGSERIAL PRIMARY KEY,
  phrase        TEXT NOT NULL,
  capability_id TEXT NOT NULL REFERENCES capability(id),
  confidence    REAL NOT NULL DEFAULT 1.0,
  source_doc_id TEXT REFERENCES document(id),
  page_ref      TEXT,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_synonym_phrase ON synonym USING gin (to_tsvector('english', phrase));
CREATE INDEX IF NOT EXISTS idx_synonym_cap ON synonym (capability_id);

CREATE TABLE IF NOT EXISTS product (
  id            TEXT PRIMARY KEY,
  vendor_id     TEXT NOT NULL REFERENCES vendor(id),
  family        TEXT NOT NULL,
  sku_or_name   TEXT NOT NULL,
  form_factor   TEXT,
  notes         TEXT,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS product_capability (
  product_id     TEXT NOT NULL REFERENCES product(id),
  capability_id  TEXT NOT NULL REFERENCES capability(id),
  support_level  TEXT NOT NULL
    CHECK (support_level IN ('native','option','partner','not_applicable','unknown')),
  notes          TEXT,
  source_url     TEXT,
  PRIMARY KEY (product_id, capability_id)
);

CREATE TABLE IF NOT EXISTS cdm_alignment (
  capability_id  TEXT NOT NULL REFERENCES capability(id),
  eido_or_entity TEXT NOT NULL,
  notes          TEXT,
  PRIMARY KEY (capability_id, eido_or_entity)
);

INSERT INTO vendor (id, name) VALUES ('MSI', 'Motorola Solutions')
ON CONFLICT (id) DO NOTHING;
