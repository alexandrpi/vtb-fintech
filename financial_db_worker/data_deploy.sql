COPY "{username}"."Accounts" ("AccountID", "Name", "AccountTotal")
FROM '{path}/init_data/accounts.csv'
(FORMAT 'csv', DELIMITER ';', HEADER TRUE, ENCODING 'utf8');

COPY "{username}"."Categories"
FROM '{path}/init_data/categories.csv'
(FORMAT 'csv', DELIMITER ';', HEADER TRUE, ENCODING 'utf8');

COPY "{username}"."CatsToAccs" ("@Categories", "AccountID", "OperationType")
FROM '{path}/init_data/catstoaccs.csv'
(FORMAT 'csv', DELIMITER ';', HEADER TRUE, ENCODING 'utf8');

COPY "{username}"."Assets" ("Name", "Type", "AssetFormula")
FROM '{path}/init_data/assets.csv'
(FORMAT 'csv', DELIMITER ';', HEADER TRUE, ENCODING 'utf8');

UPDATE "{username}"."Accounts"
SET "AccountTotal"={account_sum}
WHERE "AccountID" IN (50, 51)