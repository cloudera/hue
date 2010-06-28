Protovis.Bar = new Class({
	
	Extends : Protovis,
	
	options : {
		
	},
	
	initialize : function(el,options){
		this.parent(el,options);
		this.prepData();
		this.setScale();
		this.makeGraph();
		this.render();
	},
	
	prepData : function(){
		this.data = []; var d = this.options.data, x = [], y = [];
		var len = d[0].length - 1;
		
		for(var i = 0; i < d.length; i++){
			this.data.push( parseFloat(d[i][0]) );
			x.push(parseFloat(d[i][0])); 
		}
		this.limits = { xmin : pv.min(x), xmax : pv.max(x), ymin : 0, ymax: x.length};
	},
	
	setScale : function(){
		this.parent();
		this.x = pv.Scale.linear(this.limits.xmin,Math.ceil(this.limits.xmax)).range(0,this.width);
		this.y = pv.Scale.ordinal(pv.range(this.limits.ymax)).splitBanded(0,this.height, 4/5);
	},
	
	makeGraph : function(){
		this.parent();
		this.addYTicks();
		this.addXTicks();
		this.makePanel();
		this.plot();
	},
	
	addYTicks : function(){
	},
	
	addXTicks : function(){
		this.xTicks = this.graph.add(pv.Rule)
			.data(this.x.ticks())
			.left(function(d){ return Math.round(this.x(d)) - .5; }.bind(this))
			.strokeStyle(function(d){ return d ? '#ddd' : '#000'; })
			.add(pv.Rule)
			.bottom(0)
			.height(5)
			.strokeStyle("#000")
			.anchor("bottom").add(pv.Label)
	},
	
	plot : function(){
		this.bar = this.graph.add(pv.Bar)
			.data(this.data)
			.height(this.y.range().band)
			.top(function(scope){ return this.y(scope.index); }.bind(this,this.bar))
			.left(0)
			.width(this.x);
		this.bar.anchor("right").add(pv.Label)
			.textStyle("white")
			
	}
	
	
});