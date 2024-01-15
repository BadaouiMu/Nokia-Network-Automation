# Nokia-Network-Automation
This repository contains four scripts designed to automate Nokia network tasks, along with a comprehensive report detailing the installation and configuration of Zabbix for monitoring Nokia equipment.

## Important Note: 
The provided codes rely on an internal Nokia library called SATS (confidential). However, I utilize this library solely for router connectivity and command execution. You can easily adapt the code to Python using the Paramiko library for SSH connections and command execution. Feel free to ask ChatGPT for assistance. The "Result Presentation" section includes a PDF presentation explaining the codes and their outcomes.

## Network Inventory HW
This script enables Nokia network inventory creation by SSHing into each router, executing specific commands, and parsing the results into an Excel file. An example of the output can be found in "Codes/Network Inventory HW/Example."

## NE SW upgrade assesment
This crucial script compares our hardware with the supportable hardwares in the release note PDF, determining whether an upgrade is feasible. It automatically parses the PDF, extracting the essential table using the Camelot library (be mindful of the Python version).

While the release note is confidential, I've deleted it, but you can understand the logic and apply it to your project. 

The code provides two options: either provide a router for inventory and comparison, or supply an Excel file for comparison. An example of the result is available in "Codes/Network Inventory HW/Example."

## IGP Topology Discovery
This script, designed for LANs, takes a list of routers and returns the topology using IGP, focusing on OSPF and IS-IS. The result is a graph, with additional information accessible by clicking on the nodes.

## BGP Topology Discovery
Similar to the LAN version, this script takes a list of routers in a WAN and returns the topology using BGP. The result is a graph, and further details can be viewed by clicking on the nodes.

## Network Performance Monitoring 
This section provides two PDF files, one in English and one in French, guiding you through the installation and configuration of Zabbix for monitoring Nokia equipment. These comprehensive guides offer step-by-step instructions to ensure effective network performance monitoring.
















