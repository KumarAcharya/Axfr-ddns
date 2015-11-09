import sys
import time

from com.att.aic.openstack.designate.ddns import getconfig, dnsrecords, dbconn, axfr

import logging as LOG


'''LOG = logging.getLogger(__name__)'''

config = getconfig.Config()
axfr_v = axfr.Axfr()
configParser = config.getConfig()
dbcon = dnconn.DbConn()
logfile = configParser['logfile']

LOG.basicConfig(filename=logfile,level=LOG.DEBUG)
rec_count = dbcon.getLock()
if rec_count < 0:
    id = dbcon.setLock('AXFR')
    LOG.debug("Getting EISS records")
    axfr_v.compareData()
    LOG.debug("EISS has been updated")
    dbcon.releaseLock(id)
elif rec_count > 0:
    LOG.debug("Lock found in Database. EISS Update is already in execution")