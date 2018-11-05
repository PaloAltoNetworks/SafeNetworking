# SafeNetworking

[![GitHub release](https://img.shields.io/github/release/PaloAltoNetworks/safe-networking.svg?style=for-the-badge)](https://github.com/PaloAltoNetworks/safe-networking/releases)
[![GitHub repo size in bytes](https://img.shields.io/github/repo-size/badges/shields.svg?style=for-the-badge)](https://github.com/PaloAltoNetworks/safe-networking)

SafeNetworking is a software application that recevies both THREAT and TRAFFIC syslogs events from Palo Alto Networks NGFWs.  Using the Palo Alto Networks Threat Intelligence Cloud, SafeNetworking is able to correlate some of the threat logs (DNS queires mainly) with malware known to be associated with the event in question.  SafeNetworking utilizes ElasticStack's open-source version to gather, store and visualize these enriched events.

Before using SafeNetworking, please read and understand our [Support Policy](https://github.com/PaloAltoNetworks/safe-networking/wiki/Support-Policy)<br/>
For a more detailed introduction to SafeNetworking, see [What is SafeNetworking?](https://github.com/PaloAltoNetworks/safe-networking/wiki/What-is-SafeNetworking%3F)<br/>
For the latest information and release specific notes view the [release notes](docs/release-notes.md)

If you want to use SafeNetworking (not develop against it) it is suggested to get the pre-installed VM that can be obtained from your Palo Alto Networks account team and can be used for a proof-of-concept of SafeNetworking and comes pre-installed and ready to go.  

If you are looking to install a dev copy and develop against the code or do not have an account team, please take a look at instructions in the [wiki](https://github.com/PaloAltoNetworks/safe-networking/wiki) on how to install and run.  



## Support Policy
The code and templates in the repo are released under an as-is, best effort, support policy. These scripts should be seen as community supported and Palo Alto Networks will contribute our expertise as and when possible. We do not provide technical support or help in using or troubleshooting the components of the project through our normal support options such as Palo Alto Networks support teams, or ASC (Authorized Support Centers) partners and backline support options. The underlying product used (the VM-Series firewall) by the scripts or templates are still supported, but the support is only for the product functionality and not for help in deploying or using the template or script itself. Unless explicitly tagged, all projects or work posted in our GitHub repository (at https://github.com/PaloAltoNetworks) or sites other than our official Downloads page on https://support.paloaltonetworks.com are provided under the best effort policy.
