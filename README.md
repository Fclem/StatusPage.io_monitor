# StatusCake_monitor
a generic services monitoring system that updates StatusCake.com
StatusCake PUSH test manually "forked" from [my own GitHub "infra_monitor" repository](https://github.com/Fclem/infra_monitor)
This is basically the same as infra_monitor, except that it uses  StatusCake.com instead of StatusPage.io and it uses a PUSH scheme to update test (as a heartbeat) instead of updating check on a status change basis.

## How to start :
bash :
```bash
git clone https://github.com/Fclem/StatusCake_monitor.git && cd StatusCake_monitor && git clone https://github.com/Fclem/infra_monitor.git
vim config.ini
./__init__.py
```

fish :
```shell
git clone https://github.com/Fclem/StatusCake_monitor.git; and cd StatusCake_monitor; and git clone https://github.com/Fclem/infra_monitor.git
vim config.ini
./__init__.py
```

***Old documentation bellow***

Checks are loaded from `config.ini`, and once `api_key`, `page_id` and
`api_base` are filled in this configuration file, you can generate a
list of checks using
```python
StatusPageIoInterface().write_config()
```

## Currently supported checks types :
 * `url` : if HTTP GET to *url* returns HTTP 200
 * `tcp` : if connection to TCP *host port* is successful
 * `ping` : if remote *host* replies to ICMP ping (through system's ping command)

## To be supported checks types :
 * `docker` : if a named docker container is running
