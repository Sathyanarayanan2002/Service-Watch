# ServiceWatch - Linux Troubleshooting Runbook

## 1. Container is not running
docker ps -a
docker start servicewatch-app

## 2. Application port 5000 is unavailable
ss -tulnp | grep 5000
docker port servicewatch-app

## 3. Application errors
docker logs --tail 50 servicewatch-app
docker logs servicewatch-app 2>&1 | grep -i error

## 4. MySQL connection failure
systemctl status mysql
ss -tulnp | grep 3306

## 5. Network or DNS failure
ping -c 4 example.com
curl -I https://www.python.org/
nslookup www.python.org
