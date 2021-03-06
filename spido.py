#!/usr/bin/python

import re,logging
from sys import exit,version_info as ver
from optparse import OptionParser
from stat import S_ISREG,S_ISFIFO,S_ISLNK,S_ISSOCK
from os import path,uname,stat

try:
	if ver[0] == 3:
		from configparser import ConfigParser
	else:
		from ConfigParser import ConfigParser
except Exception,e:
	print(e)
	exit(1)

# Configure option parsing
parser = OptionParser()
parser.add_option('-c','--config-file',dest='conf',
	default='spido.conf',metavar='FILE',
	help='Path to spido.conf, default is ./spido.conf')
(options,args) = parser.parse_args()

# Setup the config parser
config = ConfigParser()
try:
	config.read(options.conf)
except Exception,e:
	print(e)
	parser.print_help()
	exit(1)

# Make sure options are there
confopts = ['logfile','summary','uncompress','regexes','skip_types']
for i in confopts:
	if config.has_option('main',i) == False:
		print('Option %s missing from config file' % i)
		exit(1)

try:
	logfile = config.get('main','logfile')
	summary = config.getboolean('main','summary')
	unpak = config.getboolean('main','uncompress')
	regexs = config.get('main','regexes')
	skip_types = config.get('main','skip_types')
except Exception,e:
	print(e)
	exit(1)

# Verify our options
pathopts = [logfile,regexs,skip_types]
boolopts = [summary,unpak]
for p in pathopts:
	if not path.exists(p):
		print('Some file path(s) in config file do not exist')
		exit(1)
for b in boolopts:
	if not isinstance(b,bool):
		print('summary or uncompress options may not be boolean '\
			'(0 or 1,true or false,True or False)')

# Setup the logger
logger = logging.getLogger('spido')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s > %(message)s')
logh = logging.FileHandler(logfile,mode='a')
logh.setLevel(logging.DEBUG)
logh.setFormatter(formatter)
logger.addHandler(logh)

# Set hostname
hostname = uname()[1]

# Get regexes from file
with open(regexs,'r') as f:
	data = []
	for i in f.read().splitlines():
		if not i.strip().startswith('#'):
			data.append(i.strip())
	regs = re.compile('|'.join('({0})'.format(x) for x in data))
	del data,i,regexs

# Get skip_types
with open(skip_types,'r') as f:
	stypes = []
	for i in f.read().splitlines():
		if not i.strip().startswith('#'):
			stypes.append('.'+i.strip())
	del i,skip_types
