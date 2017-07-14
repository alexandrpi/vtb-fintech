--
-- VTBClients database creation script
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
-- Name: VTBClients; Type: DATABASE; Schema: -; Owner: postgres
--

\connect "VTBClients"

DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

CREATE TABLE public."Users" (
  "@Users" BIGINT NOT NULL,
  "PhoneNumber" VARCHAR(15) NOT NULL,
  "VTBClient" BOOLEAN NOT NULL,
  "INN" VARCHAR(12),
  "KPPs" TEXT DEFAULT '',
  "OrgName" TEXT,
  "Account" VARCHAR(20),
  "BankName" TEXT DEFAULT '',
  "BankCity" TEXT DEFAULT '',
  "BankBIC" VARCHAR(9),
  "BankCorrAccount" VARCHAR(20) DEFAULT '',
  "AccessToken" VARCHAR(64),
  "TokenExpires" TIMESTAMP DEFAULT now(),
  PRIMARY KEY("@Users")
);

CREATE TABLE public."Drafts" (
  "@Drafts" BIGSERIAL,
  "PayerID" BIGINT,
  "ReceiverID" BIGINT,
  "ReceiverPN" VARCHAR(15),
  "Reason" TEXT,
  "Total" MONEY,
  "DateFrom" TIMESTAMP DEFAULT now(),
  "Confirmed" BOOLEAN DEFAULT FALSE,
  PRIMARY KEY("@Drafts")
);

SET client_encoding = 'UTF-8';

COMMENT ON COLUMN public."Drafts"."ReceiverPN"
IS 'Номер телефона получателя платежа';

COMMENT ON COLUMN public."Drafts"."Reason"
IS 'Назначение платежа';

COMMENT ON COLUMN public."Drafts"."Total"
IS 'Сумма платежа';
