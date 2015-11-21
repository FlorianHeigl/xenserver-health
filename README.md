# xenserver-health

Healthcheck and Reporting Script for Citrix XenServer and Xen Cloud Platform
Generates a html file for easy viewing.

The script will fetch info to detect / warn you of common issues in XenServer.


Features:

* dmesg filtering: Any "common" messages from dmesg are stripped away, the report will show you mostly uncommon messages.
* checks filesystem usage and free space of /var against logfile bloat
* multipathing info
* storage layout
* extensible at will :)



Usage:

```
chmod 700 cfg2html-linux xenserver-health.py
./xenserver-health.py ${HOSTNAME}.txt health-${HOSTNAME}.html
```



cfg2html is used for standardized info.
Finally it's no longer in a locked down Yahoo! group :)

Documentation for cfg2html, along with potential updates can be found at:

https://github.com/cfg2html/cfg2html
