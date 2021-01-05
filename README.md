# Warcraft-Logs-API-Med-Perf-Avg

Queries the Warcraft Logs API to capture combat data of players who have defeated Kel'Thuzad on a given server.

This script primarily performs two outputs:
  It generates a list of players who have defeated the last boss in World of Warcraft Classic
  Allows user to filter and print the Median Performance Average of those players
  
It calls on the classic.warcraftlogs.com restful API to query data.

For larger queries, it records progress along the way in case of interruptions or API Query caps.

Example Output:

Janok
median perf avg
82.29083712073711

...

Tkipp
median perf avg
39.65972660095267
