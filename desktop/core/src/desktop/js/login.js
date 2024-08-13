// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import 'regenerator-runtime/runtime';
import 'jquery/jquery.login';
import 'ext/bootstrap.2.3.2.min';
import Dropzone from 'dropzone';
import hueAnalytics from 'utils/hueAnalytics';
import huePubSub from 'utils/huePubSub';
window.Dropzone = Dropzone;
window.hueAnalytics = hueAnalytics;
window.huePubSub = huePubSub;

import { createApp } from 'vue';
import TrademarkBanner from 'vue/components/login/TrademarkBanner.vue';
import { createReactComponents } from './reactComponents/createRootElements';

window.addEventListener('DOMContentLoaded', () => {
  createReactComponents('.login-page');
  $("form").on("submit", function () {
    console.log("test1");
    window.setTimeout(function () {
      $(".logo").find("img").addClass("waiting");
    }, 1000);
  });

  $(document).keypress(function (event) {
    console.log("test2");
      var keycode = event.keyCode ? event.keyCode : event.which;
      if(keycode == '13') {
        console.log("test3");
        $("[type=submit]").click();
      }
  });

  var loginData = document.getElementById('login-data');
  var backendNames = JSON.parse(loginData.getAttribute('data-backend-names'));
  var nextUrl = JSON.parse(loginData.getAttribute('data-next-url'));

  console.log("test4");
  console.log(loginData);
  debugger;
  if (backendNames.includes('AllowAllBackend')) {
    document.getElementById('id_password').value = 'password';
  }

  if (backendNames.length === 1 && backendNames[0] === 'OAuthBackend') {
    var inputs = document.querySelectorAll("input");
    inputs.forEach(function(input) {
      input.style.display = 'block';
      input.style.marginLeft = 'auto';
      input.style.marginRight = 'auto';
      input.addEventListener('click', function () {
        window.location.replace('/login/oauth/');
        return false;
      });
    });
  }

  if (nextUrl) {
    var redirectInput = document.querySelector('input[name="next"]');
    redirectInput.value = redirectInput.value + window.location.hash;
  }

  createApp({
    components: {
      'trademark-banner': TrademarkBanner
    },
    data: () => ({})
  }).mount('#trademark');
});
