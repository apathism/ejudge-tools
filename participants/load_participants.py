#!/usr/bin/python2
#-*- coding: utf-8 -*- 
from __future__ import unicode_literals
import MySQLdb
import codecs

PARTICIPANTS_CSV = "logins-passwords.csv"

def execute_cursor(cursor, query, *kwargs):
	formatted_query = query.format(*kwargs)
	cursor.execute(formatted_query)

def register_in_mysql(userlist):
	db = MySQLdb.connect(host="localhost",
	                     user="ejudge",
	                     passwd="password",
	                     db="ejudge",
	                     charset="utf8",
	                     use_unicode=True)
	db.set_character_set('utf8')
	cur = db.cursor()

	for user in userlist:
                if int(user['login'].split('-')[1]) not in xrange(1, 19):
                        continue
		execute_cursor(cur, u'INSERT INTO logins (login, password) VALUES ("{}", "{}");',
                               user['login'], user['password'])
		user_id = cur.lastrowid
		execute_cursor(cur, u'INSERT INTO cntsregs (user_id, contest_id) VALUES ({}, {});', user_id, 5)
                execute_cursor(cur, u'INSERT INTO cntsregs (user_id, contest_id, incomplete, locked) VALUES ({}, {}, {}, {});',
                               user_id, 6, 1, 0 if user['login'].startswith('f9-') else 1)
                execute_cursor(cur, u'INSERT INTO cntsregs (user_id, contest_id, incomplete, locked) VALUES ({}, {}, {}, {});',
                               user_id, 7, 1, 1 if user['login'].startswith('f9-') else 0)
	db.commit()

def load_user_csv():
	file = codecs.open(PARTICIPANTS_CSV, "r", encoding="utf-8")

	userlist = []
	for line in file.readlines():
		data = line.strip().split(",")
		if len(data) <= 1:
			break
		cur_user = {}
		cur_user['login'] = data[0]
		cur_user['password'] = data[1]
		userlist.append(cur_user)
	return userlist


users = load_user_csv()
register_in_mysql(users)
