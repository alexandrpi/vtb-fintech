--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.1
-- Dumped by pg_dump version 9.6.0

-- Started on 2017-01-30 02:55:07

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 2170 (class 1262 OID 16393)
-- Name: FinancialStatements; Type: DATABASE; Schema: -; Owner: postgres
--

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

--
-- TOC entry 1 (class 3079 OID 12387)
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- TOC entry 2172 (class 0 OID 0)
-- Dependencies: 1
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

--
-- TOC entry 195 (class 1255 OID 16518)
-- Name: update_accs(); Type: FUNCTION; Schema: public; Owner: postgres
--

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

--
-- TOC entry 186 (class 1259 OID 16405)
-- Name: Accounts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "Accounts" (
    "@Accounts" integer DEFAULT nextval(('public.Accounts_@accounts_seq'::text)::regclass) NOT NULL,
    "Name" text NOT NULL,
    "AccountTotal" double precision NOT NULL
);


ALTER TABLE "Accounts" OWNER TO postgres;

--
-- TOC entry 193 (class 1259 OID 16476)
-- Name: Accounts_@accounts_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE "Accounts_@accounts_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE "Accounts_@accounts_seq" OWNER TO postgres;

--
-- TOC entry 188 (class 1259 OID 16428)
-- Name: Assets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "Assets" (
    "@Assets" integer DEFAULT nextval(('public.Assets_@assets_seq'::text)::regclass) NOT NULL,
    "Name" text NOT NULL,
    "AssetTotal" double precision NOT NULL,
    "Type" smallint NOT NULL,
    "AssetFormula" text NOT NULL
);


ALTER TABLE "Assets" OWNER TO postgres;

--
-- TOC entry 192 (class 1259 OID 16471)
-- Name: Assets_@assets_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE "Assets_@assets_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE "Assets_@assets_seq" OWNER TO postgres;

--
-- TOC entry 185 (class 1259 OID 16397)
-- Name: Categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "Categories" (
    "@Categories" integer DEFAULT nextval(('public.Categories_@categories_seq'::text)::regclass) NOT NULL,
    "Name" text
);


ALTER TABLE "Categories" OWNER TO postgres;

--
-- TOC entry 194 (class 1259 OID 16486)
-- Name: Categories_@categories_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE "Categories_@categories_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE "Categories_@categories_seq" OWNER TO postgres;

--
-- TOC entry 187 (class 1259 OID 16413)
-- Name: CatsToAccs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "CatsToAccs" (
    "@CatsToAccs" integer DEFAULT nextval(('public.Catstoaccs_@catstoaccs_seq'::text)::regclass) NOT NULL,
    "@Categories" integer NOT NULL,
    "@Accounts" integer NOT NULL,
    "OperationType" smallint NOT NULL
);


ALTER TABLE "CatsToAccs" OWNER TO postgres;

--
-- TOC entry 191 (class 1259 OID 16458)
-- Name: Catstoaccs_@catstoaccs_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE "Catstoaccs_@catstoaccs_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE "Catstoaccs_@catstoaccs_seq" OWNER TO postgres;

--
-- TOC entry 189 (class 1259 OID 16446)
-- Name: Operations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "Operations" (
    "@Operations" bigint NOT NULL,
    "@Categories" integer NOT NULL,
    "OperationTotal" double precision NOT NULL,
    "OperationDate" timestamp(0) with time zone,
    "Commentary" text
);


ALTER TABLE "Operations" OWNER TO postgres;

--
-- TOC entry 190 (class 1259 OID 16449)
-- Name: Operations_@Operations_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE "Operations_@Operations_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE "Operations_@Operations_seq" OWNER TO postgres;

--
-- TOC entry 2173 (class 0 OID 0)
-- Dependencies: 190
-- Name: Operations_@Operations_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE "Operations_@Operations_seq" OWNED BY "Operations"."@Operations";


--
-- TOC entry 2034 (class 2604 OID 16510)
-- Name: Operations @Operations; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "Operations" ALTER COLUMN "@Operations" SET DEFAULT nextval('"Operations_@Operations_seq"'::regclass);


--
-- TOC entry 2038 (class 2606 OID 16479)
-- Name: Accounts Accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "Accounts"
    ADD CONSTRAINT "Accounts_pkey" PRIMARY KEY ("@Accounts");


--
-- TOC entry 2042 (class 2606 OID 16474)
-- Name: Assets Assets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "Assets"
    ADD CONSTRAINT "Assets_pkey" PRIMARY KEY ("@Assets");


--
-- TOC entry 2036 (class 2606 OID 16489)
-- Name: Categories Categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "Categories"
    ADD CONSTRAINT "Categories_pkey" PRIMARY KEY ("@Categories");


--
-- TOC entry 2040 (class 2606 OID 16461)
-- Name: CatsToAccs CatsToAccs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "CatsToAccs"
    ADD CONSTRAINT "CatsToAccs_pkey" PRIMARY KEY ("@CatsToAccs");


--
-- TOC entry 2044 (class 2606 OID 16502)
-- Name: Operations Operations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "Operations"
    ADD CONSTRAINT "Operations_pkey" PRIMARY KEY ("@Operations");


--
-- TOC entry 2048 (class 2620 OID 16519)
-- Name: Operations Operations_tr; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER "Operations_tr" AFTER INSERT ON "Operations" FOR EACH ROW EXECUTE PROCEDURE update_accs();


--
-- TOC entry 2045 (class 2606 OID 16480)
-- Name: CatsToAccs Accounts_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "CatsToAccs"
    ADD CONSTRAINT "Accounts_fk" FOREIGN KEY ("@Accounts") REFERENCES "Accounts"("@Accounts") ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 2046 (class 2606 OID 16490)
-- Name: CatsToAccs Categories_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "CatsToAccs"
    ADD CONSTRAINT "Categories_fk" FOREIGN KEY ("@Categories") REFERENCES "Categories"("@Categories");


--
-- TOC entry 2047 (class 2606 OID 16495)
-- Name: Operations Categories_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "Operations"
    ADD CONSTRAINT "Categories_fk" FOREIGN KEY ("@Categories") REFERENCES "Categories"("@Categories") ON UPDATE RESTRICT ON DELETE RESTRICT;


-- Completed on 2017-01-30 02:55:08

--
-- PostgreSQL database dump complete
--

