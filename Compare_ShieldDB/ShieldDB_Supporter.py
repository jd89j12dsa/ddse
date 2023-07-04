import heapq
import sys
import os
import pdb
import time
import csv
import shutil
import utilities
import math
import pymongo
from collections import defaultdict
def generate_graph(weights, a):
    graph = [[float('inf')] * len(weights) for _ in range(len(weights))]
    min_weight = float('inf')

    for i in range(len(weights)):
        graph[i][i] = 0
        for j in range(i+a,len(weights)):
                weight = abs(j - i) * weights[j]
                min_weight = min (weight, min_weight)
                graph[i][j] = weight
    return graph,min_weight

def generate_heuristic(weights,a,min_weight):

    all_weights = sum(weights)

    heuristic = [ sum(weights[i:min(i+a,len(weights))])- weights[i]*min(a,len(weights)-i) for i in range(len(weights))]

    #pdb.set_trace()

    max_heuristic = max(heuristic)*min_weight/2

    heuristic = [(i/max_heuristic) for i in heuristic]

    return heuristic

def dijkstra(graph, heuristic, alpha, start, end):
    pq = [(0, 0, start)]
    distances = [float('inf')] * len(graph)
    distances[start] = 0
    previous_vertices = [None] * len(graph)

    while pq:
        priority, current_distance, current_vertex = heapq.heappop(pq)

        #print('I am at:', current_vertex, 'priority: ', priority, 'current_distance: ', current_distance)

        if current_distance > distances[current_vertex]:
            continue

        for neighbor in range(len(graph[current_vertex])):
            if current_vertex+ 2*alpha < neighbor:
                continue
            weight = graph[current_vertex][neighbor]
            if weight == float('inf'):
                continue
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_vertices[neighbor] = current_vertex
                priority = distance + heuristic[neighbor]
                heapq.heappush(pq, (priority, distance, neighbor))

    path = []
    if distances[end] == float('inf'):
        print('shortest_path failed at: ', current_vertex)

    current_vertex = end
    while current_vertex is not None:
        path.append(current_vertex)
        current_vertex = previous_vertices[current_vertex]
    path = path[::-1]

    return distances[end], path

def DB_read(test_db_name):

    myclient = pymongo.MongoClient("mongodb://localhost:27017/?maxPoolSize=600&w=0")
    mydb = myclient[test_db_name]
    plaintextdb = myclient[test_db_name] 

    return myclient,mydb,plaintextdb


def write_result(result_string,result_path,data):
    resultpath = "./Result"+ '/' + test_db_name + '/' + result_path +'/'+ str(dis_a) + '/'
    if os.path.exists(resultpath) == False:
        os.makedirs(resultpath) 

    resultpath += result_string
    filename = open( resultpath,'w')
    for d in data:
        filename.writelines(d)
    filename.close()


def cluster_from_stp(nodelist, shortest_path):

    nodelist_name = [i[0] for i in nodelist]
    nodelist_occ = [i[1] for i in nodelist]
    keyword_in_cluster_list = []
    cluster_keywords = []
    cluster_keywords_occ = []
    output_clusters_points=[]
    lastind = -1
    for ind in shortest_path:
        if lastind == -1:
            lastind = ind
        else:
            cluster_keywords.append(nodelist_name[lastind:ind])
            cluster_keywords_occ.append(sum(nodelist_occ[lastind:ind]))
            output_clusters_points.append(lastind)
            keyword_in_cluster_list.extend([ind+1 for _ in range(lastind,ind)])
            lastind = ind

    wiki_wl_v_off_SampleDataOfShieldDB = []
    for i in cluster_keywords:
        wiki_wl_v_off_SampleDataOfShieldDB.extend(i)

    # utilities.dump_data_to_file(wiki_wl_v_off_SampleDataOfShieldDB,'./Var/'+test_db_name,'wiki_wl_v_off_SampleDataOfShieldDB.pkl')

    return cluster_keywords,cluster_keywords_occ,keyword_in_cluster_list,output_clusters_points[1:]


def get_cluster_occ(cluster_keywords_occ):

    all_occ = sum(cluster_keywords_occ)
    print("recommend thresshold: [", cluster_keywords_occ[0], cluster_keywords_occ[-1],"]")
    cluster_occ = [i/all_occ for i in cluster_keywords_occ]

    return cluster_occ

def get_keywords_occ(nodelist):

    all_occ = sum([i[1] for i in nodelist])
    keywords_occ = [(i[0],i[1],i[1]/all_occ) for i in nodelist]

    return keywords_occ

def output_cluster_dist(test_db_name,keywords_occ,keyword_in_cluster_list):
    
    #pdb.set_trace()
    data = [[i[0],i[1],i[2]] for i in keywords_occ]
    file_path = "./Var/"  + test_db_name + '/' + test_db_name + "_cluster_dists.csv"

    with open(file_path,'w', newline = "") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)

def flushstream():

    path = './Var/' + test_db_name + '/streaming/'
    if os.path.exists(path) == True:
        shutil.rmtree(path)

def Writestream(filename,data):

    Writestreampath = './Var/' + test_db_name + '/streaming/'
    if os.path.exists(Writestreampath) == False:
        os.makedirs(Writestreampath)

    file_path = Writestreampath+str(filename)
    with open(file_path,'w', newline = "" ) as file:
        file.write(','.join(item for item in data))


def output_cluster_points(test_db_name,n_keywords, dis_a, cluster_keywords_occ):

    data = [[n_keywords,dis_a,cluster_keywords_occ]]

    file_path = "./Var/" + test_db_name + '/' + test_db_name + "_cluster_points.csv"
    with open(file_path,'w', newline = "") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)


def process_anno(keyword_dict):
    
    filename_dict = defaultdict(list)
    same_filename_count_dict = defaultdict(lambda : 0)
    filename_name = {}
    filename_value = {}
    file_Attack_doc = []
    fileno = 0
    
    for keyword, filenames in keyword_dict.items():

        temp_same_file_count_dict = defaultdict(lambda : 0)

        for filename in filenames:
            if filename not in filename_name:
                filename_name[filename] = fileno
                fileno += 1
            
            No_filename = filename_name[filename]
            temp_same_file_count_dict[No_filename]+=1
            filename_dict[No_filename].append(keyword)

        for No_filename, count in temp_same_file_count_dict.items():

            same_filename_count_dict[No_filename] = max(same_filename_count_dict[No_filename], count)


    filenumber = 1

    for No_filename, keyword in filename_dict.items():

        keyword = list(set(keyword))

        for i in range(same_filename_count_dict[No_filename]):

            Writestream(filenumber,keyword)
            file_Attack_doc.append(keyword)

            filename_value[filenumber] = No_filename

            filenumber+=1

    utilities.dump_data_to_file(file_Attack_doc,'./Var/'+test_db_name,'wiki_doc.pkl')
    utilities.dump_data_to_file(filename_value,'./Var/'+test_db_name, 'translate_dict')

if __name__ == '__main__':

    test_db_name = str(sys.argv[1])
    dis_a = int(sys.argv[2])

    myclient,mydb,plaintextdb = DB_read(test_db_name)
    plaintext_col = plaintextdb["id_keywords"]
    plaintext_cur = plaintext_col.find(no_cursor_timeout=True).batch_size(1000)
    plaintextdata = dict()
    flushstream()

    for plaintext in plaintext_cur:
        plaintextdata[plaintext['k']] = plaintext['val_set']

    process_anno(plaintextdata)

    #pdb.set_trace()

    for keyword, val_set in plaintextdata.items():

        plaintextdata[keyword] = len(val_set) 

    plaintextdata = sorted(plaintextdata.items(), key = lambda x : x[1])

    nodelist = [(key,value) for key,value in plaintextdata]

    graph,min_weight = generate_graph([0]+[i[1] for i in nodelist], dis_a)

    heuristic = generate_heuristic([0]+[i[1] for i in nodelist], dis_a,min_weight)

    # time of the cluster distribution generation

    ts = time.time()

    distance, shortest_path = dijkstra(graph, heuristic, dis_a ,0, len(nodelist))

    data = []
    data.append("Cluster_gen: "+str(time.time()-ts)+'\n')
    write_result("Setup_cluster.txt", "Setup", data)

    cluster_keywords,cluster_keywords_occ,keyword_in_cluster_list,output_clusters_points = cluster_from_stp(nodelist, shortest_path)

    utilities.dump_data_to_file(cluster_keywords,'./Var/'+test_db_name+'/',"fixed_clusters_keywords")

    n_keywords = len(plaintextdata)

    output_cluster_points(test_db_name,n_keywords, dis_a, output_clusters_points)

    keywords_occ = get_keywords_occ(nodelist)
    
    cluster_occ = get_cluster_occ(cluster_keywords_occ)

    utilities.dump_data_to_file(cluster_occ,'./Var/'+test_db_name+'/',"prob_clusters")

    output_cluster_dist(test_db_name,keywords_occ,keyword_in_cluster_list)



    
    

