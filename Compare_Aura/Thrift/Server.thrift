namespace cpp server

struct SerialisedNode {
    1: i64 index,
    2: i32 level,
    3: binary key
}

service SSEService {
    oneway void add_entries(1:string label, 2:string tag, 3:list<string> ciphertext_list),
    list<i32> search(1:string token, 2: list<SerialisedNode> node_list,3:i32 level)
}