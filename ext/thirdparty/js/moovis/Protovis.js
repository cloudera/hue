
var Protovis = new Class({
	
	Implements : [Options],
	
	options : {
		data : [],
		width : 'auto',
		height : 'auto',
		bottom : 20,
		left : 20,
		right : 10,
		top : 5,
		colors : ['#9edae5', '#17becf', '#dbdb8d', '#bcbd22']
	},
	
	initialize : function(el,options){
		this.setOptions(options);
		this.el = el;
		pv.Panel.$dom = el;
	},
	
	setScale : function(){
		var size = this.el.getParent().getParent().getSize();
		if(this.options.width == 'auto' || this.options.height == 'auto'){
			this.width = size.x -5;
			this.height = size.y - 5;	
		} else {
			this.width = this.options.width;
			this.height = this.options.height;
		}
		this.width -= (this.options.left + this.options.right);
		this.height -= (this.options.top + this.options.bottom);
	},
	
	makeGraph : function(){
		this.graph = new pv.Panel()
			.width(this.width)
			.height(this.height)
			.bottom(this.options.bottom)
			.left(this.options.left)
			.right(this.options.right)
			.top(this.options.top);		
	},
	
	makePanel : function(){
		this.panel = this.graph.add(pv.Panel)
			.data(this.data);
	},
	
	refresh : function(options){
		this.setOptions(options);
		this.destroy();
		this.setScale();
		this.makeGraph();
		this.render();
	},
	
	render : function(){
		this.graph.render();
	},
	
	destroy : function(){
		$(this.el.getElement('svg').getParent()).dispose();
	}
	
	
});
