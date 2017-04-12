sudo -u postgres psql -c "DROP DATABASE IF EXISTS transitionsdb;"
sudo -u postgres psql -c "DROP ROLE IF EXISTS simplequant;"
sudo -u postgres psql -c "CREATE USER simplequant WITH PASSWORD 'simplequantpwd';"
sudo -u postgres psql -c "CREATE DATABASE transitionsdb ENCODING 'UTF8';" 
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE transitionsdb TO simplequant;"

sudo -u postgres psql -d transitionsdb -a -c "SET ROLE 'simplequant';CREATE TABLE transition(id SERIAL PRIMARY KEY, name varchar(80), strategy_name varchar(120), object varchar(120), duration INT, customize_parameter varchar(1024));"
#sudo -u postgres psql -d transitionsdb -a -c "SET ROLE 'simplequant';INSERT INTO transition(id, name, strategy_name, object, duration, customize_parameter) VALUES (1, 'newTransition', '', '', 100, '');"
