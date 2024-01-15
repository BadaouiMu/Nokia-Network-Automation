*** Settings ***
Resource             sats.robot
Library              Temp_Lib/Lib.py

*** Variables ***        
${CLI}           True
${ssh_jump}      True
${jumphost}      x.x.x.x
${jumpuser}      root
${jumppass}      Stage2023    
${hosts}         hosts.txt

${Test_bol}      False

*** Test Cases ***
Test 
    ${hostnames}                 read_text     ${hosts}
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
    Log to Console      \n Working on ${host}
    
    Run Keyword If    ${ssh_jump}    SSH Jump True 2    ${host}   ${user}   ${pass}   ${jumphost}  ${jumpuser}  ${jumppass}
    Run Keyword If    '${ssh_jump}'== 'False'     SSH Jump False 2      ${host}   ${user}   ${pass}


    ${system_name}                        Send SROS Command And Parse Output Using Template
    ...                                           show system information
    ...                                           Temp_Lib/system_name.template
    ${system_id}                          Send SROS Command And Parse Output Using Template
    ...                                           show router interface "system"
    ...                                           Temp_Lib/system_id.template
    ${chassis}                            Send SROS Command And Parse Output Using Template
    ...                                           show chassis detail
    ...                                           Temp_Lib/chassis.template
    Run Keyword If    '${CLI}'== 'False'         Send SROS Command                  //
    ${prim_sec_image}                     Send SROS Command And Parse Output Using Template
    ...                                           show bof
    ...                                           Temp_Lib/show_bof.template 
    Run Keyword If    '${CLI}'== 'False'         Send SROS Command                  //
    ${card}                               Send SROS Command And Parse Output Using Template
    ...                                           show card detail
    ...                                           Temp_Lib/card.template
    ${mda}                                Send SROS Command And Parse Output Using Template 
    ...                                           show mda detail
    ...                                           Temp_Lib/mda.template
    ${port}                               Send SROS Command And Parse Output Using Template
    ...                                           show port 
    ...                                           Temp_Lib/port_no_desc.template
    ${port_description}                   Send SROS Command And Parse Output Using Template
    ...                                           show port description
    ...                                           Temp_Lib/port_desc.template
       
    SROS Disconnect
    
    HW_network_inventory   ${host}  ${system_name}  ${system_id}  ${chassis}  ${prim_sec_image}  ${card}  ${mda}  ${port}  ${port_description}  
    
    Log to Console    \nDone with ${host}
    
SSH False 
    [Arguments]    ${host}
    Log to Console    \n ${host} host unreachable


    