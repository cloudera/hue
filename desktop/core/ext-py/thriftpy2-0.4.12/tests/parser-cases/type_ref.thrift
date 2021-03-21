include "type_ref_shared.thrift";

const type_ref_shared.Writer jerry = {
    'name': 'jerry', 'age': 26,
    'country': type_ref_shared.Country.US}
const type_ref_shared.Book book = {'writer': jerry, 'name': 'Hello World'}
