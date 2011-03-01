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
/*
---
description: Hue namespace, (deprecated) Hue namespace + the base requirements for loading the Hue.
provides: [DesktopLoader]
requires: [
  Core/Cookie,
  Core/DomReady,
  Core/Element.Event,
  Core/Element.Dimensions,
  Core/Element.Style,
  Core/Fx.Tween,
  Core/Request.HTML,
  Core/Selectors,
  More/Element.Delegation,
  More/HtmlTable.Resize,
  More/Spinner,
  More/URI,
  clientcide/dbug,
  clientcide/Clientcide,
  clientcide/StickyWin,
  clientcide/StickyWin.PointyTip,
  Widgets/ART.Popup,
  JFrame/JFrame.Browser,
  JFrame/FlashMessage,
  JFrame/JFrame.Keys,
  JFrame/MooTools.Config,
  hue-shared/Hue,
  hue-shared/Hue.Desktop.BackgroundManager,
  hue-shared/Hue.Desktop.Config,
  hue-shared/Hue.JFrame.Target,
  hue-shared/Hue.Login,
  hue-shared/Hue.Profiler,
  hue-shared/Hue.Request,
  hue-shared/Hue.User,
  hue-shared/CCS.JFrame, #These CCS.* files are all just deprecated namespaces; here for backwards compat
  hue-shared/CCS.JFrame.DeprecatedFilters,
  hue-shared/CCS.JBrowser,
  hue-shared/CCS.Desktop.FlashMessage,
]
script: Hue.js

...
*/