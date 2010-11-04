Selectors.RegExps.combined = (/\.([\w-]+)|\[([\w-]+)(?:([!*^$~|]?=)(["']?)([^\4]*?)\4)?\]|:([\w-]+)(?:\(["']?(.*?)?["']?\)|$)/g);

describe('PartialUpdate', function(){

	var makeTable = function(id, howbig, randomize){
		var table = '<table id="tbl' + id + '"><tbody data-partial-container-id="tbl">';
		var rows = [];
		howbig.times(function(i){
			rows.push('<tr data-partial-line-id="tr' + i + '"><td data-partial-id="tr' + i + 'td1">tbl' + id + ' tr' + i + ' td1</td><td data-partial-id="tr' + i + 'td2">tbl' + id + ' tr' + i + ' td2</td></tr>');
		});
		if (randomize) rows.shuffle();
		table += rows.join('');
		table += '</tbody></table>';
		return Elements.from(table)[0];
	};

	var table1 = makeTable(1, 2);
	var table2 = makeTable(2, 2);
	var table3 = makeTable(3, 3);
	//remove item 1
	table3.getElements('tr')[1].dispose();
	//move item 2 to be before item 0 (2,0)
	table3.getElements('tr')[1].injectBefore(table3.getElements('tr')[0]);
	var table4 = makeTable(4, 3);
	//move item 2 before item 0 (2,0,1)
	table4.getElements('tr')[2].injectBefore(table4.getElements('tr')[0]);
	//move item 2 before item 1 (2,1,0)
	table4.getElements('tr')[2].injectBefore(table4.getElements('tr')[1]);

	var bigtable = makeTable(1, 1000);
	var bigtable2 = makeTable(2, 1000);
	var bigtable3 = makeTable(3, 1050, true);

	var div = Elements.from('<div><p data-partial-id="foo">foo</p></div>')[0];
	var div2 = Elements.from('<div><p data-partial-id="foo">bar</p></div>')[0];

	var table = table1.clone(true, true);

	var updater = new PartialUpdate(table.getElement('tbody'), {
		updateClass: '',
		updateClassToRemove: ''
	});

	var single = new PartialUpdate.Single(div.getElement('[data-partial-id]'), {
		updateClass: '',
		updateClassToRemove: ''
	});

	var bigTclone = bigtable.clone(true, true);
	var bigUp = new PartialUpdate(bigTclone.getElement('tbody'), {
		updateClass: '',
		clone: true,
		updateClassToRemove: ''
	});

	var test = function(tbl, up){
		up = up || updater;
		var tbody = tbl.getElement('tbody').clone(true, true);
		up.update(tbody);
		expect(document.id(up).innerHTML).toEqual(tbl.getElement('tbody').innerHTML);
		//dbug.log('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~');
	};
	
	it('Should initialize PartialUpdate', function(){
		expect(updater.partials.tr0td1.html).toEqual('tbl1 tr0 td1');
	});

	it('Should update a PartialUpdate instance', function(){
		//dbug.log('Should update a PartialUpdate instance');
		test(table2);
		expect(updater._sortCount).toEqual(0);
	});
	
	it('Should update and sort elements in a PartialUpdate instance', function(){
		//dbug.log('Should update and sort elements in a PartialUpdate instance');
		test(table3);
		expect(updater._sortCount).toEqual(1);
	});
	
	it('Should update and add elements in a PartialUpdate instance', function(){
		//dbug.log('Should update and add elements in a PartialUpdate instance');
		test(table4);
		expect(updater._sortCount).toEqual(1);
	});

	it('Should update and remove elements in a PartialUpdate instance', function(){
		//dbug.log('Should update and remove elements in a PartialUpdate instance');
		test(table1);
		expect(updater._sortCount).toEqual(1);
	});

	it('Should initialize a PartialUpdate.Single', function(){
		expect(single.html).toEqual('foo');
	});

	it('Should update a PartialUpdate.Single', function(){
		single.update(div2.clone(true, true));
		expect(single.html).toEqual('bar');
	});

	it('Should update a PartialUpdate instance with 1000 rows (benchmark)', function(){
		//dbug.log('Should update a PartialUpdate instance with 1000 rows (benchmark)');
		test(bigtable2, bigUp);
		expect(bigUp._sortCount).toEqual(0);
	});

	it('Should update *and sort* a PartialUpdate instance with 1000 rows (benchmark)', function(){
		//dbug.log('Should update *and sort* a PartialUpdate instance with 1000 rows (benchmark)');
		test(bigtable3, bigUp);
		expect(bigUp._sortCount).toBeGreaterThan(0);
	});

});