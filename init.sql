-- Убедитесь, что корень имеет доступ
ALTER USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY 'dev';

-- Создайте пользователя admin
CREATE USER 'admin'@'%' IDENTIFIED WITH mysql_native_password BY 'dev';

-- Дайте права пользователю admin
GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
