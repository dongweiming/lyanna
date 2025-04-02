#!/bin/bash

sudo cp /var/lib/redis/dump.rdb ~/lyanna
sudo chown ubuntu:ubuntu ~/lyanna/dump.rdb

mysqldump -u root lyanna > /home/ubuntu/lyanna/db_backup.sql
