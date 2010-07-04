JS_LANG_FILES = \
	src/lang/Array.js

JS_CORE_FILES = \
	src/pv.js \
	src/pv-internals.js \
	src/lang/init.js \
	src/text/Format.js \
	src/text/DateFormat.js \
	src/text/TimeFormat.js \
	src/text/NumberFormat.js \
	src/data/Arrays.js \
	src/data/Numbers.js \
	src/data/Objects.js \
	src/data/Dom.js \
	src/data/Tree.js \
	src/data/Nest.js \
	src/data/Flatten.js \
	src/data/Vector.js \
	src/data/Transform.js \
	src/data/Scale.js \
	src/data/QuantitativeScale.js \
	src/data/LinearScale.js \
	src/data/LogScale.js \
	src/data/RootScale.js \
	src/data/OrdinalScale.js \
	src/data/QuantileScale.js \
	src/data/Histogram.js \
	src/color/Color.js \
	src/color/Colors.js \
	src/color/Ramp.js \
	src/scene/svg/SvgScene.js \
	src/scene/svg/SvgCurve.js \
	src/scene/svg/SvgArea.js \
	src/scene/svg/SvgBar.js \
	src/scene/svg/SvgDot.js \
	src/scene/svg/SvgImage.js \
	src/scene/svg/SvgLabel.js \
	src/scene/svg/SvgLine.js \
	src/scene/svg/SvgPanel.js \
	src/scene/svg/SvgRule.js \
	src/scene/svg/SvgWedge.js \
	src/scene/vml/VmlScene.js \
	src/scene/vml/VmlArea.js \
	src/scene/vml/VmlBar.js \
	src/scene/vml/VmlDot.js \
	src/scene/vml/VmlImage.js \
	src/scene/vml/VmlLabel.js \
	src/scene/vml/VmlLine.js \
	src/scene/vml/VmlPanel.js \
	src/scene/vml/VmlRule.js \
	src/scene/vml/VmlWedge.js \
	src/scene/Scene.js \
	src/mark/Mark.js \
	src/mark/Anchor.js \
	src/mark/Area.js \
	src/mark/Bar.js \
	src/mark/Dot.js \
	src/mark/Label.js \
	src/mark/Line.js \
	src/mark/Rule.js \
	src/mark/Panel.js \
	src/mark/Image.js \
	src/mark/Wedge.js

JS_LAYOUT_FILES = \
	src/physics/Particle.js \
	src/physics/Simulation.js \
	src/physics/Quadtree.js \
	src/physics/Force.js \
	src/physics/ChargeForce.js \
	src/physics/DragForce.js \
	src/physics/SpringForce.js \
	src/physics/Constraint.js \
	src/physics/CollisionConstraint.js \
	src/physics/PositionConstraint.js \
	src/physics/BoundConstraint.js \
	src/layout/Layout.js \
	src/layout/Network.js \
	src/layout/Hierarchy.js \
	src/layout/Grid.js \
	src/layout/Stack.js \
	src/layout/Treemap.js \
	src/layout/Tree.js \
	src/layout/Indent.js \
	src/layout/Pack.js \
	src/layout/Force.js \
	src/layout/Cluster.js \
	src/layout/Partition.js \
	src/layout/Arc.js \
	src/layout/Horizon.js \
	src/layout/Rollup.js \
	src/layout/Matrix.js \
	src/layout/Bullet.js \
	src/behavior/Behavior.js \
	src/behavior/Drag.js \
	src/behavior/Point.js \
	src/behavior/Select.js \
	src/behavior/Resize.js \
	src/behavior/Pan.js \
	src/behavior/Zoom.js

JS_GEO_FILES = \
	src/geo/Geo.js \
	src/geo/LatLng.js \
	src/geo/Projection.js \
	src/geo/Projections.js \
	src/geo/GeoScale.js

JS_FILES = \
	$(JS_LANG_FILES) \
	$(JS_CORE_FILES) \
	$(JS_LAYOUT_FILES) \
	$(JS_GEO_FILES)

JS_COMPILER = \
	java -jar lib/google-compiler/compiler-20100201.jar \
	--charset UTF-8 \
	--warning_level=QUIET

JSDOC_HOME = /Library/jsdoc-toolkit
JSDOC = java -jar $(JSDOC_HOME)/jsrun.jar $(JSDOC_HOME)/app/run.js

all: protovis-d3.2.js protovis-r3.2.js
protovis-d3.2.js: $(JS_FILES)
protovis-r3.2.js: $(JS_FILES)

%-d3.2.js: Makefile
	grep '	' -Hn $(filter %.js,$^) && echo "ERROR: tab" && exit 1 || true
	grep -P '\r\n' -Hn $(filter %.js,$^) && echo "ERROR: dos newline" && exit 1 || true
	grep ' $$' -Hn $(filter %.js,$^) && echo "ERROR: trailing space" && exit 1 || true
	rm -f $@
	echo "// $(shell git rev-parse HEAD)" >> $@
	cat $(filter %.js,$^) >> $@

%-r3.2.js:: Makefile
	rm -f $@
	echo "// $(shell git rev-parse --short HEAD)" >> $@
	cat $(filter %.js,$^) | $(JS_COMPILER) >> $@

jsdoc: $(JS_FILES) Makefile
	rm -rf jsdoc
	$(JSDOC) -a -t=$(JSDOC_HOME)/templates/jsdoc -d=$@ -E="^pv-" $(JS_FILES)

clean:
	rm -rf protovis-d3.2.js protovis-r3.2.js jsdoc
