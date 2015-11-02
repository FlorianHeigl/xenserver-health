#!/usr/bin/env python

import sys
import re
import commands

config = {}


def read_file(cfgfile):
    f = open(cfgfile)
    data = re.split(r"-?--=\[ ", f.read())

    result = {}
    for section in data[1:]:
        name_search = re.findall(r"(.*) \]=--.*", section)

        if len(name_search) == 1:
            name = name_search[0]
            result[name] = {}
            result[name]["message"] = section.splitlines()[1:-1]
            if result[name]["message"][0] == "n/a or not configured":
                result[name]["error"] = True
            else:
                result[name]["error"] = False

    return result


def print_element(f, name):
    if not config[name]:
        return

    if config[name]["error"]:
        color = "red"
    else:
        color = "green"

    line = '<p style="color:%s">%s</p>\n<pre style="margin-left: 20px"><code>%s</code></pre>\n' % (color, name, "\n".join(config[name]["message"]))
    f.write(line)


def render(output_file):

    try:
      f = open(output_file, "w")
    except IOError:
      print "Error: File does not appear to exist."
      sys.exit(1)

    f.write("<html><h1>XenServer Health Check</h1>\n")

    print_element(f, "Host alias")
    print_element(f, "XNTP Time Protocol Daemon")

    name = "Multipath Devices Basic Information"
    if not config[name]["error"]:
        if re.search(".*driver not loaded.*", config[name]["message"][0]):
            config[name]["error"] = True
    print_element(f, name)

    name = "Filesystems and Usage"
    if not config[name]["error"]:
        if is_re_in_list(r".*[8|9].%.*", config[name]["message"]):
            config[name]["error"] = True
    print_element(f, name)

    name = "Total Size of /var/log"
    if not config[name]["error"]:
        if int(config[name]["message"][0]) > 1073741824:
            config[name]["error"] = True
            config[name]["message"] = ["The /var/log directory seems too big: " + config[name]["message"][0] + " bytes > 1GB"]
        else:
            config[name]["message"] = ["The /var/log directory size is ok: " + config[name]["message"][0] + " bytes < 1GB"]
    print_element(f, name)

    print_element(f, "List of Xen Physical Interfaces")
    print_element(f, "List of Xen Hosts")
    print_element(f, "List of Xen VMs")
    print_element(f, "Volumegroups")
    print_element(f, "Bonding State")

    name = "dmesg"
    if not config[name]["error"]:
        dm = open("dmesg")
        exclude_dmesg = dm.read().splitlines()
        dm.close()
        #exclude_dmesg = ["[timestamp] usbhid: USB HID core driver", "[timestamp] usb 6-2: Product: ThinkPad USB Laser Mouse"]
        config[name]["message"] = filter_output(config[name]["message"], exclude_dmesg)
    print_element(f, name)

    f.write("</html>")
    f.close()


def get_command_output(command_to_execute):
    command_result = commands.getstatusoutput(command_to_execute)
    result = {}

    result["message"] = command_result[1].splitlines()

    if command_result[0] == 0:
        result["error"] = False
    else:
        result["error"] = True

    return result


def filter_output(output, exclude_list):
    result = []
    for line in output:
        relevant = True
        for raw_exclude in exclude_list:
            exclude = raw_exclude.split("] ", 1)
            if len(exclude) > 1:
                if line.endswith(exclude[1]):
                    relevant = False
                    break
        if relevant:
            result.append(line)
    return result


def xen_elements():
    result = {}
    result["Total Size of /var/log"] = get_command_output('du --max-depth=0 /var/log | cut -f 1')
    result["List of Xen VMs"] = get_command_output('xe vm-list')
    result["List of Xen Physical Interfaces"] = get_command_output('xe pif-list')
    result["List of Xen Networks"] = get_command_output('xe network-list')
    result["List of Xen Hosts"] = get_command_output('xe host-list')
    result["dmesg"] = get_command_output('dmesg')
    result["Bonding State"] = get_command_output('cat /proc/net/bonding/bond*')

    return result


def is_re_in_list(search_re, list):
    return bool([m for l in list for m in [re.search(search_re, l)] if m])


if __name__ == '__main__':

    if len(sys.argv) == 3:
        cfg = sys.argv[1]
        output = sys.argv[2]

        config = read_file(cfg)
        config.update(xen_elements())

        render(output)
    else:
        print("usage: " + sys.argv[0] + " cfg2html.txt output.html")
