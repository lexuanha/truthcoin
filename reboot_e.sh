#!/bin/bash

# Ghi log trước khi khởi động lại (tuỳ chọn)
echo "Khởi động lại lúc $(date)" >> reboot.log

# Khởi động lại hệ thống
/sbin/reboot
