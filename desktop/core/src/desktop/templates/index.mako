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

  <script src="/depender/build?client=true&require=dbug,DomReady,Cookie"></script>
  <!--[if IE 8]>
      <script>
          window.ie8 = true;
      </script>
  <![endif]-->
  <script>
  
  window.addEvent('domready', function(){
    if (Browser.Engine.trident) {
      $('closeWarning').addEvent('click', function(){
        Cookie.write('desktop-browser-warned', true);
        $(document.body).removeClass('warned');
      });
      if (!Cookie.read('desktop-browser-warned')) $(document.body).addClass('warned');
      if (!ie8) alert("Hue does not currently support any version of Internet Explorer other than IE8.");
    }
    var appName = "Hue";
    Depender.require({
      scripts: ["CCS.Request", "CCS.User", "CCS.Desktop", "CCS.Desktop.Config", "CCS.Desktop.FlashMessage", "CCS.Desktop.Keys", "CCS.Login", "StickyWin.PointyTip", "Element.Delegation", "Fx.Tween", "Fx.Elements"],
      callback: function(){
        $('bg').set('tween', {duration:500}).tween('opacity', 0, 1);
        $(document.body).addEvent('click:relay(img.desktop-logo)', rotateBG);
        rotateBG.periodical(300000); //rotate the background every 5 min
        
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
      }
    });
  });
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

    <script>
      if (Browser.Engine.trident) $(document.body).addClass('IEroot');
    </script>
</body>
</html>
