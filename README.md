# StatusPage.io_monitor
a services monitoring system that updates Checks on StatusPage.io
StatusPage.io depends on [my own GitHub "infra_monitor" repository](https://github.com/Fclem/infra_monitor)
This use the default scheme to update remote Checks upon status change.

## How to start :
bash :
```bash
git clone https://github.com/Fclem/StatusPage.io_monitor.git && cd StatusCake_monitor && git clone https://github.com/Fclem/infra_monitor.git
vim config.ini
./__init__.py
```

fish :
```shell
git clone https://github.com/Fclem/StatusPage.io_monitor.git; and cd StatusCake_monitor; and git clone https://github.com/Fclem/infra_monitor.git
vim config.ini
./__init__.py
```

Checks are loaded from `config.ini`, and once `api_key`, `page_id` and `api_base` are filled in this configuration file, you can generate a list of checks using  
```python
StatusPageIoInterface().write_config()
```

## Currently supported checks types :
 * `url` : if HTTP GET to *url* returns HTTP 200
 * `tcp` : if connection to TCP *host port* is successful
 * `ping` : if remote *host* replies to ICMP ping (through system's ping command)

## To be supported checks types :
 * `docker` : if a named docker container is running
