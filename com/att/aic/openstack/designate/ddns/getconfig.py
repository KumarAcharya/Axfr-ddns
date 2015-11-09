'''
Created on Sep 21, 2015

@author: ma501v
'''
import ConfigParser

from oslo_log import log as logging

class Config:
	LOG = logging.getLogger(__name__)
	path = os.path.dirname(os.path.realpath(__file__))
	def getConfig(self):
		Config = ConfigParser.ConfigParser()
		# This is absolute path this needs to change to a relative path
		Config.read(path+"/ddns.conf")
		configparams = {}
		for section in Config.sections():
			options = Config.options(section)
			for option in options:
				try:
					configparams[option] = Config.get(section, option)
					if configparams[option] == -1:
						self.LOG.debug("skip: %s" % option)
				except:
					self.LOG.debug ("exception on %s!" % option)
					configparams[option] = None
		return configparams
