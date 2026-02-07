#!/bin/bash

cd ../main || exit

# Kiểm tra xem phiên byobu có tên 'trump_session' đang chạy chưa
if ! byobu has-session -t trump_session 2>/dev/null; then
    echo "Không có trump_session — chạy lại lúc $(date)" >> log.txt
    ./start_main.sh
fi
