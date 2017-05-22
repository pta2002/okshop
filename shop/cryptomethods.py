from bitcoinrpc.authproxy import AuthServiceProxy
from django.conf import settings
import bitaddress


def get_rpc():
    if not getattr(settings, 'TESTING', False):
        return AuthServiceProxy("http://%s:%s@%s:%s" % (getattr(settings,
                                                                'RPC_USERNAME'),
                                                        getattr(settings, 'RPC_PASSWORD'),
                                                        getattr(settings, 'RPC_IP'),
                                                        getattr(settings, 'RPC_PORT')))


def new_address():
    if not getattr(settings, 'TESTING', False):
        rpc = get_rpc()
        return rpc.getnewaddress()
    return bitaddress.generate_address(version=0x37)


def getreceivedbyaddress(address, confirms):
    if not getattr(settings, 'TESTING', False):
        rpc = get_rpc()
        return rpc.getreceivedbyaddress(address, confirms)
    return 0


def settxfee(fee):
    if not getattr(settings, 'TESTING', False):
        rpc = get_rpc()
        rpc.settxfee(fee)


def sendtoaddress(addr, ammount):
    if not getattr(settings, 'TESTING', False):
        rpc = get_rpc()
        rpc.sendtoaddress(addr, ammount)


def validateaddress(addr):
    if getattr(settings, 'TESTING', False):
        return get_rpc().validateaddress(addr)
    return {'isvalid': len(addr) == 34}  # TODO: More accurate
