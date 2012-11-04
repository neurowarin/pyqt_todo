#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
@script  : test_model.py
@created : 2012-11-04 02:28:46.742
@changed : 2012-11-04 18:51:02.576
@creator : mkpy.py --version 0.0.27
@author  : Igor A.Vetrov <qprostu@gmail.com>
@about   : testing application model classes
"""
import os, sys
sys.path.insert( 0, os.path.normpath( os.path.join( os.getcwd(), '..' ) ) )
from db.sqlite import SQLite
from db.model import Priority, Task
import threading
import unittest
from datetime import datetime, date, timedelta
from sqlite3 import IntegrityError


__revision__ = 5



class PriorityTable(unittest.TestCase):

    def setUp(self):
        with threading.Lock():
            self.dbName = "test.sqlite3"
            self.db = SQLite(self.dbName)
            self.table = Priority(self.db)


    def tearDown(self):
        with threading.Lock():
            if os.path.exists(self.dbName):
                self.db.__del__()
                os.unlink(self.dbName)


    def test_table_exists(self):
        self.assertTrue( self.db.tableExists(self.table.name) )


    def test_create_sql(self):
        sql = "create table TodoPriority(\n" \
              "\tcode integer primary key not null,\n" \
              "\tname text not null,\n" \
              "\tcreated timestamp default (datetime('now', 'localtime'))\n" \
              ");"
        self.assertEqual( sql, self.table.createSql() )


    def test_defaults(self):
        cnt = self.table.count()
        self.assertEqual( cnt, 3 )


    def test_low(self):
        row = self.db.execSql( "select name from {} where code=?;".format(self.table.name), (1,) )[0]
        self.assertEqual( row["name"], "Low" )


    def test_medium(self):
        row = self.db.execSql( "select name from {} where code=?;".format(self.table.name), (2,) )[0]
        self.assertEqual( row["name"], "Medium" )


    def test_high(self):
        row = self.db.execSql( "select name from {} where code=?;".format(self.table.name), (3,) )[0]
        self.assertEqual( row["name"], "High" )



class TaskTable(unittest.TestCase):

    def setUp(self):
        with threading.Lock():
            self.dbName = "test.sqlite3"
            self.db = SQLite(self.dbName)
            self.priority = Priority(self.db)
            self.task = Task(self.db)
            self.db.execSql( "insert into {} (name, priority, deadline) values(?, ?, ?)".format(self.task.name),
                             ("Low Test", 1, date.today() + timedelta(2)) )
            self.db.execSql( "insert into {} (name, priority, deadline) values(?, ?, ?)".format(self.task.name),
                             ("Medium Test", 2, date.today() + timedelta(3)) )
            self.db.execSql( "insert into {} (name, priority, deadline) values(?, ?, ?)".format(self.task.name),
                             ("High Test", 3, date.today() + timedelta(4)) )


    def tearDown(self):
        with threading.Lock():
            if os.path.exists(self.dbName):
                self.db.__del__()
                os.unlink(self.dbName)


    def test_table_exists(self):
        self.assertTrue( self.db.tableExists(self.priority.name) )
        self.assertTrue( self.db.tableExists(self.task.name) )


    def test_create_sql(self):
        sql = "create table TodoTask(\n" \
              "\tid integer primary key autoincrement not null,\n" \
              "\tname text not null,\n" \
              "\tpriority integer references TodoPriority(code) default 2,\n" \
              "\tdeadline date not null default (date('now', 'localtime')),\n" \
              "\tstatus integer default 0,\n" \
              "\tcompleted timestamp,\n" \
              "\tcreated timestamp default (datetime('now', 'localtime'))\n" \
              ");"
        self.assertEqual( sql, self.task.createSql() )


    def test_index_exists(self):
        self.assertIn( "status", self.task.indices )


    def test_records(self):
        cnt = self.task.count()
        self.assertEqual( cnt, 3 )


    def test_low(self):
        row = self.db.execSql( "select * from {} where id=?;".format(self.task.name), (1,) )[0]
        self.assertEqual( row["name"], "Low Test" )
        self.assertEqual( row["priority"], 1 )
        self.assertEqual( row["deadline"], date.today() + timedelta(2) )


    def test_medium(self):
        row = self.db.execSql( "select * from {} where id=?;".format(self.task.name), (2,) )[0]
        self.assertEqual( row["name"], "Medium Test" )
        self.assertEqual( row["priority"], 2 )
        self.assertEqual( row["deadline"], date.today() + timedelta(3) )


    def test_high(self):
        row = self.db.execSql( "select * from {} where id=?;".format(self.task.name), (3,) )[0]
        self.assertEqual( row["name"], "High Test" )
        self.assertEqual( row["priority"], 3 )
        self.assertEqual( row["deadline"], date.today() + timedelta(4) )


    def test_integrity(self):
        self.assertRaises( IntegrityError, self.db.execSql,
                           "insert into {} (name, priority, deadline) values(?, ?, ?)".format(self.task.name),
                           ("Highest Test", 4, date.today() + timedelta(4)) )



if __name__ == '__main__':

    unittest.main(verbosity=2)

# end of test_model.py