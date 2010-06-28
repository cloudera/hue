FitText
=======

![FitText](http://github.com/rpflorence/FitText/raw/master/Assets/logo.png)

Truncates the text nodes of elements to fit inside a container

How to use
----------

### Example:

#### HTML:

    #HTML
    <ul id="container">
    	<li><span>Lorem ipsum dolor</span></li>
    	<li><span>sit amet, consectetur adipisicing</span></li>
    	<li><span>elit, sed do eiusmod tempor incididunt ut labore et</span></li>
    </ul>

#### CSS:

    #CSS
    ul {
    	list-style: none;
    	width: 50%;
    }

    li {
    	white-space: nowrap;
    }
    
#### JavaScript

    #JS
    var myFitText = new FitText('container','li > span',{
      offset: 20,
      fitClass: 'fitted'
    });
    
View the [MooDoc](http://moodocs.net/rpflo/mootools-rpflo/FitText) for usage and examples.
