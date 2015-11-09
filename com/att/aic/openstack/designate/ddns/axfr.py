#!/usr/bin/env python
# -*- coding: utf-8 -*-
import dns.query
import dns.resolver
import dns.zone
import dns.tsigkeyring
from oslo_log import log as logging

class Axfr:
    #keyring = dns.tsigkeyring.from_text({'aic-key' : 'fVlEv+7RaUD3xT7GEjTOtw=='})
    LOG = logging.getLogger(__name__)
    
    config = getconfig.Config()
    dbcon = dbconn.DbConn()
    
    configParser = config.getConfig()
    records = dbcon.getAll()
   
    zone = configParser['zone']
    dnsServer = configParser['dnsserver']

    def get_axfr(self):
        return dns.zone.from_xfr(dns.query.xfr(self.dnsServer, self.zone))

    def compareData(self):
        axfr_data = self.get_axfr()
        need_to_update = dict()
        try:
            for name in axfr_data.nodes.keys():
                data = z[name].to_text(name).split(" ")
                vmname = data[0]
                ttl = data[1]
                rec_type = data[2]
                ip_address = data[3]
                #ip_address = data[3].split(".")[0]
                #ipaddress = ipaddress.split("-")
                #ipaddress.pop(0)
                #ipaddress = ":".join(ipaddress)
                fqdn = vmname + self.zone
                records = dbcon.get_records(fqdn)
                
                #data | name | type | ttl
                if len(records) > 1:
                    raise Exception('Duplicates records found in Designate.')
                for row in records:
                    action = row[0]
                    data = row[1]
                    fqdn_name = row[2]
                    type = row[3]
                    ttl_value = row[4]
                    valid = True
                    if ip_address == data:
                        valid = True
                    else:
                        valid = False
                        break
                    if type == rec_type:
                        valid == True
                    else:
                        valid = False
                        break
                    if ttl == ttl_value:
                        valid = True
                    else:
                        valid = False
                        break
                
                    if valid == 'True':
                        self.LOG.debug("%s is upto date." %fqdn)
                    else:
                        update_eiss(action, data, vmname, type, ttl_value)
                
        except:
            self.LOG.exception("More then 1 record found for the requested Ip. Please check designate for duplicates")            
            raise            
        
    def update_eiss(self, action, ip, vmname, recType, ttl_value):
        config = getconfig.Config()
        configParser = config.getConfig()
        keyname = configParser['keyname']
        secretkey = configParser['secretkey']
        zone = configParser['zone']
        dnsServer = configParser['dnsserver']
        self.LOG.debug("keyname: {}, secretkey: {}, zone: {}, dnsserver: {}".format(keyname,secretkey,zone, dnsServer))
        try:
            keyring = dns.tsigkeyring.from_text({keyname : secretkey})
            update = dns.update.Update(zone, keyring=keyring)
        except:
            raise
        if (action == 'UPDATE') or (action == 'CREATE'):
            self.LOG.debug("vmname: {}, ip {}, record Type: {}".format(vmname, ip, recType))
            update.replace(vmname, ttl_value, recType, ip)
        elif (action == 'DELETE'):
            self.LOG.debug("vmname: {}, recordType: {}".format(vmname, recType))
            update.delete(vmname, recType)
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
                