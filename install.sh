#!/bin/bash

for svc in *.service
do
  cp "${svc}" /lib/systemd/system
  svc="${svc%.service}"
  systemctl start "${svc}"
  systemctl enable "${svc}"
done

