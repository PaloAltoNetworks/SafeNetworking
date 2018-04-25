### This is the development branch of SafeNetworking 3.0.  It is suggested that you use the [latest release](https://github.com/PaloAltoNetworks/safe-networking-sp/releases) unless you know what you are doing with this development release
![GitHub release](https://img.shields.io/github/release/qubyte/rubidium.svg?style=for-the-badge)
![GitHub repo size in bytes](https://img.shields.io/github/repo-size/badges/shields.svg?style=for-the-badge)

SafeNetworking is a software application that recevies events (DNS queries to known, malicious domains) from Palo Alto Networks NGFWs.  Using the Palo Alto Networks Threat Intelligence Cloud, SafeNetworking is able to correlate these DNS queries with malware known to be associated with the domain in question.  SafeNetworking utilizes ElasticStack's open-source version to gather, store and visualize these enriched events.

For a more detailed introduction to SafeNetworking, see [What is SafeNetworking?](https://github.com/PaloAltoNetworks/safe-networking-sp/wiki/What-is-SafeNetworking%3F)<br/>
For the latest information and release specific notes view the [release notes](docs/release-notes.md)

#### NOTE: If you already have an ElasticStack cluster (i.e. ElasticCloud or a local install) skip to step 2
1.) [Infrastructure Setup Instructions](https://github.com/PaloAltoNetworks/safe-networking-sp/wiki/Infrastructure-Setup)

2.) [Install SafeNetworking](https://github.com/PaloAltoNetworks/safe-networking-sp/wiki/Installing-the-SafeNetworking-Software)

3.) [Configure SafeNetworking for your installation](https://github.com/PaloAltoNetworks/safe-networking-sp/wiki/Configuring-SafeNetworking)

4.) [NGFW Configuration](https://github.com/PaloAltoNetworks/safe-networking-sp/wiki/NGFW-Configuration)

5.) [Running SafeNetworking](https://github.com/PaloAltoNetworks/safe-networking-sp/wiki/Running-SafeNetworking)

<br/>

## Post install
SafeNetworking should now be running and processing events.  You will need to perfrom some minor post install setup in Kibana for the visualizations and dashboards.
[Kibana setup for SafeNetworking](https://github.com/PaloAltoNetworks/safe-networking-sp/wiki/Kibana-post-install-setup)

<br/>

## Best Practices and Optional Configuration
You should be all set.  For even more ideas on what you can do with the system and other things that you can download and install to get the most out of SafeNetworking, checkout the [Wiki](https://github.com/PaloAltoNetworks/safe-networking-sp/wiki)!!
