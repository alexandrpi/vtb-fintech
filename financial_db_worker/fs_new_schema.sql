CREATE SCHEMA {username};

CREATE FUNCTION {username}.update_accs() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
	WITH t AS (SELECT "@Accounts", "OperationType" FROM {username}."CatsToAccs"
		WHERE "@Categories"=NEW."@Categories")
    UPDATE {username}."Accounts" a
    	SET "AccountTotal"=a."AccountTotal" + t."OperationType" * NEW."OperationTotal"
    FROM t 
    WHERE 
    	a."@Accounts"=t."@Accounts";
    RETURN NEW;
END;
$$;

ALTER FUNCTION {username}.update_accs() OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;

CREATE TABLE {username}."Accounts" (
    "@Accounts" serial NOT NULL,
    "Name" text NOT NULL,
    "AccountTotal" double precision NOT NULL
);

ALTER TABLE {username}."Accounts" OWNER TO postgres;

CREATE TABLE {username}."Assets" (
    "@Assets" serial NOT NULL,
    "Name" text NOT NULL,
    "Type" smallint NOT NULL,
    "AssetFormula" text NOT NULL
);

ALTER TABLE {username}."Assets" OWNER TO postgres;

CREATE TABLE {username}."Categories" (
    "@Categories" serial NOT NULL,
    "Name" text NOT NULL,
	"CategoryType" smallint NOT NULL
);

ALTER TABLE {username}."Categories" OWNER TO postgres;

CREATE TABLE {username}."CatsToAccs" (
    "@CatsToAccs" serial NOT NULL,
    "@Categories" integer NOT NULL,
    "@Accounts" integer NOT NULL,
    "OperationType" smallint NOT NULL
);

ALTER TABLE {username}."CatsToAccs" OWNER TO postgres;

CREATE TABLE {username}."Operations" (
    "@Operations" bigserial NOT NULL,
    "@Categories" integer NOT NULL,
    "OperationTotal" double precision NOT NULL,
    "OperationDate" timestamp(0) with time zone,
    "Commentary" text
);

ALTER TABLE {username}."Operations" OWNER TO postgres;

ALTER TABLE ONLY {username}."Accounts"
    ADD CONSTRAINT "Accounts_pkey" PRIMARY KEY ("@Accounts");

ALTER TABLE ONLY {username}."Assets"
    ADD CONSTRAINT "Assets_pkey" PRIMARY KEY ("@Assets");

ALTER TABLE ONLY {username}."Categories"
    ADD CONSTRAINT "Categories_pkey" PRIMARY KEY ("@Categories");

ALTER TABLE ONLY {username}."CatsToAccs"
    ADD CONSTRAINT "CatsToAccs_pkey" PRIMARY KEY ("@CatsToAccs");

ALTER TABLE ONLY {username}."Operations"
    ADD CONSTRAINT "Operations_pkey" PRIMARY KEY ("@Operations");

CREATE TRIGGER "Operations_tr" AFTER INSERT ON {username}."Operations" FOR EACH ROW EXECUTE PROCEDURE {username}.update_accs();

ALTER TABLE ONLY {username}."CatsToAccs"
    ADD CONSTRAINT "Accounts_fk" FOREIGN KEY ("@Accounts") REFERENCES {username}."Accounts"("@Accounts") ON UPDATE RESTRICT ON DELETE RESTRICT;

ALTER TABLE ONLY {username}."CatsToAccs"
    ADD CONSTRAINT "Categories_fk" FOREIGN KEY ("@Categories") REFERENCES {username}."Categories"("@Categories");

ALTER TABLE ONLY {username}."Operations"
    ADD CONSTRAINT "Categories_fk" FOREIGN KEY ("@Categories") REFERENCES {username}."Categories"("@Categories") ON UPDATE RESTRICT ON DELETE RESTRICT;

