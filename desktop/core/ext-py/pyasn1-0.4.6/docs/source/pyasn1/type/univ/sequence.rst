
.. _univ.Sequence:

.. |ASN.1| replace:: Sequence

|ASN.1| type
------------

.. autoclass:: pyasn1.type.univ.Sequence(componentType=NamedTypes(), tagSet=tagSet(), subtypeSpec=ConstraintsIntersection(), sizeSpec=ConstraintsIntersection())
   :members: isValue, isSameTypeWith, isSuperTypeOf, tagSet, effectiveTagSet, tagMap, componentType, subtypeSpec, sizeSpec, getComponentByPosition,
             setComponentByPosition, getComponentByName, setComponentByName, setDefaultComponents,
             clear, reset

   .. note::

        The |ASN.1| type models a collection of named ASN.1 components.
        Ordering of the components **is** preserved upon de/serialisation.

   .. automethod:: pyasn1.type.univ.Sequence.clone(componentType=NamedTypes(), tagSet=tagSet(), subtypeSpec=ConstraintsIntersection())
   .. automethod:: pyasn1.type.univ.Sequence.subtype(componentType=NamedTypes(), implicitTag=Tag(), explicitTag=Tag(),subtypeSpec=ConstraintsIntersection())
