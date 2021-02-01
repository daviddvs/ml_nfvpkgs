#!/usr/bin/env python3
# Copyright 2021 i2t
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


class MonitorCharm(CharmBase):
    _stored = StoredState()

    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.install, self._on_install)
        self.framework.observe(self.on.start, self._on_start)
        self.framework.observe(self.on.server_relation_changed, self.get_server_ipaddr )
        #self.framework.observe(self.on.config_changed, self._on_config_changed)
        #self.framework.observe(self.on.fortune_action, self._on_fortune_action)
        #self._stored.set_default(things=[])

    '''
    def _on_config_changed(self, _):
        current = self.config["thing"]
        if current not in self._stored.things:
            logger.debug("found a new thing: %r", current)
            self._stored.things.append(current)
    '''

    def _on_install(self, _):
        self.unit.status = MaintenanceStatus("Installing dependencies")
        subprocess.run(["apt", "update"])
        subprocess.run(["apt", "install", "-y", "git", "python3-pip"])#, "openssh-server"])
        self.unit.status = MaintenanceStatus("Installing ML app")
        repoPath="https://github.com/daviddvs/ml_nfv_ec.git"
        wd=os.path.expanduser('~')+"/ml_nfv_ec"
        subprocess.run(["git", "clone", repoPath, wd])
        wd=wd+"/mon"
        subprocess.run(["git", "checkout", "devel"], cwd=wd)
        subprocess.run(["pip3", "install", "-r", "requirements.txt"], cwd=wd)
        self.unit.status = ActiveStatus("ML app installed")

    def _on_start(self, _):
        self.unit.status = MaintenanceStatus("Starting ML app")
        wd=os.path.expanduser('~')+"/ml_nfv_ec/mon"
        subprocess.Popen(["python3", "server.py"], cwd=wd)
        time.sleep(2) # wait until runs
        self.unit.status = ActiveStatus("ML app started")

    def get_server_ipaddr(self, event):
        self.unit.status = MaintenanceStatus("Reading Server IP")
        ip = event.relation.data[event.unit].get("ip")
        wd=os.path.expanduser('~')+"/ml_nfv_ec/mon"
        if(ip != None):
            subprocess.run(["python3", "mon2.py", "--add", str(ip)+",root,root"], cwd=wd)
            self.unit.status = ActiveStatus(f"Added server {ip}")

if __name__ == "__main__":
    main(MonitorCharm)
