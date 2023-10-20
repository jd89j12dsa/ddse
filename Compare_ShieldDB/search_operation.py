import random, utilities
import sys
from sse_client import SSE_Client
from service_communicator import Service_Contactor
from timeit import default_timer as timer
import multiprocessing
import pymongo
import pdb

class Search_Operator(multiprocessing.Process):
    def __init__(self, client_state_folder, 
                 edb_host='127.0.0.1', edb_port='5000'):
       
        super(Search_Operator, self).__init__()
        
        #read client state
        client_state = utilities.load_data_from_file(client_state_folder, "client")
        #read trueDB data to generate random query keywords
        self.keywords_tracking = utilities.load_data_from_file(client_state_folder, "keywords_tracking") 
        self.sse_client = SSE_Client()
        self.sse_client.importClientState(client_state)
        
        #open edb connection 
        self.service_connector = Service_Contactor(edb_host,edb_port)
        self.test_db_name = 'VAX_USENIX'
        self.client_state_folder = client_state_folder
        
    def search_list(self):

        myclient = pymongo.MongoClient("mongodb://localhost:27017/?maxPoolSize=600&w=0")
        plaintextdb = myclient[self.test_db_name]
        search_col = plaintextdb['id_keyword_search_list']
        plaintext_cur = search_col.find(no_cursor_timeout=True).batch_size(1000)
        task_search = [x["k"] for x in plaintext_cur]
        return task_search

    def reverse(self,raw_ids):

        true_ids = []
        for raw_id in raw_ids:
            if int(raw_id) in self.reverse_map:
                true_ids.append(raw_id)
        ret_ids = []
        for raw_id in true_ids:
            if int(raw_id) < 1000000:
                ret_ids.append(raw_id)
        return list(set(ret_ids))

    def run(self):
        
        try:
            self.service_connector.open_connection()
            # n_query_number= int(0.1 * len(self.keywords_tracking))
            # n_query_number = min(1000, len(self.keywords_tracking))   
            # print("No. keywords " + str(len(self.keywords_tracking)))
            #serving counting attack
            access_patterns = []
            #total ids
            #total_ids = 0
            # value_dict = utilities.load_data_from_file(client_state_folder, "translate_dict")     
            #select keywords, #note search token to perform search later
            # self.keywords_tracking = sorted(self.keywords_tracking, key=lambda x: self.keywords_tracking[x], reverse=True)
            # print(self.keywords_tracking)
            # #print(n_query_keywords)
            n_query_keywords = self.search_list()
                
            query_time = 0
            wiki_wl_v_off_1 = {}
            wiki_wl_v_off_2 = {}
            cnt =0
            raw_ids = []
            for query_keyword in n_query_keywords:
                start_time = timer() # in seconds
                self.reverse_map = utilities.load_data_from_file(self.client_state_folder,'dup_translate')
                search_token= self.sse_client.generateToken(query_keyword)
                encrypted_IDs = self.service_connector.search_connect(search_token)
                if encrypted_IDs is not None:
                    wiki_wl_v_off_1[cnt] = len(encrypted_IDs)
                    wiki_wl_v_off_2[cnt] = sys.getsizeof(encrypted_IDs)
                    cnt+=1
                    raw_ids = self.sse_client.decryptIDs(encrypted_IDs)
                    #value_ids = [value_dict[raw] for raw in raw_ids]
                    #value_ids = list(set(raw_ids))
                
                local_raw_ids = self.search_local_cache(query_keyword)
                if local_raw_ids is not None:
                    raw_ids.extend(local_raw_ids)
                raw_ids_len = len(raw_ids)
                raw_ids = self.reverse(raw_ids)                
                access_patterns.append(raw_ids)

                end_time = timer() 

                #total_ids += len(encrypted_IDs)
                
                print(query_keyword,'\t',raw_ids_len,'\t', end_time - start_time)
                
                query_time += (end_time - start_time)
                # print(end_time - start_time, len(raw_ids))
                
                
            utilities.dump_data_to_file([wiki_wl_v_off_2,wiki_wl_v_off_1],"./","wiki_wl_v_off.pkl")
            #print("Total ids " + str(total_ids))
            #write search data to file

            
            utilities.dump_data_to_file(n_query_keywords, "tmp", "query")
            utilities.dump_data_to_file(access_patterns,"tmp", "access")
        #except:
        #    print("Search exception")
        finally:
            self.service_connector.close_connection()
            
    def search_local_cache(self, keyword):
        self.cached_data_clusters = utilities.load_data_from_file(self.client_state_folder, "cache")
        for cluster in self.cached_data_clusters:
            if keyword in cluster:
                return list(cluster[keyword])
        return None
