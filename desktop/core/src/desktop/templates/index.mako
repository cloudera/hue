## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"> 
<html>
<head>
	<meta http-equiv="X-UA-Compatible" content="IE=8" />
	<title>Hue</title>
	<link rel="shortcut icon" href="/static/art/favicon_solid.png" type="image/x-icon" /> 
	<link rel="icon" href="/static/art/favicon_solid.png" type="image/x-icon" />
	<link rel="stylesheet" href="/static/css/shared.css" type="text/css" media="screen" title="no title" charset="utf-8">
	<link rel="stylesheet" href="/static/css/reset.css" type="text/css" media="screen" charset="utf-8">
	<link rel="stylesheet" href="/static/css/windows.css" type="text/css" media="screen" charset="utf-8">
	<link rel="stylesheet" href="/static/css/desktop.css" type="text/css" media="screen" charset="utf-8">

  <script src="/depender/build?client=true&require=ccs-shared/CCS.Request,ccs-shared/CCS.User,ccs-shared/CCS.Desktop,ccs-shared/CCS.Desktop.Config,ccs-shared/CCS.Desktop.FlashMessage,ccs-shared/CCS.Desktop.Keys,ccs-shared/CCS.Login,More/Fx.Elements"></script>
  <!--[if IE 8]>
      <script>
          window.ie8 = true;
      </script>
  <![endif]-->
  <script>
  
  window.addEvent('domready', function(){
    //this method automatically sizes the desktop image to fill the screen
    var sizer = function(){
      //get the backgrounds (there may be more than one if rotation is in process)
      var bgs = $('bg').getElements('.desktop-bg');
      //get the window dimensions
      var size = window.getSize();
      //if the aspect ratio of the window is > 1.6
      if (size.x/size.y > 1.6) {
        //then set the width of the image to equal the window
        bgs.setStyles({
          width: size.x,
          height: 'auto'
        });
      } else {
        //else set the height to match the window
        bgs.setStyles({
          width: 'auto',
          height: size.y
        });
      }
    };
    //when the window is resized, resize the background
    window.addEvent('resize', sizer);
    
    if (Browser.Engine.trident) {
      $('closeWarning').addEvent('click', function(){
        Cookie.write('desktop-browser-warned', true);
        $(document.body).removeClass('warned');
      });
      if (!Cookie.read('desktop-browser-warned')) $(document.body).addClass('warned');
      if (!ie8) alert("Hue does not currently support any version of Internet Explorer other than IE8.");
    }
    var appName = "Hue";
    //before fading in the screen, resize the background to match the window size
    sizer();
    var bgEls = $('bg').getElements('img');
    bgEls.push($('bg'));
    var styles = {};
    bgEls.each(function(el, i){
      styles[i.toString()] = { opacity: [0, 1] };
    });
    new Fx.Elements(bgEls, {
      duration: 500
    }).start(styles);
    $(document.body).addEvent('click:relay(img.desktop-logo)', rotateBG);
    
    Clientcide.setAssetLocation("/static/js/ThirdParty/clientcide/Assets");
    var growled = {};
    var launchGrowl = function(component){
      var appName = CCS.Desktop.getAppName(component);
      var loading = 'Loading ' + appName;
      var launching = 'Launching ' + appName;
      var msg = loading;
      if (CCS.Desktop.hasLoaded(component)) msg = launching;
      if (!CCS.Desktop.checkForFlashMessage(loading) && 
          !CCS.Desktop.checkForFlashMessage(launching) && 
          !$$('.loadingmsg').length) {
            growled[component] = CCS.Desktop.flashMessage(msg, 10000);
      }
    };
    var clearGrowl = function(component) {
      if (growled[component]) {
        growled[component]();
        delete growled[component];
      }
    };
    CCS.Desktop.initialize({
      onBeforeLoad: launchGrowl,
      onBeforeLaunch: launchGrowl,
      onAfterLaunch: clearGrowl
    });

    (function(){
      $('ccs-loading').fade('out').get('tween').clearChain().chain(function(){
        $('ccs-loading').destroy();
      });
    }).delay(300);

    //when the user logs in
    CCS.User.withUser(function(user){
      var bsLoaded;
      var bootstrapped = function(){
        if (bsLoaded) return;
        bsLoaded = true;

        //if there's no desktop to restore
        var linked = CCS.Desktop.launchLinked();
        // If a link was opened it chooses how to restore the desktop
        var restored;

        //we need to delay this slightly for IE; don't ask me why
        var finalize = function(){
          if (!linked) {
            //this is how we hide things in IE because it hates opacity/visibility stuff w/ VML
            $('ccs-desktop').setStyle('top', -10000);
            restored = CCS.Desktop.restoreDesktop();
            $('ccs-desktop').setStyle('top', null);
          }
          if (!linked && !restored) {
            //call the autolaunchers
            CCS.Desktop.autolaunchers.each(function(fn){
              fn();
            });
          }
          $('ccs-profileLink').set('text', user.username).addClass('loggedIn');
          $(document.body).addClass('ccs-loaded');
          window.scrollTo(0,0);
          $('ccs-toolbar').show().tween('opacity', 0, 1);
          $('ccs-dock').tween('opacity', 0, 1);
        };

        if (Browser.Engine.trident) finalize.delay(100);
        else finalize();
      };

      new Element('script', {
        src: '/bootstrap.js',
        events: {
          load: function() {
            bootstrapped();
          },
          readystatechange: function(){
            if (['loaded', 'complete'].contains(this.readyState)) bootstrapped();
          }
        }
      }).inject(document.head);
    });
  });
  </script>

  <script>
    % if send_dbug_messages:
      window.sendDbug = true;
    % else:
      window.sendDbug = false;
    % endif
  </script>
</head>
<body>
  <div id="bg">
    <script>
      (function(){
        var NUMBER_OF_BACKGROUNDS = 13; //number of backgrounds in /static/art/desktops
        var r = $random(1, NUMBER_OF_BACKGROUNDS);
        //inject a random background
        document.write('<img src="/static/art/desktops/' + r + '.jpg" class="desktop-bg"><img src="/static/art/desktops/' + r + '.logo.png" class="desktop-logo">');
        //background rotation function
        this.rotateBG = function(){
          //grab the images there now
          var bg = $('bg').getElement('.desktop-bg');
          var logo = $('bg').getElement('.desktop-logo');
          //pick a new random one
          if (r < NUMBER_OF_BACKGROUNDS) r++;
          else r = 1;
          //inject them
          new Element('img', {
            src: '/static/art/desktops/' + r + '.logo.png',
            'class': 'desktop-logo'
          }).inject($('bg'), 'top');
          new Element('img', {
            src: '/static/art/desktops/' + r + '.jpg',
            'class': 'desktop-bg',
            styles: bg.getStyles('width', 'height'),
            events: {
              load: function(){
                //after they load, crossfade
                new Fx.Elements([bg, logo], {duration: 500}).start({
                  '0': {
                    'opacity': 0
                  },
                  '1': {
                    'opacity': 0
                  }
                }).chain(function(){
                  bg.destroy();
                  logo.destroy();
                });
              }
            }
          }).inject($('bg'), 'top');
        };
      })();
    </script>
  </div>
  <div id="browserWarn">Hue is best experienced in <a target="browsers" href="http://getfirefox.com">Mozilla Firefox</a>, <a target="browsers" href="http://www.apple.com/safari/">Apple Safari</a>, or <a target="browsers" href="http://www.google.com/chrome">Google Chrome</a> <a id="closeWarning"></a></div>
  <div id="ccs-desktop" class="ccs-shared">
    <div id="ccs-topnav">
      <div id="ccs-toolbar">
        <img src="/static/art/favicon.png" width="16" height="16" class="ccs-swoosh">
        <span>
          Hi
          <span id="ccs-profileLink"></span>

          <span id="ccs-logout">
            [<a href="/accounts/logout">logout</a>]
          </span>
        </span>
        <a id="hotkeys" title="show keyboard shortcuts">
          <img src="/static/art/shortcut.png"> Shortcuts
        </a>
      </div>
    </div>
    <div id="ccs-dock">
      <div id="ccs-dock-content">
        <div id="ccs-dock-status" class="ccs-inline">
          <div id="ccs-dock-status-content">
          </div>
        </div>
        <span id="ccs-dock-icons">
        </span>
      </div>
    </div>
    <div id="ccs-loading">Launching Hue</div>
    <a id="ccs-feedback" href="${feedback_url}" target="_blank"><img src="/static/art/feedback-tab.png" width="76" height="26"/></a>
  </div>
  <div class="alert_popup ccs-error-popup">
    Warning, an AJAX request was made for the Hue desktop which cannot be loaded into an application window. Typically this means that a link clicked has no <em>href</em> value. Please notify the application's author.
  </div>

    <script>
      if (Browser.Engine.trident) $(document.body).addClass('IEroot');
      $(document.body).addClass(Browser.Engine.name);
    </script>
</body>
</html>
