window.addEvent('load',function(){

	var fit = new FitText('container','li > span',{
		offset: 40,
		fitClass: 'red'
	});

	$('attachment').addEvent('click',function(){
		if(this.get('text') == 'Detach') {
			fit.detach();
			this.set('text','Attach');
		} else {
			fit.attach().fit();
			this.set('text','Detach');
		}
	});

	$('reset').addEvent('click',function(){
		fit.reset();
	});

	$('fit').addEvent('click',function(){
		fit.fit();
	});
	
});