// (c) Copyright 2016 Cloudera, Inc. All Rights reserved
/**
 * @module ko/components/carousel
 */
import componentUtils from 'cloudera-ui/ko/components/componentUtils';
import modalLoader    from 'cloudera-ui/ko/components/modalLoader';
import eventTypes     from 'cloudera-ui/ko/components/eventTypes';
import pagebus        from 'cloudera-ui/utils/pagebus';
import $              from 'jquery';
import ko             from 'knockout';
import _              from '_';
import 'bootstrap/carousel';

var carouselTemplate = `
<div class="cui-carousel" style="width:300px; height: 200px;">
<div class="carousel slide" id="carousel-example-generic" data-ride="carousel">
<ol class="carousel-indicators">
  <li data-target="#carousel-example-generic" data-slide-to="0" class=""></li>
  <li data-target="#carousel-example-generic" data-slide-to="1" class=""></li>
  <li data-target="#carousel-example-generic" data-slide-to="2" class="active"></li>
</ol>
<div class="carousel-inner" role="listbox">
  <div class="item active"><div style="width: 300px; height: 200px">Item 1</div></div>
  <div class="item"><div style="width: 300px; height: 200px">Item 2</div></div>
  <div class="item"><div style="width: 300px; height: 200px">Item 3</div></div>
</div>
<a href="#carousel-example-generic" class="left carousel-control" role="button" data-slide="prev">
  <span class="glyphicon glyphicon-chevron-left" aria-hidden="true"></span>
  <span class="sr-only">Previous</span>
</a>
<a href="#carousel-example-generic" class="right carousel-control" role="button" data-slide="next">
  <span class="glyphicon glyphicon-chevron-right" aria-hidden="true"></span>
  <span class="sr-only">Next</span>
</a>
</div>`;

class Carousel {
  constructor() {
  }
}

var COMPONENT_NAME = 'cui-carousel';

componentUtils.addComponent(Carousel, COMPONENT_NAME, carouselTemplate);

module.exports = Carousel;
