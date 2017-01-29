from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from django.conf import settings

def get_rpc():
	return AuthServiceProxy("http://%s:%s@%s:%s" % (getattr(settings, 'RPC_USERNAME'),
		getattr(settings, 'RPC_PASSWORD'),
		getattr(settings, 'RPC_IP'),
		getattr(settings, 'RPC_PORT')))

def new_address():
	rpc = get_rpc()
	return rpc.getnewaddress()