$HostAlias = "discord_vps"
$RemoteDB = "bot/achievebot.db"
$RemoteBackup = "bot/achievebot_backup.db"

$Date = Get-Date -Format "yyyy-MM-dd"
$LocalFile = ".\backup_$Date.db"

ssh $HostAlias "sqlite3 $RemoteDB '.backup $RemoteBackup'"
scp "${HostAlias}:$RemoteBackup" $LocalFile
ssh $HostAlias "rm $RemoteBackup"
