*** Settings ***

Resource             sats.robot
Library              Temp_Lib/Lib_v3.py

*** Variables ***            
${discovery}     False
${hosts}         hosts.txt
${ssh_jump}      True
${jumphost}      x.x.x.x
${jumpuser}      root
${jumppass}      Stage2023    
${Test_bol}      False

${min_cost_ospf}     0
${min_cost_isis}     0


*** Test Cases ***
Test 
    ${hostnames}    read_text    ${hosts}
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

    Run Keyword IF       ${discovery}     igp_topology_discovery

    

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
    ${ospf_neighbor}                      Send SROS Command And Parse Output Using Template
    ...                                           show ospf neighbor
    ...                                           Temp_Lib/ospf_neighbor.template
    ${routes_ospf}  ${ospf_learned}  ${ospf_routing_table}   Run Keyword If  "${ospf_neighbor}" != '[]'     Set Routes OSPF
    ...  ELSE      Set Empty Routes OSPF    ${ospf_neighbor}

    ${isis_neighbor}                      Send SROS Command And Parse Output Using Template
    ...                                           show router isis adjacency
    ...                                           Temp_Lib/isis_adjacency.template
    
    ${isis_data}  ${routes_isis}  ${isis_learned}  ${isis_routing_table}   Run Keyword If  "${isis_neighbor}" != '[]'     Set Routes ISIS
    ...  ELSE    Set Empty Routes ISIS    ${isis_neighbor}


    SROS Disconnect

    update_csv_file   ${system_name}  ${system_id}  ${ospf_neighbor}  ${isis_neighbor}  ${isis_data}  ${routes_ospf}  ${routes_isis}  ${ospf_learned}   ${isis_learned}  ${ospf_routing_table}   ${isis_routing_table}   ${min_cost_ospf}  ${min_cost_isis}  
    Log to Console    \nDone with ${host}
    
SSH False 
    [Arguments]    ${host}
    Log to Console    \n${host} host unreachable
Set Routes OSPF
    ${routes_ospf}                        Send SROS Command And Parse Output Using Template
    ...                                           show router ospf routes
    ...                                           Temp_Lib/route_ospf.template
    ${ospf_learned}                       Send SROS Command And Parse Output Using Template
    ...                                           show router ospf routes
    ...                                           Temp_Lib/learned_route.template
    ${ospf_routing_table}                 Send SROS Command And Parse Output Using Template
    ...                                           show router route-table protocol ospf 
    ...                                           Temp_Lib/learned_route_table.template
    [Return]  ${routes_ospf}  ${ospf_learned}  ${ospf_routing_table}

Set Empty Routes OSPF
    [Arguments]     ${ospf_neighbor}
    ${routes_ospf}  Set Variable   ${ospf_neighbor}
    ${ospf_learned}  Set Variable    ${ospf_neighbor}
    ${ospf_routing_table}  Set Variable    ${ospf_neighbor}
    [Return]  ${routes_ospf}  ${ospf_learned}  ${ospf_routing_table}
Set Routes ISIS
    ${isis_data}                          Send SROS Command And Parse Output Using Template
    ...                                           show router isis database detail
    ...                                           Temp_Lib/isis_database_detail.template
    ${routes_isis}                        Send SROS Command And Parse Output Using Template
    ...                                           show router isis routes 
    ...                                           Temp_Lib/route_isis.template
    ${isis_learned}                       Send SROS Command And Parse Output Using Template
    ...                                           show router isis routes 
    ...                                           Temp_Lib/learned_route.template
    ${isis_routing_table}                 Send SROS Command And Parse Output Using Template
    ...                                           show router route-table protocol isis 
    ...                                           Temp_Lib/learned_route_table.template
    [Return]  ${isis_data}  ${routes_isis}  ${isis_learned}  ${isis_routing_table}

Set Empty Routes ISIS
    [Arguments]    ${isis_neighbor}
    ${isis_data}     Set Variable   ${isis_neighbor}
    ${routes_isis}     Set Variable   ${isis_neighbor}
    ${isis_learned}     Set Variable    ${isis_neighbor}
    ${isis_routing_table}     Set Variable   ${isis_neighbor}
    [Return]  ${isis_data}  ${routes_isis}  ${isis_learned}  ${isis_routing_table}
