Protovis.Pie = new Class({
	
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
		this.data = this.data.sort(pv.reverseOrder)
	},
	
	setScale : function(){
		this.parent();
		this.r = this.width / 2;
		this.angle = pv.Scale.linear(0, pv.sum(this.data)).range(0, 2 * Math.PI);	
		console.debug(this.data);
	},
	
	makeGraph : function(){
		this.parent();
		this.graph.add(pv.Wedge)
			.data(this.data)
			.bottom(this.height / 2)
			.left(this.width / 2)
			.outerRadius(this.r / 2.2)
			.angle(this.angle)
			.title(function(d){ return d.toFixed(2);})
			.add(pv.Wedge)
				.visible(function(d){ return d > .15; })
				.innerRadius(2 * this.r / 6.2)
				.outerRadius(this.r / 2.2)
				.fillStyle(null)
				.anchor("center").add(pv.Label)
					.textAngle(0)
					.text(function(d){ return d.toFixed(2); });
	}
	
})
