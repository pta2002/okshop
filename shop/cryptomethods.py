from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from django.conf import settings
import bitaddress

def get_rpc():
	if not settings.TESTING:
		return AuthServiceProxy("http://%s:%s@%s:%s" % (getattr(settings, 'RPC_USERNAME'),
			getattr(settings, 'RPC_PASSWORD'),
			getattr(settings, 'RPC_IP'),
			getattr(settings, 'RPC_PORT')))

def new_address():
	if not settings.TESTING:
		rpc = get_rpc()
		return rpc.getnewaddress()
	else:
		return bitaddress.generate_address()

def getreceivedbyaddress(address, confirms):
	if not settings.TESTING:
		rpc = get_rpc()
		return rpc.getreceivedbyaddress(address, confirms)
	else:
		return 10

def settxfee(fee):
	if not settings.TESTING:
		rpc = get_rpc()
		rpc.settxfee(fee)

def sendtoaddress(addr, ammount):
	if not settings.TESTING:
		rpc = get_rpc()
		rpc.sendtoaddress(address, ammount)

def validateaddress(addr):
	if settings.TESTING:
		return get_rpc().validateaddress(request.GET['address'])
	return len(addr) == 34 # TODO: More accurate