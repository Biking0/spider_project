@echo off
start cmd /k "cd ../mitm && mitmdump --mode upstream:https://127.0.0.1:1080 --no-http2 -s addons.py"

@echo off
start cmd /k python wn_man.py hyn-test 1 1

