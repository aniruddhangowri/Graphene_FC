mkdir ./controlserver/log 2>/dev/null
[ -a ./controlserver/log/logview.txt ] || (> ./controlserver/log/logview.txt; ln -s ./controlserver/log/logview.txt ./controlserver/logview.txt)

xterm -e "cd $PWD/controlserver; python ./controlserver.py" &
sleep 10
xterm -e "cd $PWD/httpserver; python ./httpserver.py" &
