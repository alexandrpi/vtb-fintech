-- SQL Manager Lite for PostgreSQL 5.8.1.48500
-- ---------------------------------------
-- Host      : localhost
-- Database  : FinancialStatements
-- Version   : PostgreSQL 9.6.1, compiled by Visual C++ build 1800, 64-bit



SET check_function_bodies = false;
--
-- Structure for table Operations (OID = 16394) : 
--
SET search_path = public, pg_catalog;
CREATE TABLE public."Operations" (
)
WITH (oids = false);
--
-- Structure for table Categories (OID = 16397) : 
--
CREATE TABLE public."Categories" (
    "@Categories" integer NOT NULL,
    "Name" text
)
WITH (oids = false);
--
-- Structure for table Accounts (OID = 16405) : 
--
CREATE TABLE public."Accounts" (
    "@Accounts" integer NOT NULL,
    "Name" text NOT NULL,
    "AccountTotal" double precision NOT NULL
)
WITH (oids = false);
--
-- Structure for table CatsToAccs (OID = 16413) : 
--
CREATE TABLE public."CatsToAccs" (
    "@CatsToAccs" integer NOT NULL,
    "@Categories" integer NOT NULL,
    "@Accounts" integer NOT NULL,
    "OperationType" smallint NOT NULL
)
WITH (oids = false);
--
-- Structure for table Assets (OID = 16428) : 
--
CREATE TABLE public."Assets" (
    "@Assets" integer NOT NULL,
    "Name" text NOT NULL,
    "AssetTotal" double precision NOT NULL,
    "Type" smallint NOT NULL,
    "AssetFormula" text NOT NULL
)
WITH (oids = false);
--
-- Definition for index Categories_pkey (OID = 16403) : 
--
ALTER TABLE ONLY "Categories"
    ADD CONSTRAINT "Categories_pkey"
    PRIMARY KEY ("@Categories");
--
-- Definition for index Accounts_pkey (OID = 16411) : 
--
ALTER TABLE ONLY "Accounts"
    ADD CONSTRAINT "Accounts_pkey"
    PRIMARY KEY ("@Accounts");
--
-- Definition for index CatsToAccs_pkey (OID = 16416) : 
--
ALTER TABLE ONLY "CatsToAccs"
    ADD CONSTRAINT "CatsToAccs_pkey"
    PRIMARY KEY ("@CatsToAccs");
--
-- Definition for index Accounts (OID = 16418) : 
--
ALTER TABLE ONLY "CatsToAccs"
    ADD CONSTRAINT "Accounts"
    FOREIGN KEY ("@Accounts") REFERENCES "Accounts"("@Accounts") ON UPDATE RESTRICT ON DELETE RESTRICT;
--
-- Definition for index Categories (OID = 16423) : 
--
ALTER TABLE ONLY "CatsToAccs"
    ADD CONSTRAINT "Categories"
    FOREIGN KEY ("@Categories") REFERENCES "Categories"("@Categories");
--
-- Definition for index Assets_pkey (OID = 16434) : 
--
ALTER TABLE ONLY "Assets"
    ADD CONSTRAINT "Assets_pkey"
    PRIMARY KEY ("@Assets");
--
-- Comments
--
COMMENT ON SCHEMA public IS 'standard public schema';
