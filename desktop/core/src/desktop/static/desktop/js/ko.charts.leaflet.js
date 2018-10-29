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

(function () {

  ko.bindingHandlers.leafletMapChart = {
    update: function (element, valueAccessor) {
      var _options = valueAccessor();
      var _data = _options.transformer(valueAccessor().datum);

      function toggleVisibility() {
        if (!_data.message && ((_options.visible != null && _options.visible) || _options.visible == null || typeof _options == "undefined")) {
          $(element).show();
          $(element).siblings(".leaflet-nodata").remove();
        }
        else {
          $(element).hide();
          if ((_data.message || (_options.visible != null && _options.visible)) && !_options.isLoading) {
            $(element).siblings(".leaflet-nodata").remove();
            $(element).before($("<div>").addClass("leaflet-nodata").css({ "textAlign": "center", "fontSize": "18px", "fontWeight": 700, "marginTop": "20px"}).text(_data.message || window.HUE_I18n.chart.noData));
          }
        }
      }

      if ($(element).data("mapData") == null || $(element).data("mapData") != ko.toJSON(_data) || _options.forceRedraw) {

        $(element).data("mapData", ko.toJSON(_data));

        var _hasAtLeastOneLat = false;
        _data.forEach(function (item) {
          if (item.lat != null && $.isNumeric(item.lat)) {
            _hasAtLeastOneLat = true;
          }
        });
        var _hasAtLeastOneLng = false;
        _data.forEach(function (item) {
          if (item.lng != null && $.isNumeric(item.lng)) {
            _hasAtLeastOneLng = true;
          }
        });

        if (_options.height != null) {
          $(element).height(_options.height * 1);
        }
        else {
          if ($(element).parents(".tab-pane").length > 0) {
            $(element).height($(element).parents(".tab-pane").height() - 100);
          }
          else {
            $(element).height(300);
          }
        }

        toggleVisibility();

        var _map = null;
        if ($(element).data('_map') != null) {
          _map = $(element).data('_map');
          _map.removeLayer($(element).data('_markerLayer'));
          if ($(element).data('_heatLayer')){
            _map.removeLayer($(element).data('_heatLayer'));
            $(element).data('_heatLayer', null);
          }
        }

        var _clusterGroup = L.markerClusterGroup({
          maxClusterRadius: 10,
          polygonOptions: {
            weight: 1.5
          }
        });

        if (_hasAtLeastOneLat && _hasAtLeastOneLng) {
          try {
            if (_map == null) {
              if (LEAFLET_DEFAULTS.mapOptions.crs) {
                LEAFLET_DEFAULTS.mapOptions.crs = L.CRS[LEAFLET_DEFAULTS.mapOptions.crs];
              }
              _map = L.map(element, LEAFLET_DEFAULTS.mapOptions);
              var tileLayerOptions = {
                layer: 'http://{s}.tile.osm.org/{z}/{x}/{y}.png',
                attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
              };
              if (LEAFLET_DEFAULTS.layer) {
                tileLayerOptions.layer = LEAFLET_DEFAULTS.layer;
              }
              if (LEAFLET_DEFAULTS.attribution) {
                tileLayerOptions.attribution = LEAFLET_DEFAULTS.attribution;
              }
              if (LEAFLET_DEFAULTS.layerOptions) {
                tileLayerOptions = $.extend(tileLayerOptions, LEAFLET_DEFAULTS.layerOptions);
              }
              L.tileLayer(tileLayerOptions.layer, tileLayerOptions).addTo(_map);

              if (L.control.zoomBox) {
                var _zoomBox = L.control.zoomBox({
                  modal: true
                });
                _map.addControl(_zoomBox);
              }

              if (_options.showMoveCheckbox) {
                var _command = L.control({
                  position: $(element).width() > 300 ? "topright" : "bottomleft"
                });

                _command.onAdd = function (map) {
                  var div = L.DomUtil.create("div", "leaflet-search-command leaflet-bar leaflet-move-label");
                  div.innerHTML = '<button id="command' + $(element).parents(".card-widget").attr("id") + '" type="button" class="btn btn-mini disable-feedback"><i class="fa fa-fw fa-square-o"></i> ' + (_options.moveCheckboxLabel ? _options.moveCheckboxLabel : 'Search as I move the map') + '</button>';
                  return div;
                };

                _command.addTo(_map);

                if (_options.onRegionChange == null) {
                  _options.onRegionChange = function () {
                  };
                }

                var _onRegionChange = function () {
                };

                $('#command' + $(element).parents('.card-widget').attr('id')).on('click', function (e) {
                  $(this).toggleClass('btn-primary');
                  $(this).find('.fa-fw').toggleClass('fa-check-square');
                  if ($(this).hasClass("btn-primary")) {
                    if (_options.onRegionChange != null) {
                      _onRegionChange = _options.onRegionChange;
                    }
                  }
                  else {
                    _onRegionChange = function () {
                    };
                  }
                });

                ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
                  $('#command' + $(element).parents('.card-widget').attr('id')).off('click');
                });

                _map.on("boxzoomend", function (e) {
                  _onRegionChange(e.boxZoomBounds);
                });
                _map.on("dragend", function () {
                  _onRegionChange(_map.getBounds());
                });
                _map.on("zoomend", function () {
                  _onRegionChange(_map.getBounds());
                });
                _map.on("viewreset", function(){
                  huePubSub.publish('leaflet.afterplot', element);
                });
              }

            }

            var heatData = [];

            function sumHeatData(data) {
              var sumData = [];
              data.forEach(function (d) {
                var found = false;
                if (d.length === 3) {
                  sumData.forEach(function (s) {
                    if (d[0] == s[0] && d[1] == s[1]) {
                      found = true;
                      s[2] += d[2];
                    }
                  });
                }
                if (!found) {
                  sumData.push(d);
                }
              });
              return sumData;
            }

            function getMaxIntensity(data) {
              var maxIntensity = 0;
              data.forEach(function (d) {
                if (d[2] > maxIntensity) {
                  maxIntensity = d[2];
                }
              });
              return maxIntensity;
            }

            _data.forEach(function (item) {
              if (item && item.lng != null && item.lat != null) {
                var _addMarker = false;
                try {
                  var _latLngObj = L.latLng(item.lat, item.lng);
                  _addMarker = true;
                }
                catch (e) {
                  if (typeof console != "undefined") {
                    console.error(e);
                  }
                }
                if (_addMarker) {
                  var _marker = L.marker([item.lat, item.lng]);
                  if (item.isHeat) {
                    if (item.intensity != null) {
                      heatData.push([item.lat, item.lng, item.intensity]);
                    }
                    else {
                      heatData.push([item.lat, item.lng]);
                    }
                  }
                  else {
                    if (item.label != null) {
                      _marker.bindPopup($.isArray(item.label) ? item.label.join("") : item.label);
                    }
                  }
                  _clusterGroup.addLayer(_marker);
                }
              }
            });
            var heat;
            if (heatData.length > 0) {
              heatData = sumHeatData(heatData);
              heat = L.heatLayer(heatData);
              if (heatData[0].length === 3) { // it has intensity
                heat.setOptions(getMaxIntensity(heatData));
              }
            }

            window.setTimeout(function () {
              if (!$("#command" + $(element).parents(".card-widget").attr("id")).is(":checked")) {
                _map.fitBounds(_clusterGroup.getBounds());
              }
              if ($(element).find('.leaflet-tile-pane').children().length > 0) {
                if (heatData.length == 0) {
                  _map.addLayer(_clusterGroup);
                  $('.leaflet-heatmap-layer').remove();
                }
                else {
                  try {
                    $('.leaflet-heatmap-layer').remove();
                    heat.addTo(_map);
                  }
                  catch (e) {
                  } // context2D not initialized yet
                }
              }
              if (_options.onComplete != null) {
                _options.onComplete();
              }
            }, 0);

            var resizeSubscription = huePubSub.subscribe('resize.leaflet.map', function () {
              if ($(element).data('_map')) {
                $(element).data('_map').invalidateSize();
                if ($(element).data('_markerLayer')) {
                  try {
                    $(element).data('_map').fitBounds($(element).data('_markerLayer').getBounds());
                  }
                  catch (e) {
                  }
                }
              }
            });

            ko.utils.domNodeDisposal.addDisposeCallback(element, function() {
              resizeSubscription.remove();
            });

          }
          catch (err) {
            $.jHueNotify.error(err.message);
          }
        }

        var previousMarkerLayer = $(element).data('_markerLayer');
        if (previousMarkerLayer) {
          window.setTimeout(function () {
            try {
              previousMarkerLayer.removeLayers(previousMarkerLayer.getLayers());
            }
            catch(e){}
          }, 0);
        }

        $(element).data('_map', _map);
        $(element).data('_markerLayer', _clusterGroup);
        $(element).data('_heatLayer', heat);
        if (_options.onComplete != null) {
          _options.onComplete();
        }
      }
      else {
        toggleVisibility();
      }
    }
  };

})();