--
-- VTBUsers database creation script
--


SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'WIN1251';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: VTBUsers; Type: DATABASE; Schema: -; Owner: postgres
--

DROP DATABASE IF EXISTS "VTBUsers";

CREATE DATABASE "VTBUsers"
  WITH OWNER = postgres
    ENCODING = 'UTF8'
    TABLESPACE = pg_default;
	
	
\connect "VTBUsers"

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

CREATE TABLE public."Organizations" (
  "@Organizations" BIGSERIAL,
  "PhoneNumber" VARCHAR(15) NOT NULL,
  "TelegramID" BIGINT NOT NULL,
  "VTBClient" BOOLEAN NOT NULL,
  "CLIENT_ID" BIGINT,
  "CLIENT_SECRET" TEXT,
  "INN" VARCHAR(12),
  "KPPs" VARCHAR(9) [],
  "OrgName" TEXT,
  "Account" VARCHAR(20),
  "BankName" TEXT,
  "BankCity" TEXT,
  "BankBIC" VARCHAR(9),
  "BankCorrAccount" VARCHAR(20),
  CONSTRAINT "Organizations_pkey" PRIMARY KEY("@Organizations")
);

