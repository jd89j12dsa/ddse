script_path=$(cd "$(dirname "$0")" && pwd)

mkdir result

$script_path/AuraServer &
$script_path/AuraClient $script_path/dataset/Enron_USENIX 0 0 > $script_path/result/Enron_USENIX
pkill AuraServer



