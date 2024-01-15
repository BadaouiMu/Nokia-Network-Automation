import csv
import pandas as pd
import camelot
import PyPDF2
from openpyxl import Workbook
from openpyxl.styles import PatternFill
import paramiko
from socket import error as socket_error
import warnings
def test_ssh(host, username, password):
    warnings.filterwarnings("ignore")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, username=username, password=password, timeout=10)
        return True
    except paramiko.AuthenticationException:
        return False
    except paramiko.SSHException as ssh_ex:
        return False
    except socket_error:
        return False
    finally:
        ssh.close()
    return False

def test_ssh_jump(host, username, password, jumphost, jumpuser, jumppass):
    warnings.filterwarnings("ignore")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(jumphost, username=jumpuser, password=jumppass, timeout=5)
        transport = ssh.get_transport()
        dest_addr = (host, 22)
        local_addr = ('', 0)
        channel = transport.open_channel("direct-tcpip", dest_addr, local_addr)
        target_ssh = paramiko.SSHClient()
        target_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        target_ssh.connect(host, username=username, password=password, sock=channel, timeout=5)
        return True
    except paramiko.AuthenticationException:
        return False
    except paramiko.SSHException as ssh_ex:
        return False
    except socket_error:
        return False
    finally:
        ssh.close()
    return False


def read_text(path):
    warnings.filterwarnings("ignore")
    list=[]

    with open(path) as device_file:
        
        for line in device_file:
            if line and line != "" and "," in line:
                list1=[]
                ipaddr, username, password = line.strip().split(",")
                list1.append(ipaddr)
                list1.append(username)
                list1.append(password)
                list.append(list1)

    return list

def HW_network_inventory(ip_address, list0, list1, list11, list6, list2, list3, list4, list5):
    warnings.filterwarnings("ignore")
    try:
        df = pd.read_excel("network_inventory.xlsx")
    except FileNotFoundError:
        df = pd.DataFrame(columns= ["IP Address", "Name", "system ID", "chassis type", "manufacture date", "part number", "software version", 
                                    "system up date", "primary image", "secondary image", "slot id", "card type", "Part Number", "manufacture date (card)", 
                                    "port cli name", "administrative state", "operational state", "description", "connector type"])

    
     
    system_name = list0[0][0] if len(list0) >= 1 and len(list0[0]) >= 1 else ""
    chassis_type = list0[0][1] if len(list0) == 1 and len(list0[0]) >= 1 else ""
    soft_version = list0[0][2] if len(list0) == 1 and len(list0[0]) >= 1 else ""
    soft_version = "TiMOS-"+soft_version
    up_date = list0[0][3] if len(list0) == 1 and len(list0[0]) >= 1 else ""
    
    system_id = list1[0][0] if len(list1) >= 1 and len(list1[0]) >= 1 else ""
    
    chassis_part = list11[0][0] if len(list11) >= 1 and len(list11[0]) >= 1 else ""
    chassis_date = list11[0][1] if len(list11) >= 1 and len(list11[0]) >= 1 else ""
    
    primary_image = list6[0][0] if len(list6) >= 1 and len(list6[0]) >= 1 else ""
    secondary_image = list6[0][1] if len(list6) >= 1 and len(list6[0]) >= 1 else ""

    mask = df["Name"] == system_name
    mask1 = df["IP Address"] == ip_address
    if mask.any() and mask1.any():
        df = df[~mask]
        df.reset_index(drop=True, inplace=True)
    for card in list2:
        card_id = card[0] if len(card) >= 1  else ""
        card_type = card[1] if len(card) >= 1 else ""
        card_admin_st= card[2] if len(card) >= 1 else ""
        card_oper_st= card[3] if len(card) >= 1 else ""
        if "down" in card_oper_st.lower():
            card_type = card_type + "(not equipped)"
        card_part = card[4][:10] if len(card) >= 1 and len(card[4])>10  else card[4]
        card_date = card[5] if len(card) >= 1 else ""
        row_dict= {"IP Address":ip_address, "Name":system_name, "system ID":system_id, "chassis type":chassis_type, "manufacture date":chassis_date, "part number":chassis_part, "software version":soft_version, 
                        "system up date":up_date, "primary image":primary_image, "secondary image":secondary_image, "slot id":str(card_id), "card type":card_type, "Part Number":card_part, "manufacture date (card)":card_date, 
                        "port cli name":"", "administrative state":card_admin_st, "operational state":card_oper_st, "description":"", "connector type":""}
        df = df.append(row_dict, ignore_index=True)
        if card_id.isdigit():
            for mda in list3:
                mda_card_id = mda[0] if len(mda) >= 1  else ""
                if mda_card_id==card_id:
                    mda_id = mda[1] if len(mda) >= 1  else ""
                    mda_type = mda[2] if len(mda) >= 1 else ""
                    mda_part = mda[5] if len(mda) >= 1  else ""
                    mda_date = mda[6] if len(mda) >= 1 else ""
                    mda_idd= "'"+card_id+"/"+mda_id
                    for port in list4:
                        port_card_id = port[0] if len(port) >= 1  else ""
                        port_mda_id = port[1] if len(port) >= 1  else ""
                        if port_card_id==card_id and port_mda_id==mda_id:
                            
                            port_id = port[2] if len(port) >= 1  else ""
                            #print(port_id)
                            port_admin_state = port[3] if len(port) >= 1  else ""
                            port_oper_state = port[4] if len(port) >= 1  else ""        
                            port_type = port[5] if len(port) >= 1 else ""
                            ioss=0
                            for por in list5:
                                port_card_id2 = por[0] if len(por) >= 1  else ""
                                port_mda_id2 = por[1] if len(por) >= 1  else ""
                                port_id2 = por[2] if len(por) >= 1  else ""
                                
                                if port_card_id2==port_card_id and port_mda_id2==port_mda_id and port_id2==port_id:
                                    ioss=1
                                    port_card_id2="'"+card_id+"/"+mda_id+"/"+port_id2
                                    #print(port_card_id2+" 2")
                                    port_desc = por[3] if len(por) >= 1  else ""
                                    row_dict= {"IP Address":ip_address, "Name":system_name, "system ID":system_id, "chassis type":chassis_type, "manufacture date":chassis_date, "part number":chassis_part, "software version":soft_version, 
                                                    "system up date":up_date, "primary image":primary_image, "secondary image":secondary_image, "slot id":mda_idd, "card type":mda_type, "Part Number":mda_part, "manufacture date (card)":mda_date, 
                                                        "port cli name":port_card_id2, "administrative state":port_admin_state, "operational state":port_oper_state, "description":port_desc, "connector type":port_type}
                                    df = df.append(row_dict, ignore_index=True)
                                    break
                            if ioss==0:
                                port_card_id="'"+card_id+"/"+mda_id+"/"+port_id
                                row_dict= {"IP Address":ip_address, "Name":system_name, "system ID":system_id, "chassis type":chassis_type, "manufacture date":chassis_date, "part number":chassis_part, "software version":soft_version, 
                                                    "system up date":up_date, "primary image":primary_image, "secondary image":secondary_image, "slot id":mda_idd, "card type":mda_type, "Part Number":mda_part, "manufacture date (card)":mda_date, 
                                                        "port cli name":port_card_id, "administrative state":port_admin_state, "operational state":port_oper_state, "description":"", "connector type":port_type}
                                df = df.append(row_dict, ignore_index=True)
    writer = pd.ExcelWriter('network_inventory.xlsx', engine='xlsxwriter')
    df = df.astype(str)
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    header_format = workbook.add_format({'bold': True, 'bg_color': '#90EE90'})
    worksheet.set_column(0, len(df.columns)-1, 20)
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_format)
    writer.save()
