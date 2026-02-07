#!/bin/bash

sleep 30  # Đợi 1 phút sau khi khởi động
cd ../main
byobu new-session -d -s trump_session 'python3 main.py'
