include "value_ref_shared.thrift";

const i32 abc = 899

const map<string, list<i32>> container = value_ref_shared.container;
const list<i32> lst = [value_ref_shared.int32, abc, 123];
