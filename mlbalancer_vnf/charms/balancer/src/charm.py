#!/usr/bin/env python3
# Copyright 2020 i2t
# See LICENSE file for licensing details.

import logging
import subprocess, os
import time

from ops.charm import CharmBase
from ops.main import main
from ops.framework import StoredState
#from charms.osm.sshproxy import SSHProxyCharm
from ops.model import (
    ActiveStatus,
    MaintenanceStatus,
)

logger = logging.getLogger(__name__)


class BalancerCharm(CharmBase):
    _stored = StoredState()

    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.install, self._on_install)
        self.framework.observe(self.on.start, self._on_start)
        self.framework.observe(self.on.server_relation_changed, self.get_server_ipaddr )
        #self.framework.observe(self.on.config_changed, self._on_config_changed)
        #self.framework.observe(self.on.fortune_action, self._on_fortune_action)
        self._stored.set_default(things=[])

    '''
    def _on_config_changed(self, _):
        current = self.config["thing"]
        if current not in self._stored.things:
            logger.debug("found a new thing: %r", current)
            self._stored.things.append(current)

    def _on_fortune_action(self, event):
        fail = event.params["fail"]
        if fail:
            event.fail(fail)
        else:
            event.set_results({"fortune": "A bug in the code is worth two in the documentation."})
    '''

    def _on_install(self, _):
        self.unit.status = MaintenanceStatus("Installing Proxy")
        subprocess.run(["apt", "update"])
        subprocess.run(["apt", "install", "-y", "git", "python3-pip", "haproxy"])
        self.unit.status = ActiveStatus("Proxy installed")

    def _on_start(self, _):
        self.unit.status = MaintenanceStatus("Starting Proxy")
        lines = [
            '',
            'listen mlappbalance',
            '        bind *:5000',
            '        balance roundrobin',
            '        option forwardfor',
            '        option httpchk']
        for ln in lines:
            cmd = f'echo "{ln}" >> /etc/haproxy/haproxy.cfg'
            subprocess.run(cmd, shell=True)
        self.unit.status = ActiveStatus("Proxy started")

    def get_server_ipaddr(self, event):
        self.unit.status = MaintenanceStatus("Reading Server IP")
        ip = event.relation.data[event.unit].get("ip")
        
        if(ip != None):
            ln = f'        server webserver{ip} {ip}:5000'
            cmd = f'echo "{ln}" >> /etc/haproxy/haproxy.cfg'
            subprocess.run(cmd, shell=True)
            cmd = 'service haproxy restart'
            subprocess.run(cmd, shell=True)
            self.unit.status = ActiveStatus(f"Added server {ip}")

if __name__ == "__main__":
    main(BalancerCharm)
