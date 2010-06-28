# Protovis Makefile
#
# Note: This Makefile depends on the YUI Compressor for JavaScript
# minification. The JAR file should be installed in the lib directory.
# The YUI Compressor is available at http://yuilibrary.com/downloads/

JS_LANG_FILES = \
	js/lang/Array.js \
	js/lang/Date.js

JS_PV_FILES = \
	js/pv.js \
	js/data/Tree.js \
	js/data/Nest.js \
	js/data/Flatten.js \
	js/data/Vector.js \
	js/data/Scale.js \
	js/data/LinearScale.js \
	js/data/LogScale.js \
	js/data/OrdinalScale.js \
	js/color/Color.js \
	js/color/Colors.js \
	js/color/Ramp.js \
	js/scene/SvgScene.js \
	js/scene/SvgArea.js \
	js/scene/SvgBar.js \
	js/scene/SvgDot.js \
	js/scene/SvgImage.js \
	js/scene/SvgLabel.js \
	js/scene/SvgLine.js \
	js/scene/SvgPanel.js \
	js/scene/SvgRule.js \
	js/scene/SvgWedge.js \
	js/mark/Mark.js \
	js/mark/Anchor.js \
	js/mark/Area.js \
	js/mark/Bar.js \
	js/mark/Dot.js \
	js/mark/Label.js \
	js/mark/Line.js \
	js/mark/Rule.js \
	js/mark/Panel.js \
	js/mark/Image.js \
	js/mark/Wedge.js \
	js/layout/Layout.js \
	js/layout/Grid.js \
	js/layout/Stack.js \
	js/layout/Icicle.js \
	js/layout/Sunburst.js \
	js/layout/Treemap.js

JS_FILES = \
	$(JS_LANG_FILES) \
	js/pv-start.js \
	$(JS_PV_FILES) \
	js/pv-end.js 
# not needed because this is used for function expressions support (ugly eval).	HUE CHANGE
#	js/lang/init.js     

all: protovis-d3.1.js protovis-r3.1.js

protovis-d3.1.js: $(JS_FILES) Makefile
	grep '	' -Hn $(JS_FILES) && echo "ERROR: tab" && exit 1 || true
	grep '' -Hn $(JS_FILES) && echo "ERROR: dos newline" && exit 1 || true
	grep ' $$' -Hn $(JS_FILES) && echo "ERROR: trailing space" && exit 1 || true
	cat $(JS_FILES) > $@

protovis-r3.1.js: protovis-d3.1.js
	rm -f $@
	cat $(JS_LANG_FILES) | java -jar lib/yuicompressor-2.4.2.jar --charset UTF-8 --type js >> $@
	cat js/pv-start.js >> $@
	cat $(JS_PV_FILES) | java -jar lib/yuicompressor-2.4.2.jar --charset UTF-8 --type js >> $@
	cat js/pv-end.js >> $@
	cat js/lang/init.js | java -jar lib/yuicompressor-2.4.2.jar --charset UTF-8 --type js >> $@

clean:
	rm -rf protovis-d3.1.js protovis-r3.1.js

