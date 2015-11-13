from setuptools import setup, find_packages
import sys

setup(name="attdns", 
      version='1.0', 
      description='''Designate AXFR-DDNS module will post the DNS records that are 
                     created or updated or deleted to the AT&T EISS Servers.  
                     It also does an AXFR on a dialy basis and updates the 
                     DNS records in Mini DNS.''',
      packages=find_packages(),
      zip_safe=True
)
