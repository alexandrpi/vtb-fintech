chcp 1251
psql -h vtb-clients.cncpsfr8xl23.us-east-2.rds.amazonaws.com -p 5432 -f vtb_users_db.sql -L logs/db_creation.log -U apostgres -W VTBClients
pause