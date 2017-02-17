from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from django.conf import settings
import bitaddress

def get_rpc():
	if not getattr(settings, 'TESTING', False):
		return AuthServiceProxy("http://%s:%s@%s:%s" % (getattr(settings, 'RPC_USERNAME'),
			getattr(settings, 'RPC_PASSWORD'),
			getattr(settings, 'RPC_IP'),
			getattr(settings, 'RPC_PORT')))

def new_address():
	if not getattr(settings, 'TESTING', False):
		rpc = get_rpc()
		return rpc.getnewaddress()
	else:
		return bitaddress.generate_address()

def getreceivedbyaddress(address, confirms):
	if not getattr(settings, 'TESTING', False):
		rpc = get_rpc()
		return rpc.getreceivedbyaddress(address, confirms)
	else:
		return 0

def settxfee(fee):
	if not getattr(settings, 'TESTING', False):
		rpc = get_rpc()
		rpc.settxfee(fee)

def sendtoaddress(addr, ammount):
	if not getattr(settings, 'TESTING', False):
		rpc = get_rpc()
		rpc.sendtoaddress(address, ammount)

def validateaddress(addr):
	if getattr(settings, 'TESTING', False):
		return get_rpc().validateaddress(request.GET['address'])
	return len(addr) == 34 # TODO: More accurate
