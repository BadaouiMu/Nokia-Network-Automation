*** Settings ***

Resource             sats.robot
Library              Temp_Lib/Lib_v2.py

*** Variables ***            
${path}                       software.pdf
${chapitre}                   Release 22.2.R1 Supported Hardware
${for_extracting}             False
${hosts}                      hosts.txt
${excel}                      False
${excel_path}                 Card_Inventory_sample.xlsx 

${ssh_jump}      False
${jumphost}      x.x.x.x
${jumpuser}      root
${jumppass}      Stage2023  
${Test_bol}      False


*** Test Cases ***
Test 
    Run Keyword IF       ${excel}     Retrieve from Excel    ${excel_path}    ${path}   ${chapitre}
    Run Keyword If    '${excel}'== 'False'     Retrieve From Routers     ${path}    ${chapitre}


    Log To Console       \n Done

*** Keywords ***
Retrieve from Routers 
    [Arguments]     ${path}     ${chapitre}
    ${hostnames}                 read_text    ${hosts}
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

    Run Keyword IF       ${for_extracting}     Extracting and Comparing      ${path}   ${chapitre}

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
    Set Suite Variable   ${for_extracting}      True

    Run Keyword If    ${ssh_jump}    SSH Jump True 2    ${host}   ${user}   ${pass}   ${jumphost}  ${jumpuser}  ${jumppass}
    Run Keyword If    '${ssh_jump}'== 'False'     SSH Jump False 2      ${host}   ${user}   ${pass}


    ${system_name}                        Send SROS Command And Parse Output Using Template
    ...                                           show system information
    ...                                           Temp_Lib/system_name.template
    ${version_name}                       Send SROS Command And Parse Output Using Template
    ...                                           show version
    ...                                           Temp_Lib/version.template 
    ${cards}                              Send SROS Command And Parse Output Using Template
    ...                                           show card detail
    ...                                           Temp_Lib/card.template
    ${MDAs}                               Send SROS Command And Parse Output Using Template 
    ...                                           show mda detail
    ...                                           Temp_Lib/mda.template
    
    SROS Disconnect

    update_csv_file     ${host}    ${system_name}    ${version_name}    ${cards}    ${MDAs}   

    Log to Console    \nDone with ${host}
    
SSH False 
    [Arguments]    ${host}
    Log to Console    \n${host} host unreachable
    
Extracting and Comparing
    [Arguments]    ${path}     ${chapitre}
    Log to Console      Working on: extracting and comparing
    extract_data_from_pdf      ${path}   ${chapitre}
    compare_csv_file           ${chapitre}

Retrieve From Excel
    [Arguments]    ${excel_path}   ${path}     ${chapitre}
    Log To Console    \nWorking on Excel file

    extract_data_from_pdf      ${path}   ${chapitre}
    compare_excel_file           ${excel_path}   ${chapitre}

    Log To Console    \nDone with Excel file
