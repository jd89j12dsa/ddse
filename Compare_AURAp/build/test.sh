script_path=$(cd "$(dirname "$0")" && pwd)

mkdir result

$script_path/AuraServer &
$script_path/AuraClient $script_path/dataset/Crime_USENIX_REV 0 0 > $script_path/result/Crime_USENIX_REV
pkill AuraServer



