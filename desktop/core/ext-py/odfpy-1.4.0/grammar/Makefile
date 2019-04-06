all: odf grammarnew.py

#simplified-7-22.rng: OpenDocument-strict-schema-v1.2-draft7.rng OpenDocument-schema-v1.0-os.rng
#simple-schema-7-22.rng: OpenDocument-strict-schema-v1.0-os.rng OpenDocument-schema-v1.0-os.rng simplification.xsl
#simple-schema-7-22.rng: OpenDocument-strict-schema-v1.1.rng OpenDocument-schema-v1.1.rng simplification.xsl
simple-schema-7-22.rng: OpenDocument-v1.2-os-schema.rng simplification.xsl
	xsltproc --stringparam out-name simple-schema- simplification.xsl $<

simple-manifest-7-22.rng: OpenDocument-manifest-schema-v1.0-os.rng simplification.xsl
	xsltproc --stringparam out-name simple-manifest- simplification.xsl $<

grammarnew.py: allowed_children.py allows_text.py required_attrs.py allowed_attrs.py
	cat allowed_children.py allows_text.py required_attrs.py allowed_attrs.py >grammarnew.py

allowed_children.py: simple-schema-7-22.rng simple-manifest-7-22.rng gen_allowed_children.py
	python gen_allowed_children.py > allowed_children.py

allows_text.py: simple-schema-7-22.rng simple-manifest-7-22.rng gen_allows_text.py
	python gen_allows_text.py > allows_text.py

required_attrs.py: simple-schema-7-22.rng simple-manifest-7-22.rng simple-manifest-7-22.rng gen_required_attrs.py
	python gen_required_attrs.py > required_attrs.py

allowed_attrs.py: simple-schema-7-22.rng simple-manifest-7-22.rng gen_allowed_attrs.py
	python gen_allowed_attrs.py > allowed_attrs.py

clean:
	rm -f odf simple-schema-7-*.rng simple-manifest-7-*.rng \
	  required_attrs.py allowed_attrs.py allowed_children.py allows_text.py \
	  grammarnew.py

odf:
	ln -s ../odf
