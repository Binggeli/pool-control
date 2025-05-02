#!/bin/bash

# update python sources
rsync -rtv --del bin/ ~/bin/

# update and activate services
cd svc
for svc in *.service
do
  cp "${svc}" /lib/systemd/system
  svc="${svc%.service}"
  systemctl start "${svc}"
  systemctl enable "${svc}"
done
