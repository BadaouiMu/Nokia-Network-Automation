import networkx as nx
import matplotlib.pyplot as plt
import warnings
import pandas as pd
import paramiko
from socket import error as socket_error
import ast
import numpy as np
import random

global G, table_data, last_clicked, Xx, Yy, node, release
last_clicked, Xx, Yy, node, release= "None", 0, 0, "N", "N"

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

def update_csv_file(router_name, router_id, summary_all, bgp_route_v4, bgp_route_v6, bgp_learned_v4, bgp_learned_v6, bgp_table_v4, bgp_table_v6, interfaces, Max_AS):
    warnings.filterwarnings("ignore")
    # for table:
    bgp_learned_v4= bgp_learned_v4[0][0]   if len(bgp_learned_v4) >= 1 and len(bgp_learned_v4[0]) >= 1 else "N"
    bgp_table_v4= bgp_table_v4[0][0]   if len(bgp_table_v4) >= 1 and len(bgp_table_v4[0]) >= 1 else "N"
    bgp_learned_v6= bgp_learned_v6[0][0]   if len(bgp_learned_v6) >= 1 and len(bgp_learned_v6[0]) >= 1 else "N"
    bgp_table_v6= bgp_table_v6[0][0]   if len(bgp_table_v6) >= 1 and len(bgp_table_v6[0]) >= 1 else "N"
    table = []
    table.append(bgp_learned_v4)
    table.append(bgp_learned_v6)
    table.append(bgp_table_v4)
    table.append(bgp_table_v6)
    ###########################3

    router_id_v4 = router_id[0][0] if len(router_id) >= 1 and len(router_id[0]) >= 1 else ""
    router_id_v6 = router_id[1][0] if len(router_id) >= 2 and len(router_id[1]) >= 1 else ""
    router_name = router_name[0][0]
    
    router_id = router_name + "\n" + router_id_v4 + "\n" + router_id_v6
    
    Max_AS = int(Max_AS)


    
    Node = []
    Node.append(router_id)
    


    # For AS : 
    ASn=0
    for i in bgp_route_v4:
        if i[0]==router_id_v4:
            ASn=i[1]+ " " + i[2]
            ASn = ASn.split()[-1]
            break
    ##################
    # for interfaces : 
    tmpp=[]
    for i in interfaces:
        tmpp.append(i[0])
    tmp=[]
    tmp.append(router_id)
    tmp.append(ASn)
    tmp.append(tmpp)
    interfaces = tmp
    ########################
    # for Dark: 
    dark= []
    for i in summary_all:
        if i[0]=="" and i[1]=="" and i[-1]!= "":
            tmp = dark [-1]
            del dark[-1]
            tmp[-1]= tmp[-1] + "\n" + i[-1]
        else:
            tmp = []
            tmp.append(router_id)
            tmp.append(i[0])
            tmp.append(i[1])
            prot= i[2]
            if i[1]==ASn:
                prot= "iBGP\n" + prot
            else:
                prot= "eBGP\n" + prot
            tmp.append(prot)
        dark.append(tmp)
    ###########################3    
    light= []
    for i in bgp_route_v4:
        if i[0]!= "":
            tmp = []
            ASn_tmp=i[1]+ " " + i[2]
            ASn_tmp = ASn_tmp.split()[-1]
            count_AS = ASn_tmp.count(" ")
            if count_AS < Max_AS:
                tmp.append(router_id)
                tmp.append(i[0])
                tmp.append(ASn_tmp)
                prot="IPv4"
                if ASn_tmp==ASn:
                    prot= "iBGP\n" + prot
                else:
                    prot= "eBGP\n" + prot
                tmp.append(prot)
                light.append(tmp)
    for i in bgp_route_v6:
        if i[0]!= "":
            tmp = []
            ASn_tmp=i[1]+ " " + i[2]        
            ASn_tmp = ASn_tmp.split()[-1]
            count_AS = ASn_tmp.count(" ")
            if count_AS < Max_AS:
                tmp.append(router_id)
                tmp.append(i[0])
                tmp.append(ASn_tmp)
                prot="IPv6"
                if ASn_tmp==ASn:
                    prot= "iBGP\n" + prot
                else:
                    prot= "eBGP\n" + prot
                tmp.append(prot)
                light.append(tmp)
    #8888888888888888888
    for i in light:
        if i[1] not in Node:
            Node.append(i[1])
    
    try:
        df = pd.read_csv("BGP_table.csv")
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Node", "dark", "light", "table", "interfaces", "connection"])
        
    mask = df["Node"].isin([Node[0], router_id_v4, router_id_v6])
    if mask.any():
        df = df[~mask]
        df.reset_index(drop=True, inplace=True)
    row_dict = {"Node": Node[0],"dark":dark, "light":light, "table":table, "interfaces":interfaces, "connection":Node}
    df = df.append(row_dict, ignore_index=True)

    mask = df["Node"].tolist() 
    for i in Node[1:]:
        jjj=0
        for j in mask:
            if i in j:
                jjj=1
        if jjj==0:
            row_dict = {"Node": i,"dark":"", "light":"", "table":"", "interfaces":"", "connection":""}
            df = df.append(row_dict, ignore_index=True)

    df.to_csv("BGP_table.csv", index=False)

def for_plot():
    nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=500)
    nx.draw_networkx_edges(G, pos, width=2, edge_color='gray')
    light_edges = [(u, v) for u, v, data in G.edges(data=True) if 'color' in data and data['color'] == 'lightblue']
    nx.draw_networkx_edges(G, pos, edgelist=light_edges, width=2, edge_color='lightblue', label="Learned")
    dark_edges = [(u, v) for u, v, data in G.edges(data=True) if 'color' in data and data['color'] == 'black']
    nx.draw_networkx_edges(G, pos, edgelist=dark_edges, width=2, edge_color='black', label="Neighbor")
    edge_labels= {}
    for u, v, data in G.edges(data=True):
        label = f"{data['protocole1']}"
        edge_labels[(u, v)] = label
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)
    nx.draw_networkx_labels(G, pos, font_size=12, font_color='black')
        
    plt.axis('off')
    plt.draw()
    legendd = {"node":"Routers", "black": "Neighbor", "lightblue": "Learned"}
    for i in AS_list:
        asn= i[0]
        minx= pos[i[1][0]][0]
        maxx= pos[i[1][0]][0]
        miny=pos[i[1][0]][1]
        maxy=pos[i[1][0]][1]
        for j in i[1]:
            minx= min (minx, pos[j][0])
            maxx= max (maxx, pos[j][0])
            miny= min (miny, pos[j][1])
            maxy= max (maxy, pos[j][1])
        add= 0.12
        if len(i[1])==1: 
            add= 0.3
        x =[minx-add, minx-add, maxx+add, maxx+add, minx-add ]
        y =[miny-add, maxy+add, maxy+add, miny-add, miny-add ]
        color = '#8B0000'
        plt.plot(x, y, color=color, linestyle="--", alpha=0.2)
        text_x = (maxx+add-0.2)
        text_y = (miny-add+0.05)
        plt.text(text_x, text_y, f'AS{asn}', fontsize=10,color= color,  horizontalalignment='center', verticalalignment='center')
        
    plt.legend(legendd.values(), loc=1)
    plt.show()

def bgp_topology_discovery():
    global AS_list, pos, G, table_data
    global pos
    AS_list=[]  
    
    df = pd.read_csv('BGP_table.csv')
    
    
        #%%%%%%%%%%%%%%%%%%%%%%%%%
    input_lists = df["connection"].tolist()
    
    l=[]
    for i, list in enumerate(input_lists):
        if type(list) != float:
            list = ast.literal_eval(list)   
            l.append (list) 
    input_lists=l
    for index1, list1 in enumerate(input_lists):
        for item1 in list1:
            for index2, list2 in enumerate(input_lists):
                if list1 != list2:
                    for item2 in list2:
                        if item1 in item2:
                            input_lists[index1].extend(set(list2) - set(list1))
                            input_lists[index2] = []
                            break

    max_list = max(input_lists, key=len)
    
    
    df = df[df['Node'].isin(max_list)]
    #%%%%%%%%%%%%%%%%
    
    
    global lights
    Node = df["Node"].tolist()
    darks= df["dark"].tolist()
    lights= df["light"].tolist()
    table= df["table"].tolist()
    interfaces = df["interfaces"].tolist()

    G= nx.Graph()
    node_attrss = {}
    table_data= {}
    for i, router_id in enumerate(Node):
        G.add_node(router_id)
        if type(table[i]) != float:
            table[i] = ast.literal_eval(table[i])
            bgp_learned_v4 = table[i][0]
            bgp_learned_v6 = table[i][0]
            bgp_table_v4 = table[i][1]
            bgp_table_v6 = table[i][1]

            table_str =   "--------------------------------------------------------\n"
            table_str +=  "|                                    |  BGPv4  |  BGPv6  |\n"
            table_str +=  "--------------------------------------------------------\n"
            table_str += f"| learned route                      | {bgp_learned_v4.ljust(6)} | {bgp_learned_v6.ljust(6)} |\n"
            table_str += f"| routing table                      | {bgp_table_v4.ljust(6)} | {bgp_table_v6.ljust(6)} |\n"
            table_str +=  "--------------------------------------------------------\n"

            node_attrss[router_id] = {"table":table_str}
            table_data[router_id] = node_attrss[router_id]['table']

    for_light=[]
    for light in lights:
        if type(light) != float:
            light = ast.literal_eval(light)
            for i in light:
                if i[1] != "":
                    router_id= i[0]
                    neighbor_id= i[1]
                    for jjj in Node:
                        if neighbor_id in jjj:
                            neighbor_id= jjj
                    protocole = i[3]
                    tmp_dark=[]
                    tmp_dark.append(router_id)
                    tmp_dark.append(neighbor_id)
                    tmp_dark.append(protocole)
                    for_light.append(tmp_dark)
                    lll=0
                    ll=0
                    
                    for s in AS_list:
                        if s[0]==i[2]:
                            ll=1
                            for ss in s[1]:
                                if ss in neighbor_id:
                                    lll=1
                            if lll==0:
                                s[1].append(neighbor_id)
                    if ll==0:
                        tmm=[]
                        tmm.append(i[2])
                        tm=[]
                        tm.append(neighbor_id)
                        tmm.append(tm)
                        AS_list.append(tmm)
    for i in for_light:
        protocole = i[2]
        for j in for_light:
            if i != j:
                if (i[0]==j[0] and i[1]==j[1]):
                    #print(i)
                    p1,p2 = j[2].split("\n")
                    protocole= protocole + "\n" + p2
                    del for_light[for_light.index(j)]
        if (i[0]!=i[1]):
            G.add_edge(i[0], i[1], protocole1=protocole, color="lightblue")    
    
    edge_labels = {}
    
    for_dark=[]
    for dark in darks:
        if type(dark) != float:
            dark = ast.literal_eval(dark)
            for i in dark:
                router_id= i[0]
                neighbor_id= i[1]
                tmpid=0
                for interface in interfaces:
                    if type(interface) != float:
                        interface = ast.literal_eval(interface)
                        if tmpid==1:
                            break
                        for kk in interface[2]:
                            if neighbor_id == kk:
                                tmpid=1
                                neighbor_id= interface[0]
                                break
                if tmpid==1:
                    protocole = i[3]
                    tmp_dark=[]
                    tmp_dark.append(router_id)
                    tmp_dark.append(neighbor_id)
                    tmp_dark.append(protocole)
                    for_dark.append(tmp_dark)             
    for i in for_dark:
        protocole = i[2]
        for j in for_dark:
            if i != j:
                if i[1]==j[1]:
                    p = j[2].split("\n") 
                    print
                    for jj in p[1:]:
                        protocole= protocole + "\n" + jj
                    del for_dark[for_dark.index(j)]
        G.add_edge(i[0], i[1], protocole1=protocole, color="black")
    pos = nx.spring_layout(G, seed=42)
    for_plot()
#############################
def on_click(event):
    global last_clicked
    global Xx
    global Yy
    global node
    global pos
    global release
    if event.inaxes is not None:
        node = None
        for n in G.nodes():
            if pos[n][0]-0.1 <= event.xdata <= pos[n][0]+0.1 and pos[n][1]-0.1 <= event.ydata <= pos[n][1]+0.1:
                node = n
                break
        if node is not None:
            nx.draw_networkx_labels(G, pos)
            Xx=event.xdata
            Yy=event.ydata
            if last_clicked == node:
                plt.gca().clear()
                for_plot()
                last_clicked = None
            else:
                release= "N"
                plt.gca().clear()
                for_plot()
                plt.gca().text(0.5, 0.5, table_data[node], bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5), fontsize=10, transform=plt.gca().transAxes, verticalalignment='center', horizontalalignment='center')
                plt.gca().set_axis_off()
                last_clicked = node
            plt.draw()
#############################
def on_release(event):
    global last_clicked
    global Xx
    global Yy
    global node
    global release
    release = "K"
###########################
def on_motion(event):
    global last_clicked
    global Xx
    global Yy
    global node
    global pos
    global release
    if last_clicked=="None" or release== "K":
        return
    dx = event.xdata - Xx
    dy = event.ydata - Yy
    pos[node][0] = pos[node][0] + dx
    pos[node][1] = pos[node][1] + dy
    Xx= event.xdata
    Yy= event.ydata
    nx.draw_networkx_labels(G, pos)
    plt.gca().clear()
    for_plot()
    
plt.gcf().canvas.mpl_connect('button_press_event', on_click)
plt.gcf().canvas.mpl_connect('button_release_event', on_release)
plt.gcf().canvas.mpl_connect('motion_notify_event',on_motion)

#update_csv_file([['R1']], [['1.1.1.1']], [['2.2.2.2', '100', 'IPv4'],['', '', 'IPv444444'], ['192.168.2.2', '200', 'IPv4'], ['1000::5', '100', 'IPv6'], ['2222::2', '200', 'IPv6'],['', '', 'IPv666']],  [['1.1.1.1', '200', '100'], ['2.2.2.2', '200', '100'], ['3.3.3.3', '200', '100'], ['4.4.4.4', '200', '100'], ['5.5.5.5', '200', '100'], ['6.6.6.6', '200', ''], ['7.7.7.7', '300', ''], ['7.7.7.7', '200', '100']],  [['1000::1', '200', '100'], ['1000::5', '200', '3000']], [['18']],  [['9']], [['4']], [['2']],  [['1.1.1.1'], ['1000::1'], ['192.168.11.1'], ['192.168.1.1'], ['192.168.1.9'], ['1133::1'], ['fe80::ca65:ffff:fe00:0'], ['192.168.1.13'], ['1144::1'], ['fe80::ca65:ffff:fe00:0'], ['192.168.2.1'], ['2222::1'], ['fe80::ca65:ffff:fe00:0']])

#update_csv_file([["F6"]], [["1.1.1.1", "f6f6::1"]], [["192.168.1.10", "200", "IPv4"], ["f6f7::2", "200", "IPv6"]], [["4.4.4.4", "200", "300"], ["3.3.3.3", "200", ""], ["2.2.2.2", "200", ""], ["1.1.1.1", "200", "100"]], [["f9f9::1", "200", "300"], ["f8f8::1", "200", ""], ["f7f7::1", "200", ""], ["f6f6::1", "200", "100"]], [["7"]], [["6"]], [["4"]], [["4"]], [["192.168.1.9", "f6f7::1", "fe80::1401:ffff:fe00:0", "192.168.1.1", "192.168.111.211", "1.1.1.1", "f6f6::"]])
#update_csv_file([["F7"]], [["2.2.2.2", "f7f7::1"]], [["192.168.1.9", "100", "IPv4"], ["f6f7::1", "100", "IPv6"], ["3.3.3.3", "200", "IPv4"], ["f8f8::1", "200", "IPv6"]], [["4.4.4.4", "100", "200 300"], ["3.3.3.3", "100", "200"], ["2.2.2.2", "100", "200"], ["1.1.1.1", "100", ""], ["4.4.4.4", "300", ""]], [["f9f9::1", "100", "200 300"], ["f8f8::1", "100", "200"], ["f7f7::1", "100", "200"], ["f6f6::1", "100", ""], ["f9f9::1", "300", ""]], [["7"]], [["6"]], [["4"]], [["4"]],[["2.2.2.2", "f7f7::1", "192.168.1.10", "f6f7::2", "fe80::5201:ff:fe1d:3", "192.168.1.1", "f7f8::1", "fe80::5201:ff:fe1d:2"]] )
#update_csv_file([["F8"]], [["3.3.3.3", "f8f8::1"]], [["192.168.1.6", "100", "IPv4"], ["f8f9::1", "100", "IPv6"], ["2.2.2.2", "200", "IPv4"], ["f7f7::1", "200", "IPv6"]], [["4.4.4.4", "300", ""], ["3.3.3.3", "300", "200"], ["2.2.2.2", "300", "200"], ["1.1.1.1", "100", ""], ["1.1.1.1", "300", "200 100"]], [["f9f9::1", "300", ""], ["f8f8::1", "300", "200"], ["f7f7::1", "300", "200"], ["f6f6::1", "300", "200 100"], ["f6f6::1", "100", ""]], [["7"]], [["6"]], [["4"]], [["4"]],[["3.3.3.3", "f8f8::1","192.168.1.2", "f7f8::2", "fe80::5201:ff:fe1e:2", "192.168.1.5", "f8f9::2", "fe80::5201:ff:fe1d:2"]] )
#update_csv_file([["F9"]], [["4.4.4.4", "f9f9::1"]], [["192.168.1.5", "100", "IPv4"], ["f8f9::2", "100", "IPv6"]], [["4.4.4.4", "200", "300"], ["3.3.3.3", "200", ""], ["2.2.2.2", "200", ""], ["1.1.1.1", "200", "100"]], [["f9f9::1", "200", "300"], ["f8f8::1", "200", ""], ["f7f7::1", "200", ""], ["f6f6::1", "200", "100"]], [["7"]], [["6"]], [["4"]], [["4"]],[["4.4.4.4", "f9f9::1","192.168.1.6", "f8f9::1", "fe80::5201:ff:fe1e:2", "192.168.111.211"]] )
#bgp_topology_discovery()