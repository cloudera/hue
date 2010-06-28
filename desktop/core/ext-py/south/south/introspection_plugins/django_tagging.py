from south.modelsinspector import add_introspection_rules

try:
    from tagging.fields import TagField
except ImportError:
    pass
else:
    rules = [
        (
            (TagField, ),
            [],
            {
                "blank": ["blank", {"default": True}],
                "max_length": ["max_length", {"default": 255}],
            },
        ),
    ]

    add_introspection_rules(rules, ["^tagging\.fields",])
