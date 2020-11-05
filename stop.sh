#!/bin/bash
app_pid=$(ps aux | grep -v grep  | grep -i app.py | awk '{print $2}')
rpc_server_pid=$(ps aux | grep -v grep  | grep -i rpcServer.py | awk '{print $2}')
DHP_WSParamsMiddleWare_pid=$(ps aux | grep -v grep  | grep -i DHP_WSParamsMiddleWare.py | awk '{print $2}')

echo ${app_pid}
echo ${rpc_server_pid}
echo ${DHP_WSParamsMiddleWare_pid}

echo priv123 | sudo -S kill -9 ${app_pid}
echo priv123 | sudo -S kill -9 ${rpc_server_pid}
echo priv123 | sudo -S kill -9 ${DHP_WSParamsMiddleWare_pid}