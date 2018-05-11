### This is the development branch of SafeNetworking 3.0.  It is suggested that you use the [latest release](https://github.com/PaloAltoNetworks/safe-networking/releases) unless you know what you are doing with this development release
[![GitHub release](https://img.shields.io/github/release/PaloAltoNetworks/safe-networking.svg?style=for-the-badge)](https://github.com/PaloAltoNetworks/safe-networking/releases)
[![GitHub repo size in bytes](https://img.shields.io/github/repo-size/badges/shields.svg?style=for-the-badge)](https://github.com/PaloAltoNetworks/safe-networking)

SafeNetworking is a software application that recevies events (DNS queries to known, malicious domains) from Palo Alto Networks NGFWs.  Using the Palo Alto Networks Threat Intelligence Cloud, SafeNetworking is able to correlate these DNS queries with malware known to be associated with the domain in question.  SafeNetworking utilizes ElasticStack's open-source version to gather, store and visualize these enriched events.

For a more detailed introduction to SafeNetworking, see [What is SafeNetworking?](https://github.com/PaloAltoNetworks/safe-networking/wiki/What-is-SafeNetworking%3F)<br/>
For the latest information and release specific notes view the [release notes](docs/release-notes.md)

#### NOTE: If you already have an ElasticStack cluster (i.e. ElasticCloud or a local install) skip to step 2
1.) [Infrastructure Setup Instructions](https://github.com/PaloAltoNetworks/safe-networking/wiki/Infrastructure-Setup)

2.) [Install SafeNetworking](https://github.com/PaloAltoNetworks/safe-networking/wiki/Installing-the-SafeNetworking-Software)

3.) [Configure SafeNetworking for your installation](https://github.com/PaloAltoNetworks/safe-networking/wiki/Configuring-SafeNetworking)

4.) [NGFW Configuration](https://github.com/PaloAltoNetworks/safe-networking/wiki/Home#config-ngfw)

5.) [Running SafeNetworking](https://github.com/PaloAltoNetworks/safe-networking/wiki/Running-SafeNetworking)

<br/>

## Post install
SafeNetworking should now be running and processing events.  You will need to perfrom some minor post install setup in Kibana for the visualizations and dashboards.
[Kibana setup for SafeNetworking](https://github.com/PaloAltoNetworks/safe-networking/wiki/Kibana-post-install-setup)

<br/>

## Best Practices and Optional Configuration
You should be all set.  For even more ideas on what you can do with the system and other things that you can download and install to get the most out of SafeNetworking, checkout the [Wiki](https://github.com/PaloAltoNetworks/safe-networking/wiki)!!

# Support Policy
The code and templates in the repo are released under an as-is, best effort, support policy. These scripts should be seen as community supported and Palo Alto Networks will contribute our expertise as and when possible. We do not provide technical support or help in using or troubleshooting the components of the project through our normal support options such as Palo Alto Networks support teams, or ASC (Authorized Support Centers) partners and backline support options. The underlying product used (the VM-Series firewall) by the scripts or templates are still supported, but the support is only for the product functionality and not for help in deploying or using the template or script itself. Unless explicitly tagged, all projects or work posted in our GitHub repository (at https://github.com/PaloAltoNetworks) or sites other than our official Downloads page on https://support.paloaltonetworks.com are provided under the best effort policy.
