#!/usr/bin/env python2

import json
from bitcoin.rpc import Proxy

import httplib
import os.path

import platform

def get_proxy(user, password, port=8336):
     return Proxy(service_url="http://{0}:{1}@localhost:{2}".format(user, password, port))

class NameTakenError(ValueError):
    pass

class Namecoin(object):
    def __init__(self, proxy):
        self.proxy = proxy

    def get_secret(self, name):
        dns_record = self.proxy._call('name_show', 'd/' + name) # throws if the name doesn't exist, iirc
        name_info = json.loads(dns_record['value'])
        return name_info['syncnet']['secret'] # of course this could throw a KeyError

    def validate_address(self, name):
        try:
            self.clean_address(name)
        except ValueError:
            return False
        else:
            return True

    def clean_address(self, address):
        name, suffix = address.rsplit('.', 1)
        if suffix != 'bit':
            raise ValueError("Address {0} ends with suffix .{1} instead of .bit".format(address, suffix))
        else:
            return name

    def name_exists(self, name):
        dns_record = self.proxy._call('name_show', 'd/' + name) # throws if the name doesn't exist, iirc
        try:
            name_info = json.loads(dns_record['value'])
        except ValueError:
            return False
        else:
            return bool(name_info.get('syncnet', {}).get('secret')) # of course this could throw a KeyError

    def register_name(self, name):
        if self.name_exists(name):
            raise NameTakenError("Name {0}.bit taken!".format(name)) # XXX: we might own this name though

        txid, rnd = self.proxy._call("name_new", 'd/' + name)

        # XXX: Store txid and/or rnd for name_firstupdate, poll at/around expected time

    def test_connection(self):
        try:
            self.proxy._call('help')
            return True
        except:
            return False

    def _build_json_value(self, secret, existing=None):
        existing = dict(existing) or {}
        existing['syncnet'] = existing.get('syncnet', {})
        existing['syncnet']['secret'] = secret
        return existing
