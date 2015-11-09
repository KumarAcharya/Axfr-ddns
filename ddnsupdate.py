import sys
import time

from com.att.aic.openstack.designate.ddns import getconfig, dnsrecords, dbconn

import logging as LOG


'''LOG = logging.getLogger(__name__)'''

config = getconfig.Config()
configParser = config.getConfig()
dbcon = dnconn.DbConn()
logfile = configParser['logfile']

LOG.basicConfig(filename=logfile,level=LOG.DEBUG)
rec_count = dbcon.getLock()
if rec_count < 0:
    id = dbcon.setLock()
    LOG.debug("Getting DNS records that were created in the previous Minute....")
    dnsRecs = dnsrecords.DnsRecords()
    LOG.debug("Publishing Created|Updated records to the EISS DNS Server")
    dnsRecs.updatedns_records()
    LOG.debug("Publishing Deleted records to the EISS DNS Server")
    dnsRecs.deletedns_records()
    LOG.debug("Done with Publishing Records to the EISS")
    dbcon.releaseLock(id)
elif rec_count > 0:
    LOG.debug("Lock found in Database. DNS records Update is already in execution")