RO=`docker container ls | grep 'k8s_ro_ro' | cut -c 1-4`
docker exec ${RO} /bin/sh -c "apt update"
docker exec ${RO} /bin/sh -c "apt install sudo"
docker exec ${RO} /bin/sh -c "echo '10.98.1.100 supermicro-1' | sudo tee -a /etc/hosts"
docker exec ${RO} /bin/sh -c "echo '10.98.0.50 cfaa-controller' | sudo tee -a /etc/hosts"
