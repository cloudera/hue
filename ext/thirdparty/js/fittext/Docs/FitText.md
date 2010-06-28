Class: FitText {#FitText}
=========================

<big>Truncates the text nodes of elements to fit inside a container</big>

<iframe src="http://mooshell.net/rpflo/FSPP4/embedded/result,js,html,css" style="width: 100%; height:450px"></iframe>


FitText Method: constructor {#FitText:constructor}
---------------------------------------------------


### Syntax:

	var myFitText = new FitText(container, elements, options);

### Arguments:

1. container - (`mixed`) A string of the id for an Element or an Element reference to contain the text nodes width.
2. elements - (`mixed`) A string of the selector for a group of Elements or an array of Elements to be truncated.
3. options - (`object`: optional) See below:

### Options:

* offset - (`number`: defaults to `10`) Subtracted from the container size to determine how long a line of text needs to be before truncating it.  If you have truncated text extending beyond your container, increase this number.
* fitClass - (`string`: defaulst to `truncated`) A CSS class name added to truncated elements.

### Example: 

#### HTML:

    <ul id="container">
    	<li><span>Lorem ipsum dolor</span></li>
    	<li><span>sit amet, consectetur adipisicing</span></li>
    	<li><span>elit, sed do eiusmod tempor incididunt ut labore et</span></li>
    </ul>

#### CSS:

    ul {
    	list-style: none;
    	width: 50%;
    }

    li {
    	white-space: nowrap;
    }
    
#### JavaScript

    var myFitText = new FitText('container','li > span',{
      offset: 20,
      fitClass: 'fitted'
    });
    
### Note:

Your `elements` must have have `display: inline` in order to work.

FitText Method: fit {#FitText:fit}
-----------------------------------

<big>Truncates all the elements to fit inside the container</big>

### Syntax:

    myFitText.fit();

### Returns:

This FitText instance.



FitText Method: attach {#FitText:attach}
-----------------------------------------

<big>Attaches a `resize` event to the window, upon which the method `fit` is called.</big>

### Syntax:

    myFitText.attach();

### Returns:

This FitText instance.



FitText Method: detach {#FitText:detach}
-----------------------------------------

<big>Removes the `resize` event from the window.</big>

### Syntax:

    myFitText.detach();

### Returns:

This FitText instance.


FitText Method: reset {#FitText:reset}
---------------------------------------

<big>Sets the text nodes back to their original values.</big>

### Syntax:

    myFitText.reset();

### Returns:

This FitText instance.


