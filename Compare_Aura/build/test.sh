mkdir ./Result/

sleep 10s
./AuraServer &
./AuraClient Crime_USENIXDB Crime_USENIXSearch Crime_USENIXREV> ./Result/Crime_USENIXDB00
pkill AuraServer
