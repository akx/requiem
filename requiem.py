from subprocess import check_call, call, Popen, PIPE
import os
import textwrap
import glob

os.putenv("DEBIAN_FRONTEND", "noninteractive")

#######
## Plumbing
#######


def get_output(cmd, **kwargs):
    kwargs["stdout"] = PIPE
    p = Popen(cmd, **kwargs)
    stdout, stderr = p.communicate()
    if p.returncode:
        raise ValueError("%r return code %s" % (cmd, p.returncode))
    return stdout


def sh(cmd):
    check_call(cmd, shell=True)


def shh(cmd):
    get_output(cmd, shell=True)


#######
## Packages
#######


def add_apt_key(url):
    sh("wget -O - %s | apt-key add -" % url)


def add_apt_repo(name, spec):
    with file("/etc/apt/sources.list.d/%s.list" % name, "wb") as outf:
        outf.write("deb %s\n" % spec)
    sh("apt-get update")


def install(*packages):
    sh("apt-get install -y --no-install-recommends %s" % " ".join(packages))


def get_packages():
    return set(
        l.split()[0]
        for l in get_output("dpkg --get-selections", shell=True).splitlines()
        if l
    )


def has_package(*check_packages):
    all_packages = get_packages()
    return (set(check_packages) <= all_packages)


def setup_apt_cacher_ng(apt_cacher_ng_url):
    proxy_config_file = "/etc/apt/apt.conf.d/90proxy"
    proxy_url = apt_cacher_ng_url.rstrip("/")

    if proxy_url in read(proxy_config_file):
        print "Apt proxy already configured"
        return
    
    try:
        import urllib
        data = urllib.urlopen(apt_cacher_ng_url).read()
    except:
        print "Could not acquire apt proxy settings"
        return

    if "APT Reconfiguration required" in data:  # Looks like a valid apt-cacher-ng page
        write(proxy_config_file, """Acquire::http { Proxy "%s"; };""" % proxy_url)
        print "Apt proxy activated"
    else:
        print "Not a proper apt proxy"

#######
## File damagement
#######


def has_file(path):
    return os.path.exists(path)


def nuke(*specs):
    for spec in specs:
        for filename in glob.glob(spec):
            if os.path.isfile(filename):
                print "nuking: %s" % filename
                os.unlink(filename)


def write(filename, content):
    with file(filename, "wb") as out_f:
        out_f.write(textwrap.dedent(content.strip("\n\r")))

def read(filename):
    if os.path.isfile(filename):
        with file(filename, "rb") as in_f:
            return in_f.read()
    return ""

#######
## Services
#######


def restart(service):
    sh("service %s restart" % service)


#######
## Macros
#######


def configure_etckeeper():
    if not has_package("etckeeper"):
        install("etckeeper", "git-core")
        write("/etc/etckeeper/etckeeper.conf", """
        VCS="git"
        GIT_COMMIT_OPTIONS=""
        HIGHLEVEL_PACKAGE_MANAGER=apt
        LOWLEVEL_PACKAGE_MANAGER=dpkg
        """)
        sh("etckeeper init")
        sh("etckeeper commit initial")
        print "etckeeper provisioned"
