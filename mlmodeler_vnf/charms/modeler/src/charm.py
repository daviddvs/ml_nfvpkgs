#!/usr/bin/env python3
# Copyright 2020 davidf
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


class ModelerCharm(CharmBase):
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

    def _on_fortune_action(self, event):
        fail = event.params["fail"]
        if fail:
            event.fail(fail)
        else:
            event.set_results({"fortune": "A bug in the code is worth two in the documentation."})
    '''

    def _on_install(self, _):
        self.unit.status = MaintenanceStatus("Installing dependencies")
        subprocess.run(["apt", "update"])
        subprocess.run(["apt", "install", "-y", "git", "python3-pip", "sysstat"])#, "openssh-server"])
        self.unit.status = MaintenanceStatus("Installing ML app")
        repoPath="https://github.com/daviddvs/ml_nfv_ec.git"
        wd=os.path.expanduser('~')+"/ml_nfv_ec"
        subprocess.run(["git", "clone", repoPath, wd])
        wd=wd+"/backend"
        subprocess.run(["git", "checkout", "devel"], cwd=wd)
        subprocess.run(["pip3", "install", "-r", "requirements.txt"], cwd=wd)
        self.unit.status = ActiveStatus("ML app installed")

    def _on_start(self, _):
        self.unit.status = MaintenanceStatus("Starting ML app")
        wd=os.path.expanduser('~')+"/ml_nfv_ec/backend"
        subprocess.Popen(["python3", "model.py", "--classifier", "--regressor", "--clustering", "-i", "5"], cwd=wd)
        time.sleep(2) # wait until runs
        self.unit.status = ActiveStatus("ML app started")

    def get_server_ipaddr(self, event):
        self.unit.status = MaintenanceStatus("Reading Server IP")
        ip = event.relation.data[event.unit].get("ip")
        wd=os.path.expanduser('~')+"/ml_nfv_ec/backend"
        if(ip != None):
            subprocess.run(["python3", "model.py", "--addhost", str(ip)+",root,root"], cwd=wd)
            self.unit.status = ActiveStatus(f"Added server {ip}")

if __name__ == "__main__":
    main(ModelerCharm)
