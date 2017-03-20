# collectd-python-shower
shower is a plugin for collectd that parses "show" commands from switches and routers devices and retrieves metrics.

## That is a strange name
You should pronounce it as show-er. You know, because it works with show commands, get it? :)

## Requirements

* [collectd](http://collectd.org/) with Python support
* [Netmiko](https://github.com/ktbyers/netmiko)
* [TextFSM](https://github.com/google/textfsm) (optional)

On CentOS 7 with EPEL repository enabled you can run the following:

```
yum install collectd-python
pip install netmiko textfsm
```

## Installation

Clone this repository into a folder of your choice. The following example will place the plugin into `/opt/collectd-python-shower`.

```
cd /opt
git clone https://github.com/ArnesSI/collectd-python-shower.git
```

## Configuration

```Apache
<LoadPlugin python>
    Globals true
</LoadPlugin>

<Plugin "python">
    ModulePath "/opt/collectd-python-shower"
    Import "shower"

    <Module "shower">
        Verbose false
        Workers 10
        Username "admin"
        Password "password"
        TemplatePath  "/opt/ntc-templates/templates"
        <Data "cisco_ios_cpu_multicore">
            Style "regex"
            Table True
            PluginInstance "cpu"
            TypeInstance "core"
            Types "cpu_5sec" "cpu_1min" "cpu_5min"
            Command "show processes cpu | include utilization"
            Regex "Core (?P<core>\\d+):.+:\\s?(?P<cpu_5sec>\\d+)%.+:\\s?(?P<cpu_1min>\\d+)%.+:\\s?(?P<cpu_5min>\\d+)%"
        </Data>
        <Host "myrouter">
            Type "cisco_ios"
            Address "myrouter.example.com"
            Collect "cisco_ios_cpu_multicore"
        </Host>
    </Module>
</Plugin>
```

Make sure you have Python support enabled in collectd:

```Apache
<LoadPlugin python>
    Globals true
</LoadPlugin>
```

Tell collectd where to find shower plugin and to load it:

```Apache
<Plugin "python">
    ModulePath "/opt/collectd-python-shower"
    Import "shower"
</Plugin>
```

You can have multiple [ModulePath](https://collectd.org/documentation/manpages/collectd-python.5.shtml#configuration) lines if you use other Python plugins.

All configuration for the plugin goes into the `<Module "shower">` section.

The way you configure shower is similar to collectd's [SNMP plugin](https://collectd.org/documentation/manpages/collectd-snmp.5.shtml). You define one or more Data sections. These define the show commands to be run and how to parse the output. Then you define `Host` blocks for your devices and associate `Data` blocks to hosts with `Collect` statements.

Shower global configuration options:

### Verbose *true|false*

Send info and debug level logs from shower to collectd.

### Workers *Num*

How many parallel threads should collectd use for reading data from hosts. This value should probably be lower than `ReadThreads` setting in global [collectd configuration](https://collectd.org/documentation/manpages/collectd.conf.5.shtml).

Internally shower will split hosts equally across all workers. Each worker must complete parsing all its hosts within `Interval` seconds. Otherwise collectd will complain in its log file:

```
[2017-03-13 10:46:23] [warning] plugin_read_thread: read-function of the `python.shower_6' plugin took 12.256 seconds, which is above
 its read interval (10.000 seconds). You might want to adjust the `Interval' or `ReadThreads' settings.
 ```

In such cases you'll want to increase the `Interval` or `Workers`.

### Interval *Seconds*

How often to poll hosts. Can be overridden under `Host` blocks.

### TemplatePath *Directory*

Directory where templates defined in `Data` blocks can be found. You can include multiple `TemplatePath` lines. Shower will load the template found in the last defined `TemplatePath` directory.

### Username *Username*

Global username to login to hosts with. Can be overridden under `Host` blocks.

### Password *Password*

Global password to login to hosts with. Can be overridden under `Host` blocks.

### <Data *Name*> *block*

Defines a command to be run and how to parse metrics. Name is the name to be used in `Collect` setting under `Host` blocks.

The following settings are valid under `Data` blocks:

#### Style *regex|textfsm*

What method of parsing to use. regex style specifies all needed parameters in configuration file. textfsm needs an accompanying TextFSM template.

#### PluginInstance *Name*

Collectd PluginInstance for this `Data` block. See [Metric Naming](#metric-naming) for an explanation.

#### Table *true|false*

Define if this is a single list of values or a table of values.

When Table is set to false only a single instance of fields defined will be extracted. For example 5 second, 1 minute and 5 minute CPU utilization of a router with a single one-core CPU.

When Table is set to true you also need to set TypeInstance to a name of the field whose values will be used as a collectd's TypeInstance. This is useful if you want to extract some counters for each interface on a switch for example.

#### TypeInstance *Field*

Which field to use for collectd's TypeInstance. See `Table` above for a detailed explanation.

#### Types *Field* [*Field*]

The names of fields to extract as collectd's Types.

If using textfsm Style you can leave out this parameter and all fields defined in TextFSM template will be extracted.

If using regex Style you must specify fields here.

#### TemplatePath *Directory*

Directory where template defined in this `Data` blocks can be found. Appends to the list of `TemplatePath`s defined under `Module` block.

Only applies if using textfsm Style.

#### Template *File*

The name of TextFSM template to use for parsing. Must exist in one of defined `TemplatePath`s. Or you can specify an absolute full path to template file.

Only applies if using textfsm Style.

#### Command *Command*

Command to run on host.

#### TypeOverride *Type*

If you're only extracting one instance of values and don't want to define a custom collectd type for each value, you can set this option to some type that is defined in collectd. All fields that will be extracted will be set as TypeInstances.

Only applies if using textfsm Style.

#### Regex *Regex*

Regular expression to apply to output. If `Table` is true each line of command output is compared to regex separately. If `Table` is false the regex is applied to the entire output at once.

Use named capturing groups. The names will correspond to `Types` that will be extracted.

Only applies if using regex Style.

#### Formatter *Field* *FormatFunction*

You can apply a function to transform parsed values before they are sent to collectd. This is useful if your extracted fields are not exact numbers but possibly contain some string.

If for example you extracted 12.4k you can apply multiplier2int formatter to change it to 12400.

You can specify multiple `Formatter` lines - one for each field to format.

See [Value formatting](#formatting) to learn how to make your own formating function.

#### Verbose *true|false*

Send info and debug level logs from shower to collectd.

#### Debug *true|false*

Print even more output than `Verbose`.

### <Host *Name*> *block*

Defines a host to poll metrics from. Name is the host name as presented to collectd.

The following settings are valid under `Host` blocks:

#### HostType *netmiko_type*

The type of host as [defined](https://github.com/ktbyers/netmiko/blob/master/netmiko/ssh_dispatcher.py) by Netmiko.

#### Address *Hostname or IP*

IP address or hostname to connect to. Defaults to the name of the `Host` block.

#### Username

Username to login to this host with. Overrides global `Username` setting.

#### Password

Password to login to this host with. Overrides global `Password` setting.

#### Collect *Data name* [*Data name*]

Names of Data blocks. Which commands to run for this host.

#### Interval *Seconds*

How often to poll this hosts. It must be a multiple of the `Interval` setting under `Module` block.

#### Timeout *Seconds*

How long to wait for response from host when connection or running commands.

#### Verbose *true|false*

Send info and debug level logs from shower to collectd.

#### Debug *true|false*

Print even more output than `Verbose`. Prints command output among other things. Useful when troubleshooting or developing new parsing templates.

## A note on types.db

You will probably need to define your own types in collectd's types.db. When using regex style parsing each named capturing group maps to a collectd type. And when using textfsm style parsing each Value in textfsm maps to a collectd type.

## Examples

### Parsing with simple regular expressions

#### Get CPU utilization from Cisco IOS. Single-core CPU example.

Command: `show processes cpu | i utilization`
Sample output:
```
CPU utilization for five seconds: 15%/0%; one minute: 16%; five minutes: 15%
```

We want to parse utilization for each time window.

shower data config:
```Apache
<Data "cisco_ios_cpu_single">
    Style "regex"
    PluginInstance "cpu"
    Types "cpu_5sec" "cpu_1min" "cpu_5min"
    Command "show processes cpu | include utilization"
    Regex ":\\s?(?P<cpu_5sec>\\d+)%.+:\\s?(?P<cpu_1min>\\d+)%.+:\\s?(?P<cpu_5min>\\d+)%"
</Data>
```

collectd types.db:
```
cpu_5sec                value:GAUGE:0:100
cpu_1min                value:GAUGE:0:100
cpu_5min                value:GAUGE:0:100
```

Resulting collectd metrics:
```
<host>/shower-<PluginInstance>/<Type>

myrouter/shower-cpu/cpu_5sec
myrouter/shower-cpu/cpu_1min
myrouter/shower-cpu/cpu_5min
```

#### Get CPU utilization from Cisco IOS. Multi-core CPU example.

Command: `show processes cpu | i utilization`
Sample output:
```
Core 0: CPU utilization for five seconds: 3%; one minute: 3%; five minutes: 3%                                                       
Core 1: CPU utilization for five seconds: 1%; one minute: 3%; five minutes: 3%
```

We want to parse utilization for each time window for each core.

shower data config:
```Apache
<Data "cisco_ios_cpu_multi">
    Style "regex"
    PluginInstance "cpu"
    Types "cpu_5sec" "cpu_1min" "cpu_5min"
    Table True
    TypeInstance "core"
    Command "show processes cpu | include utilization"
    Regex "Core (?P<core>\\d+):.+:\\s?(?P<cpu_5sec>\\d+)%.+:\\s?(?P<cpu_1min>\\d+)%.+:\\s?(?P<cpu_5min>\\d+)%"
</Data>
```

collectd types.db:
```
cpu_5sec                value:GAUGE:0:100
cpu_1min                value:GAUGE:0:100
cpu_5min                value:GAUGE:0:100
```

Resulting collectd metrics:
```
<host>/shower-<PluginInstance>/<Type>-<TypeInstance>

myrouter/shower-cpu/cpu_5sec-0
myrouter/shower-cpu/cpu_5sec-1
myrouter/shower-cpu/cpu_1min-0
myrouter/shower-cpu/cpu_1min-1
myrouter/shower-cpu/cpu_5min-0
myrouter/shower-cpu/cpu_5min-1
```

### Parsing with TextFSM templates

#### Get control-plane policing statistics from Cisco IOS.

Command: `show policy-map control-plane`
Sample output:
```
 Control Plane

  Service-policy input: sample-copp-policy

    Class-map: management (match-all)  
      43164 packets
      Match: access-group name copp-class-management
      police:
          cir 1000000 bps, bc 31250 bytes
        conformed 4807238 bytes; actions:
          transmit
        exceeded 0 bytes; actions:
          drop
        conformed 1000 bps, exceeded 0000 bps

    Class-map: services (match-all)  
      10954 packets
      Match: access-group name copp-class-services
      police:
          cir 1000000 bps, bc 31250 bytes
        conformed 1073690 bytes; actions:
          transmit
        exceeded 0 bytes; actions:
          drop
        conformed 0000 bps, exceeded 0000 bps

...

    Class-map: class-default (match-any)  
      114340844 packets
      Match: any
      police:
          cir 32000 bps, bc 1500 bytes
        conformed 2642588932 bytes; actions:
          transmit
        exceeded 16419273148 bytes; actions:
          drop
        conformed 31000 bps, exceeded 476000 bps
```

We want to parse all the metrics for each class-map.

shower data config:
```Apache
<Data "cisco_ios_copp">
    Style "textfsm"
    Table true
    PluginInstance "copp"
    TypeInstance "class_map"
    Template "show_policy_map_control_plane.textfsm"
</Data>
```

TextFSM template:
```
Value class_map (\S+)
Value packets (\d+)
Value cir_bps (\d+)
Value bc_bytes (\d+)
Value conformed_bytes (\d+)
Value conformed_bps (\d+)
Value exceeded_bytes (\d+)
Value exceeded_bps (\d+)


Start
  ^\s+Class-map: ${class_map} \(.*\)
  ^\s+${packets} packets
  ^\s+Match: access-group name .*
  ^\s+police:
  ^\s+cir ${cir_bps} bps, bc ${bc_bytes} bytes
  ^\s+conformed ${conformed_bytes} bytes; actions:
  ^\s+transmit
  ^\s+exceeded ${exceeded_bytes} bytes; actions:
  ^\s+drop
  ^\s+conformed ${conformed_bps} bps, exceeded ${exceeded_bps} bps -> Record
```

collectd types.db:
```
packets                 value:DERIVE:0:U
cir_bps                 value:GAUGE:0:U
bc_bytes                value:DERIVE:0:U
conformed_bytes         value:DERIVE:0:U
conformed_bps           value:GAUGE:0:U
exceeded_bytes          value:DERIVE:0:U
exceeded_bps            value:GAUGE:0:U
```

Resulting collectd metrics:
```
<host>/shower-<PluginInstance>/<TextFSM_Value>-<TypeInstance>

myrouter/shower-copp/packets-management
myrouter/shower-copp/packets-services
myrouter/shower-copp/packets-class-default
myrouter/shower-copp/cir_bps-management
myrouter/shower-copp/cir_bps-services
myrouter/shower-copp/cir_bps-class-default
...
```

#### Get MAC address statistics from Cisco IOS.

Command: `show mac address-table count`
Sample output:
```
MAC Entries for all vlans:
Dynamic Unicast Address Count:                  9
Static Unicast Address (User-defined) Count:    0
Static Unicast Address (System-defined) Count:  6
Total Unicast MAC Addresses In Use:             15
Total Unicast MAC Addresses Available:          55000
Multicast MAC Address Count:                    8
Total Multicast MAC Addresses Available:        32768
```

We want to parse MAC address stats, but don't want to pollute collectd's types with multiple new type definitions that will only be used once.

shower data config:
```Apache
<Data "cisco_ios_mac">
    Style "textfsm"
    Table false
    PluginInstance "mac"
    TypeOverride "count"
    Template "show_mac_address-table_count.textfsm"
</Data>
```

TextFSM template:
```
Value unicast_dynamic (\d+)
Value unicast_static_user (\d+)
Value unicast_static_system (\d+)
Value unicast_used (\d+)
Value unicast_total (\d+)
Value multicast_used (\d+)
Value multicast_total (\d+)


Start
 ^MAC Entries for all vlans:.*
 ^Dynamic Unicast Address Count:\s+${unicast_dynamic}
 ^Static Unicast Address (User-defined) Count:\s+${unicast_static_user}
 ^Static Unicast Address (System-defined) Count:\s+${unicast_static_system}
 ^Total Unicast MAC Addresses In Use:\s+${unicast_used}
 ^Total Unicast MAC Addresses Available:\s+${unicast_total}
 ^Multicast MAC Address Count:\s+${multicast_used}
 ^Total Multicast MAC Addresses Available:\s+${multicast_total}
```

collectd types.db:
```
count                   value:GAUGE:0:U
```

Resulting collectd metrics:
```
<host>/shower-<PluginInstance>/<TextFSM_Value>-<TypeInstance>

myrouter/shower-mac/count-unicast_dynamic
myrouter/shower-mac/count-unicast_static_user
myrouter/shower-mac/count-unicast_static_system
myrouter/shower-mac/count-unicast_used
myrouter/shower-mac/count-unicast_total
myrouter/shower-mac/count-multicast_used
myrouter/shower-mac/count-multicast_total
...
```

Resulting collectd metrics:

### Using ntc-templates

[ntc-templates](https://github.com/networktocode/ntc-templates) are a good source of TextFSM templates and might already contain a template for the command you want to parse.

## <a name="metric-naming"></a>Metric naming

First you'll want to read collectd's ducumentation on [naming schema](https://collectd.org/wiki/index.php/Naming_schema). Shower uses the same concepts and terminology.

There is one exception - when using textfsm style parsing and you set TypeOverride. You'll want to do that then you are parsing show commend that contains only one record with a large amount of metricy (types). In this case you can set TypeOverride to one of defined types in collectd. All the Values from TextFSM template will be sent to collectd as TypeInstance rather than Types.

## <a name="formatting"></a>Value formatting

Sometimes the values in output are not pure numbers but might contain some prefixes such as 5Gbit/s or 100kbit/s. You can use Formatter configuration options to translate these values into normal numbers.

The following formatting functions are available:

### multiplier2int

Converts SI metric prefixes. 1.5k becomes 1500, 100m becomes 0.1.

### Writing your own

You'll need to write a function in `formatters.py`. The function takes the value as parsed by TextFSM template or captured by regex and must return a float.

## Contributing

Any suggestions, issues, bug reports or improvements are welcome. Use GitHub's [issue tracker](https://github.com/ArnesSI/collectd-python-shower/issues) for that.

Especially welcome are pull requests with additional templates or formatters :)
