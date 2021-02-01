# OSM packages for ML app

## OSM steps to deploy VNF/NS
1. Create VIM
```
osm vim-create --name Openstack --user <user> --password <password> --auth_url <vim_url> --tenant <tenant> --account_type openstack
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
```

5. Debug
```
osm ns-list
juju switch <ns-id>
watch -c juju status --color
juju debug-log
juju debug-log --include <app-vnf-id> --replay
```