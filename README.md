# OSM packages for ML app

## OSM steps to deploy VNF/NS
1. Create VIM
```
osm vim-create --name Openstack --user <user> --password <password> --auth_url <vim_url> --tenant <tenant> --account_type openstack
# Examples:
osm vim-create --name Openstack --user david_franco --password i2tDavidEHU --auth_url http://10.98.1.100:35357/v3/ --tenant david_franco --account_type openstack
osm vim-create --name openstack-cfaa-sn4i --auth_url http://cfaa-controller:5000/v3/ --tenant SN4I --user "admin" --account_type openstack --description "OpenStack CFAA SN4I" # password is asked
osm vim-create --name openstack-eib-sn4i --auth_url http://supermicro-1:35357/v3/ --tenant SN4I --user "admin-SN4I" --account_type openstack --description "OpenStack EIB SN4I" --config '{"user_domain_name": "SN4I", "project_domain_name": "SN4I"}' # password is asked
```

2. Create VNFD/NSD packages and edit default layouts
```
osm package-create vnf mlpredictor
osm package-create ns mlapp
```

3. Onboard VNF/NS (must be repeated every time the VNFD/NSD code is modified)
```
osm nfpkg-create mlpredictor_vnf/
osm nfpkg-create mlmodeler_vnf/
osm nfpkg-create mlbalancer_vnf/
osm nfpkg-create mlmonitor_vnf/
osm nspkg-create mlapp_ns/
```

4. Instantiate NS
```
osm ns-create --ns_name mlapp --nsd_name mlapp_nsd --vim_account Openstack
# Examples:
osm ns-create --ns_name mlapp_cfaa --nsd_name mlapp_nsd --vim_account openstack-cfaa-sn4i
osm ns-create --ns_name mlapp_eib --nsd_name mlapp_nsd --vim_account openstack-eib-sn4i
osm ns-create --ns_name mlapp_eib_cfaa --nsd_name mlapp_nsd --vim_account openstack-eib-sn4i --config ' { vnf: [ {member-vnf-index: "1", vim_account: openstack-eib-sn4i}, {member-vnf-index: "2", vim_account: openstack-cfaa-sn4i}, {member-vnf-index: "3", vim_account: openstack-eib-sn4i}, {member-vnf-index: "4", vim_account: openstack-cfaa-sn4i} ] }, wim_account: false'
```

5. Debug
```
osm ns-list
juju switch <ns-id>
watch -c juju status --color
juju debug-log
juju debug-log --include <app-vnf-id> --replay
```