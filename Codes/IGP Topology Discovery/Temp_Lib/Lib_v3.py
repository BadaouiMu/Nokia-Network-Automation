import networkx as nx
import matplotlib.pyplot as plt
import warnings
import pandas as pd
import paramiko
from socket import error as socket_error
import ast
import numpy as np

global G, table_data, last_clicked, Xx, Yy, node, release, current_node, current_annotation
last_clicked, Xx, Yy, node, release= "None", 0, 0, "N", "N"
current_node= None
current_annotation = None

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

def update_csv_file(router_name, router_id, ospf_neighbor, isis_neighbor, isis_data, route_ospf, route_isis, total_ospf_learned, total_ospf_table,total_isis_learned, total_isis_table, min_cost_ospf, min_cost_isis ):
    
    warnings.filterwarnings("ignore")
    total_ospf_learned= total_ospf_learned[0][0]   if len(total_ospf_learned) >= 1 and len(total_ospf_learned[0]) >= 1 else "not configured"
    total_ospf_table= total_ospf_table[0][0]   if len(total_ospf_table) >= 1 and len(total_ospf_table[0]) >= 1 else "not configured"
    total_isis_learned= total_isis_learned[0][0]   if len(total_isis_learned) >= 1 and len(total_isis_learned[0]) >= 1 else "not configured"
    total_isis_table= total_isis_table[0][0]   if len(total_isis_table) >= 1 and len(total_isis_table[0]) >= 1 else "not configured"
    table = []
    table.append(total_ospf_learned)
    table.append(total_ospf_table)
    table.append(total_isis_learned)
    table.append(total_isis_table)
    min_cost_ospf = int(min_cost_ospf)
    min_cost_isis = int(min_cost_isis)

    router_id = router_id[0][0]
    router_name = router_name[0][0]
    router_id= router_id
    id= router_id 
    router_id = router_name + "-" + router_id
    
    ospf_neighborr=[]
    for i in ospf_neighbor: 
        ospf_neighborr.append(i[0])
    ospf_neighbor = ospf_neighborr




    ospf_routee=[]
    for i in route_ospf: 
        ospf_routee.append(i[0])
        
    ospf_route = ospf_routee

    isis_neighborr=[]
    for i in isis_neighbor: 
        isis_neighborr.append(i[0])
    isis_neighbor =isis_neighborr
    
    Nodee = []
    new_node= []  # new $$$
    new_node.append(router_id)


    isis_neighbor2=[]
    for i in isis_neighbor:
        for j in isis_data:
            if i==j[0]:
                isis_neighbor2.append(j[1])
                break
    isis_neighbor= isis_neighbor2
    

    isis_route2= []
    for i in route_isis:
        isis_route2.append(i[0])
    isis_route = isis_route2

    
    dark= []
    for i in ospf_neighbor:
        tmp = []
        tmp.append(router_id)
        new_node.append(i)   # new $$$
        tmp.append(i)
        for j in route_ospf:
            if i==j[0]:
                metric=j[1]
        tmpp = 0
        for j in isis_neighbor: 
            if i==j:
                tmpp= 1
        if tmpp == 0 : 
            tmp.append("OSPF")
            tmp.append(f"{metric}")
        else:
            for jjj in route_isis:
                if i==jjj[0] :
                    metric2=jjj[1]
            tmp.append("OSPF$$$ISIS")
            tmp.append(f"{metric}\n{metric2}")
            
        dark.append(tmp)


    for i in isis_neighbor:
        tmpp=0
        for j in ospf_neighbor:
            if j==i:
                tmpp=1
        if tmpp==0:
            tmp = []
            tmp.append(router_id)
            new_node.append(i)  # new $$$
            tmp.append(i) 
            tmp.append("ISIS")
            for jjj in route_isis:
                if i==jjj[0] :
                    metric2=jjj[1]
            tmp.append(f"{metric2}")

            dark.append(tmp)

    light= []
    #hosts=[]
    #nb_empty_host = 0  #new $$$

    #max_empty_router = 1
    #for i in list_host:
    #    hosts.append (i[0])
    
    for i in ospf_route:
        if i not in router_id:
            metric,metric2 = 0,0
            for j in route_ospf:
                if i==j[0]:
                    metric=j[1]
            tmpp = 0
            for j in isis_route: 
                if i==j:
                    tmpp= 1
                    for jjj in route_isis:
                        if i==jjj[0] :
                            metric2=jjj[1]
            #if i in hosts or i in new_node or ( nb_empty_host < max_empty_router and ((int(metric) <= min_cost_ospf and metric!=0)  or (metric2!= 0 and int(metric2) <= min_cost_isis))):#new $$$
            if  i in new_node or ((int(metric) <= min_cost_ospf and metric!=0)  or (metric2!= 0 and int(metric2) <= min_cost_isis)):#new $$$
                if i not in new_node:#new $$$
                    #nb_empty_host += 1#new $$$
                    new_node.append(i)#new $$$
                tmp = []
                tmp.append(router_id)
                tmp.append(i)                        
                if tmpp == 0 : 
                    tmp.append("OSPF")
                    tmp.append(f"{metric}")
                else:
                    tmp.append("OSPF$$$ISIS")
                    tmp.append(f"{metric}\n{metric2}")
                light.append(tmp) 

    for i in isis_route:
        if i not in router_id:
            tmpp=0
            for j in ospf_route:
                if j==i:
                    tmpp=1
            if tmpp==0:
                metric2=0
                for jjj in route_isis:
                    if i==jjj[0]:
                        metric2=jjj[1]
                #if i in hosts or i in new_node or ( nb_empty_host < max_empty_router and metric2 !=0 and int(metric2) <= min_cost_isis): #new $$$
                if i in new_node or ( metric2 !=0 and int(metric2) <= min_cost_isis): #new $$$
                    tmp = []
                    tmp.append(router_id)
                    tmp.append(i)
                    
                    if  i not in new_node:#new $$$
                        #nb_empty_host += 1#new $$$
                        new_node.append(i)#new $$$
                    tmp.append("ISIS")
                    tmp.append(f"{metric2}")
                    light.append(tmp)
    '''
    #for i in ospf_neighbor:
        if i not in Nodee:
            Nodee.append(i)
    for i in ospf_route:
        if i not in Nodee:
            Nodee.append(i)
    for i in isis_neighbor:
        if i not in Nodee:
            Nodee.append(i)
    for i in isis_route:
        if i not in Nodee:
            Nodee.append(i)
    '''
    Node= new_node
    #new_node.extend(set(hosts) - set(new_node))
    try:
        df = pd.read_csv("IGP_table.csv")
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Node", "dark", "light", "table", "connection"])

    mask = df["Node"] == Node[0]
    if mask.any():
        df = df[~mask]
        df.reset_index(drop=True, inplace=True)
         
    mask = df["Node"] == id
    if mask.any():
        df = df[~mask]
        df.reset_index(drop=True, inplace=True)

    row_dict = {"Node": Node[0],"dark":dark, "light":light, "table":table, "connection":Node}
    df = df.append(row_dict, ignore_index=True)

    mask = df["Node"].tolist()  #### add addition condition for checking existing entry (RX-Z.Z.Z.Z use split)
    for i in Node[1:]:
        jjj=0
        for j in mask:
            if i in j:
                jjj=1
        if jjj==0:
            row_dict = {"Node": i,"dark":"", "light":"", "table":"", "connection":""}
            df = df.append(row_dict, ignore_index=True)

    df.to_csv("IGP_table.csv", index=False)


def for_plot():
    nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=500)
    nx.draw_networkx_edges(G, pos, width=2, edge_color='gray')
    light_edges = [(u, v) for u, v, data in G.edges(data=True) if 'color' in data and data['color'] == 'lightblue']
    nx.draw_networkx_edges(G, pos, edgelist=light_edges, width=2, edge_color='lightblue', label="Logical")
    dark_edges = [(u, v) for u, v, data in G.edges(data=True) if 'color' in data and data['color'] == 'black']
    nx.draw_networkx_edges(G, pos, edgelist=dark_edges, width=2, edge_color='black', label="Physical")
    edge_labels= {}
    for u, v, data in G.edges(data=True):
        ll=0
        metric1=""
        metric2=""
        for light in lights:
            if type(light) != float:
                light = ast.literal_eval(light)
                for jo in  light:
                    if  (u in jo[0] and v in jo[1]) or (jo[0] in u  and jo[1] in v):
                        ll=1
                        metric1= jo[3]
                        #print(metric1)
                    if  (v in jo[0] and u in jo[1]) or (jo[0] in v  and jo[1] in u):
                        ll=1
                        metric2= jo[3]
                        #print(metric2)
        if ll==1:
            if 'protocole2' in data:
                metric11=""
                metric12=""
                metric21=""
                metric22=""
                
                if "\n" in metric1:
                    metric11, metric12 = metric1.split("\n")
                else:
                    metric11=metric1
                if "\n" in metric2:                    
                    metric21, metric22 = metric2.split("\n")
                else:
                    metric12=metric2
                if pos[u][0] < pos[v][0]:
                    label = f"{metric11}> {data['protocole1']} <{metric21}\n{metric12}> {data['protocole2']} <{metric22}"
                else :
                    label = f"{metric21}> {data['protocole1']} <{metric11}\n{metric22}> {data['protocole2']} <{metric12}"
            else:
                if pos[u][0] < pos[v][0]:
                    label = f"{metric1}> {data['protocole1']} <{metric2}"
                else :
                    label = f"{metric2}> {data['protocole1']} <{metric1}"
            edge_labels[(u, v)] = label
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)
    nx.draw_networkx_labels(G, pos, font_size=12, font_color='black')
    plt.axis('off')
    colors = {"node":"Routers", "black": "Physical", "lightblue": "Logical"}
    plt.legend(colors.values(), loc=1)
    plt.show()
    plt.draw()
    
def igp_topology_discovery():
    global AS_list, pos, G, table_data, pos

    df = pd.read_csv('IGP_table.csv')
    
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

    G= nx.Graph()

    node_attrss = {}
    table_data= {}
    for i, router_id in enumerate(Node):
        G.add_node(router_id)
        if type(table[i]) != float:
            table[i] = ast.literal_eval(table[i])
            ospf_learned = table[i][0]
            ospf_rtable = table[i][1]
            isis_learned = table[i][2]
            isis_rtable = table[i][3]

            table_str =   "--------------------------------------------------------\n"
            table_str +=  "|                                    |  OSPF  |  ISIS  |\n"
            table_str +=  "--------------------------------------------------------\n"
            table_str += f"| learned route                      | {ospf_learned.ljust(6)} | {isis_learned.ljust(6)} |\n"
            table_str += f"| routing table                      | {ospf_rtable.ljust(6)} | {isis_rtable.ljust(6)} |\n"
            table_str +=  "--------------------------------------------------------\n"

            node_attrss[router_id] = {"table":table_str}
            table_data[router_id] = node_attrss[router_id]['table']

   
    for light in lights:
        if type(light) != float:
            light = ast.literal_eval(light)
            for i in light:
                router_id= i[0]
                neighbor_id= i[1]
                for jjj in Node:
                    if neighbor_id in jjj:
                        neighbor_id= jjj
                
                protocole = i[2]
                metric_id = i[3]

                if "$$$" in protocole:
                    protocole1, protocole2 = protocole.split("$$$")
                    G.add_edge(router_id, neighbor_id, protocole1=protocole1, color="lightblue")
                    G.add_edge(router_id, neighbor_id, protocole2=protocole2, color="lightblue")

                else:
                    G.add_edge(router_id, neighbor_id, protocole1=protocole, color="lightblue")
    edge_labels = {}

    for dark in darks:
        if type(dark) != float:
            dark = ast.literal_eval(dark)
            for i in dark:
                router_id= i[0]
                neighbor_id= i[1]
                for jjj in Node:
                    if neighbor_id in jjj:
                        neighbor_id= jjj                
                protocole = i[2]
                metric_id = i[3]
                if "$$$" in protocole:
                    protocole1, protocole2 = protocole.split("$$$")
                    G.add_edge(router_id, neighbor_id, protocole1=protocole1, color="black")
                    G.add_edge(router_id, neighbor_id, protocole2=protocole2, color="black")
                else:
                    G.add_edge(router_id, neighbor_id, protocole1=protocole, color="black")

            

    pos = nx.spring_layout(G, seed=42)
    for_plot()
    
    
 

#############################
def on_click(event):
    global last_clicked, Xx, Yy, node, pos, release
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
                if node in (table_data.keys()):
                    plt.gca().text(0.5, 0.5, table_data[node], bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5), fontsize=10, transform=plt.gca().transAxes, verticalalignment='center', horizontalalignment='center')
                plt.gca().set_axis_off()
                last_clicked = node
            plt.draw()
#############################
def on_release(event):
    global last_clicked, Xx, Yy, node, release
    release = "K"
###########################
def on_motion(event):
    global last_clicked, Xx, Yy, node, pos, release
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
'''
#igp_topology_discovery()
#update_csv_file([['R1']], [['2.2.2.2']], [['3.3.3.3']], [['R3']], [['3.3.3.3', 'R3']] , [['2.2.2.2', '0'], ['3.3.3.3', '2'], ['4.4.4.4', '4']], [['2.2.2.2', '0', 'R1'], ['3.3.3.3', '10', 'R3'], ['4.4.4.4', '20', 'R3']], [['8']], [['5']], [['4']], [['0']])
#def update_csv_file(router_name, router_id, ospf_neighbor, isis_neighbor, isis_data, route_ospf, route_isis, total_ospf_learned, total_ospf_table,total_isis_learned, total_isis_table ):
update_csv_file([['R1']], [['1.1.1.1']], [['3.3.3.3']], [['R3']], [['3.3.3.3', 'R3']] , [['2.2.2.2', '500'], ['3.3.3.3', '2'], ['4.4.4.4', '4']], [['2.2.2.2', '500', 'R1'], ['3.3.3.3', '10', 'R3'], ['4.4.4.4', '20', 'R3']], [['8']], [['5']], [['4']], [['0']], 50, 50)
update_csv_file([['R2']], [['1111']], [['3333']], [['R33']], [['3333', 'R33']] , [['2222', '500'], ['3333', '2'], ['4444', '4']], [['2222', '500', 'R1'], ['3333', '10', 'R3'], ['4444', '20', 'R3']], [['8']], [['5']], [['4']], [['0']],50, 50)


igp_topology_discovery()
'''