#!/bin/bash

# update python sources
rsync -rtv --del bin/ ~/bin/

# update and activate services
cd svc
for svc in *.service
do
  sudo cp "${svc}" /lib/systemd/system
  sudo systemctl start "${svc%.service}"
  sudo systemctl enable "${svc%.service}"
done
