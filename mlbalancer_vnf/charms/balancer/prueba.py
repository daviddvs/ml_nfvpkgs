import subprocess
cmd='echo "listen mlappbalance" >> /etc/haproxy/haproxy.cfg'
subprocess.run(cmd, shell=True)
