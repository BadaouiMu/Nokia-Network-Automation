*** Settings ***
Resource              sats.robot
Library               Temp_Lib/Lib.py

*** Variables ***            
${discovery}     False
${hosts}         hosts.txt
${max_AS}        0

${ssh_jump}      True
${jumphost}      x.x.x.x
${jumpuser}      root
${jumppass}      Stage2023    

${Test_bol}      False

*** Test Cases ***
Test 
    ${hostnames}   read_text  ${hosts}
    FOR  ${ip}  IN  @{hostnames}
        ${host}           Get From List
        ...                   ${ip}  
        ...                   0
        ${user}           Get From List
        ...                   ${ip}  
        ...                   1
        ${pass}           Get From List
        ...                   ${ip}  
        ...                   2

        Run Keyword If    ${ssh_jump}    SSH Jump True   ${host}   ${user}   ${pass}   ${jumphost}  ${jumpuser}  ${jumppass}
        Run Keyword If    '${ssh_jump}'== 'False'     SSH Jump False     ${host}   ${user}   ${pass}

    END

    Run Keyword IF       ${discovery}     bgp_topology_discovery

    

    Log To Console       \n Done

*** Keywords ***
SSH Jump True
    [Arguments]   ${host}   ${user}   ${pass}   ${jumphost}  ${jumpuser}  ${jumppass}
    ${Test_bol}              test_ssh_jump    ${host}   ${user}   ${pass}   ${jumphost}  ${jumpuser}  ${jumppass}
    Run Keyword If    ${Test_bol}    SSH True   ${host}    ${user}    ${pass}
    Run Keyword If    '${Test_bol}'== 'False'     SSH False     ${host}

SSH Jump False
    [Arguments]    ${host}   ${user}   ${pass}
    ${Test_bol}              test_ssh     ${host}   ${user}   ${pass} 
    Run Keyword If    ${Test_bol}    SSH True   ${host}    ${user}    ${pass}
    Run Keyword If    '${Test_bol}'== 'False'     SSH False     ${host}
SSH Jump True 2
    [Arguments]   ${host}   ${user}   ${pass}   ${jumphost}  ${jumpuser}  ${jumppass}
    SROS Connect
        ...  sros_address=${host}
        ...  username=${user}
        ...  password=${pass}
        ...  sshjumphost=${jumphost}
        ...  sshjumpuser=${jumpuser}
        ...  sshjumppass=${jumppass}
        ...  timeout= 5 minutes

SSH Jump False 2
    [Arguments]    ${host}   ${user}   ${pass}
    SROS Connect
        ...  sros_address=${host}
        ...  username=${user}
        ...  password=${pass}
        ...  timeout= 5 minutes  
SSH True
    [Arguments]    ${host}    ${user}    ${pass}
    Log to Console      \nWorking on ${host}
    Set Suite Variable   ${discovery}      True

    Run Keyword If    ${ssh_jump}    SSH Jump True 2    ${host}   ${user}   ${pass}   ${jumphost}  ${jumpuser}  ${jumppass}
    Run Keyword If    '${ssh_jump}'== 'False'     SSH Jump False 2      ${host}   ${user}   ${pass}



    ${system_name}                        Send SROS Command And Parse Output Using Template
    ...                                           show system information
    ...                                           Temp_Lib/system_name.template
    ${system_id}                          Send SROS Command And Parse Output Using Template
    ...                                           show router interface "system"
    ...                                           Temp_Lib/system_id.template
    ${summary_all}                        Send SROS Command And Parse Output Using Template
    ...                                            show router bgp summary all
    ...                                            Temp_Lib/summary_all.template
    ${bgp_route_v4}                       Send SROS Command And Parse Output Using Template
    ...                                            show router bgp routes 
    ...                                            Temp_Lib/bgp_all.template
    ${bgp_learned_v4}  ${bgp_route_table_v4}  Run Keyword If  "${bgp_route_v4}" != '[]'     Set Routes BGPv4
    ...  ELSE      Set Empty Routes BGPv4    ${bgp_route_v4}
    ${bgp_route_v6}                       Send SROS Command And Parse Output Using Template
    ...                                            show router bgp routes ipv6 
    ...                                            Temp_Lib/bgp_all.template   
    ${bgp_learned_v6}  ${bgp_route_table_v6}  Run Keyword If  "${bgp_route_v6}" != '[]'     Set Routes BGPv6
    ...  ELSE      Set Empty Routes BGPv6    ${bgp_route_v6}
    
    ${router_interface}                   Send SROS Command And Parse Output Using Template
    ...                                            show router interface
    ...                                            Temp_Lib/router_interface.template
    SROS Disconnect

    update_csv_file     ${system_name}  ${system_id}  ${summary_all}  ${bgp_route_v4}  ${bgp_route_v6}  ${bgp_learned_v4}  ${bgp_learned_v6}  ${bgp_route_table_v4}  ${bgp_route_table_v6}  ${router_interface}  ${max_AS}

    Log to Console    \nDone with ${host}
    
SSH False 
    [Arguments]    ${host}
    Log to Console    \n${host} host unreachable


Set Routes BGPv4
    ${bgp_learned_v4}                     Send SROS Command And Parse Output Using Template
    ...                                            show router bgp routes | match "Routes" 
    ...                                            Temp_Lib/bgp_learned.template
    ${bgp_route_table_v4}                 Send SROS Command And Parse Output Using Template
    ...                                            show router route-table protocol bgp | match "Routes"
    ...                                            Temp_Lib/bgp_route_table.template    
    [Return]  ${bgp_learned_v4}  ${bgp_route_table_v4}

Set Empty Routes BGPv4
    [Arguments]     ${bgp_route_v4}
    ${bgp_learned_v4}   Set Variable   ${bgp_route_v4}
    ${bgp_route_table_v4}   Set Variable   ${bgp_route_v4}
    [Return]  ${bgp_learned_v4}  ${bgp_route_table_v4}
Set Routes BGPv6
    ${bgp_learned_v6}                     Send SROS Command And Parse Output Using Template
    ...                                            show router bgp routes ipv6 | match "Routes" 
    ...                                            Temp_Lib/bgp_learned.template
    ${bgp_route_table_v6}                 Send SROS Command And Parse Output Using Template
    ...                                            show router route-table family ipv6 protocol bgp | match "Routes"
    ...                                            Temp_Lib/bgp_route_table.template
    [Return]  ${bgp_learned_v6}  ${bgp_route_table_v6}

Set Empty Routes BGPv6
    [Arguments]    ${bgp_route_v6}
    ${bgp_learned_v6}     Set Variable   ${bgp_route_v6}
    ${bgp_route_table_v6}     Set Variable   ${bgp_route_v6}
    [Return]  ${bgp_learned_v6}  ${bgp_route_table_v6}