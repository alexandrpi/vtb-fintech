DROP DATABASE IF EXISTS "FinancialStatements";

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

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


CREATE FUNCTION update_accs() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
	WITH t AS (SELECT "@Accounts", "OperationType" FROM public."CatsToAccs"
		WHERE "@Categories"=NEW."@Categories")
    UPDATE public."Accounts" a
    	SET "AccountTotal"=a."AccountTotal" + t."OperationType" * NEW."OperationTotal"
    FROM
    	public."Accounts" accs
    INNER JOIN
    	t
    ON
    	accs."@Accounts"=t."@Accounts";
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_accs() OWNER TO postgres;


SET default_tablespace = '';

SET default_with_oids = false;


CREATE TABLE "Accounts" (
    "@Accounts" integer DEFAULT nextval(('public.Accounts_@accounts_seq'::text)::regclass) NOT NULL,
    "Name" text NOT NULL,
    "AccountTotal" double precision NOT NULL
);


ALTER TABLE "Accounts" OWNER TO postgres;


CREATE SEQUENCE "Accounts_@accounts_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE "Accounts_@accounts_seq" OWNER TO postgres;


CREATE TABLE "Assets" (
    "@Assets" integer DEFAULT nextval(('public.Assets_@assets_seq'::text)::regclass) NOT NULL,
    "Name" text NOT NULL,
    "Type" smallint NOT NULL,
    "AssetFormula" text NOT NULL
);


ALTER TABLE "Assets" OWNER TO postgres;


CREATE SEQUENCE "Assets_@assets_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE "Assets_@assets_seq" OWNER TO postgres;


CREATE TABLE "Categories" (
    "@Categories" integer DEFAULT nextval(('public.Categories_@categories_seq'::text)::regclass) NOT NULL,
    "Name" text NOT NULL,
	"CategoryType" smallint NOT NULL
);


ALTER TABLE "Categories" OWNER TO postgres;


CREATE SEQUENCE "Categories_@categories_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE "Categories_@categories_seq" OWNER TO postgres;


CREATE TABLE "CatsToAccs" (
    "@CatsToAccs" integer DEFAULT nextval(('public.Catstoaccs_@catstoaccs_seq'::text)::regclass) NOT NULL,
    "@Categories" integer NOT NULL,
    "@Accounts" integer NOT NULL,
    "OperationType" smallint NOT NULL
);


ALTER TABLE "CatsToAccs" OWNER TO postgres;


CREATE SEQUENCE "Catstoaccs_@catstoaccs_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE "Catstoaccs_@catstoaccs_seq" OWNER TO postgres;


CREATE TABLE "Operations" (
    "@Operations" bigint NOT NULL,
    "@Categories" integer NOT NULL,
    "OperationTotal" double precision NOT NULL,
    "OperationDate" timestamp(0) with time zone,
    "Commentary" text
);


ALTER TABLE "Operations" OWNER TO postgres;


CREATE SEQUENCE "Operations_@Operations_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE "Operations_@Operations_seq" OWNER TO postgres;


ALTER SEQUENCE "Operations_@Operations_seq" OWNED BY "Operations"."@Operations";


ALTER TABLE ONLY "Operations" ALTER COLUMN "@Operations" SET DEFAULT nextval('"Operations_@Operations_seq"'::regclass);


ALTER TABLE ONLY "Accounts"
    ADD CONSTRAINT "Accounts_pkey" PRIMARY KEY ("@Accounts");


ALTER TABLE ONLY "Assets"
    ADD CONSTRAINT "Assets_pkey" PRIMARY KEY ("@Assets");


ALTER TABLE ONLY "Categories"
    ADD CONSTRAINT "Categories_pkey" PRIMARY KEY ("@Categories");


ALTER TABLE ONLY "CatsToAccs"
    ADD CONSTRAINT "CatsToAccs_pkey" PRIMARY KEY ("@CatsToAccs");


ALTER TABLE ONLY "Operations"
    ADD CONSTRAINT "Operations_pkey" PRIMARY KEY ("@Operations");


CREATE TRIGGER "Operations_tr" AFTER INSERT ON "Operations" FOR EACH ROW EXECUTE PROCEDURE update_accs();


ALTER TABLE ONLY "CatsToAccs"
    ADD CONSTRAINT "Accounts_fk" FOREIGN KEY ("@Accounts") REFERENCES "Accounts"("@Accounts") ON UPDATE RESTRICT ON DELETE RESTRICT;


ALTER TABLE ONLY "CatsToAccs"
    ADD CONSTRAINT "Categories_fk" FOREIGN KEY ("@Categories") REFERENCES "Categories"("@Categories");


ALTER TABLE ONLY "Operations"
    ADD CONSTRAINT "Categories_fk" FOREIGN KEY ("@Categories") REFERENCES "Categories"("@Categories") ON UPDATE RESTRICT ON DELETE RESTRICT;