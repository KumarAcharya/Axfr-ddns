'''
Created on Sep 21, 2015

@author: ma501v,rt251j
'''
import ConfigParser
import MySQLdb
import uuid
from oslo_log import log as logging
from contextlib import closing
from com.att.aic.openstack.designate.ddns import getconfig

class DbConn:
	LOG = logging.getLogger(__name__)
	config = getconfig.Config()
	configParser = config.getConfig()
	
	host = configParser['host']
	database = configParser['db']
	user = configParser['user']
	password = configParser['pass']
	dbtype = configParser['dbtype']
	
	def getConnection(self):
		try:
			return MySQLdb.connect(self.host, self.user, self.password, self.database)
		except Exception:
			self.LOG.exception("Unable to connect to the Database.  Please check your DB credentials in the ddns.conf")
			raise
    
	def getLock(self):
		db = self.getConnection()
        try:
            cursor = db.cursor()
            sql = "SELECT * FROM eiss_update WHERE locked = 'TRUE'"
            row_count = cursor.execute(sql)
        except Exception:
            self.LOG.exception("Error While executing the Query.")
            raise
        finally:
            db.close()
        return row_count
       
	def setLock(self, type):
		db = self.getConnection()
		id = uuid.uuid4()
        try:
            cursor = db.cursor()
            sql = "INSERT INTO eiss_update (id, updated, locked, status, update_type) VALUES (%s, CURRENT_TIMESTAMP, 'TRUE', 'P', %s)" % (id, type)
            row_count = cursor.execute(sql)
        except Exception:
            self.LOG.exception("Error While Acquiring the Query.")
            raise
        finally:
            db.close()
    	return id

	def releaseLock(self, id):
		db = self.getConnection()
		try:
			cursor = db.cursor()
			sql = "UPDATE eiss_update SET locked = 'FALSE', status = 'C' WHERE id = " % id
			row_count = cursor.execute(sql)
		except Exception:
			self.LOG.exception("Error While releasing Lock.")
			raise
		finally:
			db.close()

	def getRecords(self):
		results,sql = (None, None)
		
		db = self.getConnection()
		try:		
			with closing(db.cursor()) as cursor:
				sql= """SELECT rd.created_at, rd.updated_at, rd.data, rd.action, rs.name, rs.type, rs.ttl 
						FROM records rd, recordsets rs 
						WHERE
						rd.updated_at IS NULL
						AND rd.created_at >  (now() - interval 1 minute - interval second(now()) second)
						AND rd.created_at <= (now() - interval second(now()) second)
						AND rs.id = rd.recordset_id 
						UNION 
						SELECT rd.created_at, rd.updated_at, rd.data, rd.action, rs.name, rs.type, rs.ttl 
						FROM records rd, recordsets rs 
						WHERE
						rd.updated_at IS NOT NULL
						AND rd.updated_at >  (now() - interval 1 minute - interval second(now()) second)
						AND rd.updated_at <= (now() - interval second(now()) second)
						AND rs.id = rd.recordset_id AND rs.type != 'SOA'"""
				self.LOG.debug("Executing the Query : %s", sql)
				cursor.execute(sql)
				results = cursor.fetchall()				
		except Exception:
			self.LOG.exception("Error While executing the Query.")
			raise
		finally:
			db.close()
			
		return results

	def getAll(self):
		db = self.getConnection()
		try:
			cursor = db.cursor()
			sql = "SELECT * FROM records, recordsets where records.recordset_id = recordsets.id"
			row_count = cursor.execute(sql)
		except Exception:
			self.LOG.exception("Error While executing the Query.")
			raise
		finally:
			db.close()
		return row_count

	def get_record(self, fqdn):
		db = self.getConnection()
		try:
			cursor = db.cursor()
			sql = "select rec.action, rec.data, rset.name, rset.type, rset.ttl from records rec, recordsets rset where rec.recordset_id = rset.id and rset.name = %s", fqdn
			row_count = cursor.execute(sql)
			results = cursor.fetchall()
		except Exception:
			self.LOG.exception("Error While executing the Query.")
			raise
		finally:
			db.close()
		return results
		