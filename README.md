Requiem
=======

Silliest Debian/Ubuntu provisioning toolkit (for Vagrant and such)

Example
-------

```
#!/bin/sh
wget https://github.com/akx/requiem/raw/master/requiem.py
python - <<<EOF
import requiem as R

if not R.has_package("nginx"):
	R.add_apt_key("http://nginx.org/keys/nginx_signing.key")
	R.add_apt_repo("nginx", "http://nginx.org/packages/ubuntu/ precise nginx")
	R.install("nginx")

EOF
```