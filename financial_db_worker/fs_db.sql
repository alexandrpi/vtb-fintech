DROP DATABASE IF EXISTS "FinancialStatements";

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;


--СОЗДАНИЕ БАЗЫ
CREATE DATABASE "FinancialStatements" WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'Russian_Russia.1251' LC_CTYPE = 'Russian_Russia.1251';

ALTER DATABASE "FinancialStatements" OWNER TO postgres;

\connect "FinancialStatements"

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;


CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_with_oids = false;

--НА СЛУЧАЙ, ЕСЛИ ТЕСТОВАЯ СХЕМА СУЩЕСТВУЕТ, УДАЛИМ ЕЕ
DROP SCHEMA IF EXISTS test_user CASCADE;

CREATE SCHEMA test_user;

CREATE FUNCTION test_user.update_accs() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
	WITH t AS (SELECT "@Accounts", "OperationType" FROM test_user."CatsToAccs"
		WHERE "@Categories"=NEW."@Categories")
    UPDATE test_user."Accounts" a
    	SET "AccountTotal"=a."AccountTotal" + t."OperationType" * NEW."OperationTotal"
    FROM t 
    WHERE 
    	a."@Accounts"=t."@Accounts";
    RETURN NEW;
END;
$$;

ALTER FUNCTION test_user.update_accs() OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;

CREATE TABLE test_user."Accounts" (
    "@Accounts" serial NOT NULL,
    "Name" text NOT NULL,
    "AccountTotal" double precision NOT NULL
);

ALTER TABLE test_user."Accounts" OWNER TO postgres;

CREATE TABLE test_user."Assets" (
    "@Assets" serial NOT NULL,
    "Name" text NOT NULL,
    "Type" smallint NOT NULL,
    "AssetFormula" text NOT NULL
);

ALTER TABLE test_user."Assets" OWNER TO postgres;

CREATE TABLE test_user."Categories" (
    "@Categories" serial NOT NULL,
    "Name" text NOT NULL,
	"CategoryType" smallint NOT NULL,
	"Parent" text
);

ALTER TABLE test_user."Categories" OWNER TO postgres;

CREATE TABLE test_user."CatsToAccs" (
    "@CatsToAccs" serial NOT NULL,
    "@Categories" integer NOT NULL,
    "@Accounts" integer NOT NULL,
    "OperationType" double precision NOT NULL
);

ALTER TABLE test_user."CatsToAccs" OWNER TO postgres;

CREATE TABLE test_user."Operations" (
    "@Operations" bigserial NOT NULL,
    "@Categories" integer NOT NULL,
    "OperationTotal" double precision NOT NULL,
    "OperationDate" timestamp(0) with time zone,
    "Commentary" text
);

ALTER TABLE test_user."Operations" OWNER TO postgres;

ALTER TABLE ONLY test_user."Accounts"
    ADD CONSTRAINT "Accounts_pkey" PRIMARY KEY ("@Accounts");

ALTER TABLE ONLY test_user."Assets"
    ADD CONSTRAINT "Assets_pkey" PRIMARY KEY ("@Assets");

ALTER TABLE ONLY test_user."Categories"
    ADD CONSTRAINT "Categories_pkey" PRIMARY KEY ("@Categories");

ALTER TABLE ONLY test_user."CatsToAccs"
    ADD CONSTRAINT "CatsToAccs_pkey" PRIMARY KEY ("@CatsToAccs");

ALTER TABLE ONLY test_user."Operations"
    ADD CONSTRAINT "Operations_pkey" PRIMARY KEY ("@Operations");

CREATE TRIGGER "Operations_tr" AFTER INSERT ON test_user."Operations" FOR EACH ROW EXECUTE PROCEDURE test_user.update_accs();

ALTER TABLE ONLY test_user."CatsToAccs"
    ADD CONSTRAINT "Accounts_fk" FOREIGN KEY ("@Accounts") REFERENCES test_user."Accounts"("@Accounts") ON UPDATE RESTRICT ON DELETE RESTRICT;

ALTER TABLE ONLY test_user."CatsToAccs"
    ADD CONSTRAINT "Categories_fk" FOREIGN KEY ("@Categories") REFERENCES test_user."Categories"("@Categories");

ALTER TABLE ONLY test_user."Operations"
    ADD CONSTRAINT "Categories_fk" FOREIGN KEY ("@Categories") REFERENCES test_user."Categories"("@Categories") ON UPDATE RESTRICT ON DELETE RESTRICT;

--НАПОЛНЕНИЕ БАЗЫ
COPY test_user."Accounts"
FROM :accs_path
(FORMAT 'csv', DELIMITER ';', HEADER TRUE, ENCODING 'utf8');

COPY test_user."Categories"
FROM :cats_path
(FORMAT 'csv', DELIMITER ';', HEADER TRUE, ENCODING 'utf8');

COPY test_user."CatsToAccs" ("@Categories", "@Accounts", "OperationType")
FROM :ctas_path
(FORMAT 'csv', DELIMITER ';', HEADER TRUE, ENCODING 'utf8');

COPY test_user."Assets" ("Name", "Type", "AssetFormula")
FROM :asts_path
(FORMAT 'csv', DELIMITER ';', HEADER TRUE, ENCODING 'utf8');

UPDATE test_user."Accounts"
SET "AccountTotal"=50000
WHERE "@Accounts" IN (50, 51)