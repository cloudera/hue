struct ListStruct {
    1: optional list<ListItem> list_items,
}

struct ListItem {
    1: optional list<string> list_string,
    2: optional list<list<string>> list_list_string,
}

struct MapItem {
    1: optional map<string, string> map_string,
    2: optional map<string, map<string, string>> map_map_string,
}

struct MixItem {
    1: optional list<map<string, string>> list_map,
    2: optional map<string, list<string>> map_list,
}
