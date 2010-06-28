
Protovis.Line = new Class({
	
	Extends : Protovis,
	
	options : {
		lineWidth : 1,
		interactive : true,
		xvis : 'this.index > 0',
		xprecision: 0,
		yvis : '!(this.index % 2)',
		yprecision : 0
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
		if(len < 1) return;
		// initialize sub arrays
		for(var l = 0; l < len; l++) this.data[l] = [];
 		// build line data
		for(var i = 0; i < d.length; i++){
			for(var l = 1; l <= len; l++){
				this.data[l-1].push({'x' : parseFloat(d[i][0]), 'y': parseFloat(d[i][l])});
				x.push(d[i][0]); y.push(d[i][l]);
			}
		}
		this.limits = { xmin : pv.min(x), xmax : pv.max(x), ymin : pv.min(y), ymax : pv.max(y) };
	},
	
	setScale : function(){
		this.parent();	
		this.x = pv.Scale.linear(this.limits.xmin,Math.ceil(this.limits.xmax)).range(0,this.width);
		this.y = pv.Scale.linear(this.limits.ymin,Math.ceil(this.limits.ymax)).range(0,this.height);
	},
	
	makeGraph : function(){
		this.parent();
		this.addYTicks();
		this.addXTicks();
		this.makePanel();
		this.plot();
		if(this.options.interactive) this.makeInteractive();
	},
	
	addYTicks : function(){
		this.yTicks = this.graph.add(pv.Rule)
			.data(this.y.ticks())
			.visible(function(){ return !(this.index % 2);})
			.bottom(function(d) { return Math.round(this.y(d)) - .5}.bind(this))
			.strokeStyle(function(d){ return d ? "#ddd" : "#000";})
			.anchor("left").add(pv.Label)
			.text(function(d){ return d.toFixed(this.options.yprecision);  }.bind(this));	
	},
	
	addXTicks : function(){
		this.xTicks = this.graph.add(pv.Rule);
			this.xTicks
		    .data(this.x.ticks())
		    .visible(function(d){ return this.index > 0; })
		    .left(function(d){ return Math.round(this.x(d)) - .5 }.bind(this))
		    .strokeStyle(function(d){ return d ? "#ddd" : "#000"; })
		    .anchor("bottom").add(pv.Label)
			.text(function(d){ return d.toFixed(this.options.xprecision); }.bind(this));
	},
	
	plot : function(){
		this.line = this.panel.add(pv.Line)
			.data(function(d){ return d;})
			.left(function(d){ return this.x(d.x);}.bind(this))
			.bottom(function(d){ return this.y(d.y);}.bind(this))
			.lineWidth(this.options.lineWidth);
	},
	
	makeInteractive : function(){
			this.idx = -1;
			/* The mouseover dots and label. */
			this.line.add(pv.Dot)
			    .visible(function(){ return this.idx >= 0 }.bind(this))
			    .data(function(d){ return [d[this.idx]] }.bind(this))
			    .fillStyle(function(){ return this.line.strokeStyle(); }.bind(this))
			    .strokeStyle("#000")
			    .size(20) 
			    .lineWidth(1)
			  .add(pv.Dot)
			    .left(10)
			    .bottom(function(){ return (this.parent.index * 12 + 10); })
			  .anchor("right").add(pv.Label)
			    .text(function(d){ return d.y.toFixed(2); });

			/* An invisible bar to capture events (without flickering). */
			this.graph.add(pv.Bar)
			    .fillStyle("rgba(0,0,0,.001)")
			    .event("mouseout", function() {
			        this.idx = -1;
			        return this.graph;
			      }.bind(this))
			    .event("mousemove", function() {
			        var mx = this.x.invert(this.graph.mouse().x);
			        this.idx = pv.search(this.data[0].map(function(d){return d.x }), mx);
			        this.idx = this.idx < 0 ? (-this.idx - 2) : this.idx;
			        return this.graph;
			      }.bind(this));						
		
	}
	
	
});
