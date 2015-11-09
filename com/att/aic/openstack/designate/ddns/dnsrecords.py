'''
Created on Sep 21, 2015

@author: ma501v
'''
import dns.query
import dns.tsigkeyring
import dns.update
import sys
from oslo_log import log as logging
import datetime
import time

from com.att.aic.openstack.designate.ddns import getconfig, dbconn
class DnsRecords:
    LOG = logging.getLogger(__name__)
	
    def updatedns_records(self):
        config = getconfig.Config()
        configParser = config.getConfig()
        dbcon = dbconn.DbConn()
        keyname = configParser['keyname']
        secretkey = configParser['secretkey']
        zone = configParser['zone']
        dnsServer = configParser['dnsserver']
        ddnsRecords = dbcon.getRecords()
        self.LOG.debug("keyname: {}, secretkey: {}, zone: {}, dnsserver: {}".format(keyname,secretkey,zone, dnsServer))
        for row in ddnsRecords:
            '''created_at          | updated_at          | data        | action | name                 | type | ttl'''
            '''vmname = row[4].split('.')[0]'''
            vmname = row[4][:len(row[4])-(len(zone)+1)]
            ip = row[2]
            recType = row[5]
            ttl = row[6]
            created = row[0]
            updated = row[1]
            action = row[3]
            if (action == 'UPDATE') or (action == 'CREATE'):
                try:
                    keyring = dns.tsigkeyring.from_text({keyname : secretkey})
                except:
                    raise

                update = dns.update.Update(zone, keyring=keyring)
                self.LOG.debug("vmname: {}, ip {}, record Type: {}".format(vmname, ip, recType))
                update.replace(vmname, 300, recType, ip)

                try:
                    response = dns.query.tcp(update, dnsServer)
                except dns.tsig.PeerBadKey:
                    self.LOG.exception ("The remote DNS server ns5.kcdc.att.com. did not accept the key passed.")
                    raise
                except Exception, err:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    self.LOG.exception ("type: %s, obj: %s, tb: %s" % (exc_type, exc_obj, exc_tb))
                    self.LOG.exception ("Unhandled exception in add_forward_record: %s" % err)
                    raise
                self.LOG.debug("Forward Record Output: %s" % response)

    def deletedns_records(self):
        config = getconfig.Config()
        dbcon = dbconn.DbConn()
        configParser = config.getConfig()
        keyname = configParser['keyname']
        secretkey = configParser['secretkey']
        zone = configParser['zone']
        dnsServer = configParser['dnsserver']
        ddnsRecords = dbcon.getRecords()
        self.LOG.debug("zone: {}, dnsserver: {}".format(zone, dnsServer))
        for row in ddnsRecords:
            '''rd.created_at, rd.updated_at, rd.data, rs.name, rs.type, rs.ttl'''
            vmname = row[4][:len(row[4])-(len(zone)+1)]
            ip = row[2]
            recType = row[5]
            created = row[0]
            updated = row[1]
            action = row[3]
            if action == 'DELETE':
                try:
                    keyring = dns.tsigkeyring.from_text({keyname : secretkey})
                except:
                    raise
                update = dns.update.Update(zone, keyring=keyring)
                self.LOG.debug("vmname: {}, recordType: {}".format(vmname, recType))
                update.delete(vmname, recType)

                try:
                    response = dns.query.tcp(update, dnsServer)
                except dns.tsig.PeerBadKey:
                    self.LOG.exception("The remote DNS server ns5.kcdc.att.com. did not accept the key passed.")
                    raise
                except Exception, err:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    self.LOG.exception("type: %s, obj: %s, tb: %s" % (exc_type, exc_obj, exc_tb))
                    self.LOG.exception("Unhandled exception in add_forward_record: %s" % err)
                    raise
                self.LOG.debug("Forward Record Output: %s" % response)
