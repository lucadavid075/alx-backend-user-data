#!/usr/bin/env python3
"""
Filter log module.
"""
import os
import re
import logging
import mysql.connector
from typing import List


PII_FIELDS = ("name", "email", "phone", "ssn", "password")


def filter_datum(
        fields: List[str], redaction: str, message: str, separator: str,
        ) -> str:
    """
    Obfuscates log message fields and returns
    the obfuscated log message fields
    """
    pattern_format = r'(?<={0})([^{0}\s]+)(?={0})'
    pattern = re.compile(pattern_format.format(re.escape(separator)))
    return pattern.sub(redaction, message)


def get_logger() -> logging.Logger:
    """
    Function that creates a new logger for user_data.
    """
    logger = logging.getLogger("user_data")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(RedactingFormatter(PII_FIELDS))
    logger.propagate = False
    logger.addHandler(handler)
    return logger


def get_db() -> mysql.connector.connection.MySQLConnection:
    """
    Function that creates a connector to the database.
    """
    db_username = os.getenv("PERSONAL_DATA_DB_USERNAME", "root")
    db_password = os.getenv("PERSONAL_DATA_DB_PASSWORD", "")
    db_host = os.getenv("PERSONAL_DATA_DB_HOST", "localhost")
    db_name = os.getenv("PERSONAL_DATA_DB_NAME", "")
    connection = mysql.connector.connect(
        user=db_username,
        password=db_password,
        host=db_host,
        database=db_name,
        port=3306,
    )
    return connection


def main():
    """Logs the information about user records in a table.
    """
    fields = "name,email,phone,ssn,password,ip,last_login,user_agent"
    columns = fields.split(',')
    query = "SELECT {} FROM users;".format(fields)
    info_logger = get_logger()
    connection = get_db()
    with connection.cursor() as cursor:
        cursor.execute(query)
        users = cursor.fetchall()
        for user in users:
            record = map(
                lambda x: '{}={}'.format(x[0], x[1]),
                zip(columns, user),
            )
            msg = '{};'.format('; '.join(list(record)))
            args = ("user_data", logging.INFO, None, None, msg, None, None)
            log_record = logging.LogRecord(*args)
            info_logger.handle(log_record)


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class
    """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """
        filter values in incoming log records
        """
        msg = super(RedactingFormatter, self).format(record)
        return filter_datum(self.fields, self.REDACTION, msg, self.SEPARATOR)


if __name__ == "__main__":
    main()
