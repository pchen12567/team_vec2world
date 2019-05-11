"""
@Coding: uft-8 *
@Time: 2019-05-10 23:11
@Author: Ryne Chen
@File: input_corpus.py 
"""

import pymysql
import pandas as pd


# Set table type by DataFrame data type
def make_table_sql(df):
    # Get columns in df
    columns = df.columns.tolist()

    # Get data type list of each column
    types = df.ftypes

    # Init pattern list
    make_table = []

    for col in columns:
        # Set table type pattern
        if 'int' in types[col]:
            char = col + ' INT'
        elif 'float' in types[col]:
            char = col + ' FLOAT'
        elif 'object' in types[col]:
            char = col + ' TEXT'
        elif 'datetime' in types[col]:
            char = col + ' DATETIME'
        make_table.append(char)
    return ','.join(make_table)


# Input data from csv file to mysql database
def csv2mysql(db_name, table_name, df):
    # Create database if needed
    # cursor.execute('CREATE DATABASE IF NOT EXISTS {}'.format(db_name))

    # connect to database
    conn.select_db(db_name)

    # Create table in database if needed
    cursor.execute('DROP TABLE IF EXISTS {}'.format(table_name))
    cursor.execute('CREATE TABLE {}({})'.format(table_name, make_table_sql(df)))

    # Change timestamp type to string if needed
    # df['time'] = df['time'].astype('str')

    # Get df values
    values = df.values.tolist()

    # Get columns number
    s = ','.join(['%s' for _ in range(len(df.columns))])

    # executemany insert data
    cursor.executemany('INSERT INTO {} VALUES ({})'.format(table_name, s), values)


def main():
    # Set configuration
    config = {'host': 'cdb-q1mnsxjb.gz.tencentcdb.com', 'user': 'root', 'password': 'A1@2019@me',
              'port': 10102, 'database': 'news_chinese'}

    # Init connection
    global conn
    conn = pymysql.Connect(**config)

    # Confirm commit True
    conn.autocommit(1)

    # Init cursor
    global cursor
    cursor = conn.cursor()

    # Set input file path
    # file_path = '../corpus/data/toutiao_news_corpus.csv'
    # file_path = '../corpus/data/cn_news_corpus.csv'
    file_path = '../corpus/data/total_news_corpus.csv'

    # Load file to df
    df = pd.read_csv(file_path)

    # Init database name
    db_name = 'vec2world'

    # Init table name
    # table_name = 'toutiao_news'
    # table_name = 'cn_news'
    table_name = 'total_news'

    # Input data to mysql
    print('Start Input.......')
    csv2mysql(db_name, table_name, df)
    print('End!')


if __name__ == '__main__':
    main()
