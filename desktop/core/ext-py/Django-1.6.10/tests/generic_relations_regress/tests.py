from django.db.models import Q
from django.db.utils import IntegrityError
from django.test import TestCase, skipIfDBFeature
from django.forms.models import modelform_factory
from django.db.models.deletion import ProtectedError

from .models import (
    Address, Place, Restaurant, Link, CharLink, TextLink,
    Person, Contact, Note, Organization, OddRelation1, OddRelation2, Company,
    Developer, Team, Guild, Tag, Board, HasLinkThing, A, B, C, D,
    Related, Content, Node,
)


class GenericRelationTests(TestCase):

    def test_inherited_models_content_type(self):
        """
        Test that GenericRelations on inherited classes use the correct content
        type.
        """

        p = Place.objects.create(name="South Park")
        r = Restaurant.objects.create(name="Chubby's")
        l1 = Link.objects.create(content_object=p)
        l2 = Link.objects.create(content_object=r)
        self.assertEqual(list(p.links.all()), [l1])
        self.assertEqual(list(r.links.all()), [l2])

    def test_reverse_relation_pk(self):
        """
        Test that the correct column name is used for the primary key on the
        originating model of a query.  See #12664.
        """
        p = Person.objects.create(account=23, name='Chef')
        Address.objects.create(street='123 Anywhere Place',
                               city='Conifer', state='CO',
                               zipcode='80433', content_object=p)

        qs = Person.objects.filter(addresses__zipcode='80433')
        self.assertEqual(1, qs.count())
        self.assertEqual('Chef', qs[0].name)

    def test_charlink_delete(self):
        oddrel = OddRelation1.objects.create(name='clink')
        CharLink.objects.create(content_object=oddrel)
        oddrel.delete()

    def test_textlink_delete(self):
        oddrel = OddRelation2.objects.create(name='tlink')
        TextLink.objects.create(content_object=oddrel)
        oddrel.delete()

    def test_q_object_or(self):
        """
        Tests that SQL query parameters for generic relations are properly
        grouped when OR is used.

        Test for bug http://code.djangoproject.com/ticket/11535

        In this bug the first query (below) works while the second, with the
        query parameters the same but in reverse order, does not.

        The issue is that the generic relation conditions do not get properly
        grouped in parentheses.
        """
        note_contact = Contact.objects.create()
        org_contact = Contact.objects.create()
        Note.objects.create(note='note', content_object=note_contact)
        org = Organization.objects.create(name='org name')
        org.contacts.add(org_contact)
        # search with a non-matching note and a matching org name
        qs = Contact.objects.filter(Q(notes__note__icontains=r'other note') |
                                    Q(organizations__name__icontains=r'org name'))
        self.assertTrue(org_contact in qs)
        # search again, with the same query parameters, in reverse order
        qs = Contact.objects.filter(
            Q(organizations__name__icontains=r'org name') |
            Q(notes__note__icontains=r'other note'))
        self.assertTrue(org_contact in qs)

    def test_join_reuse(self):
        qs = Person.objects.filter(
            addresses__street='foo'
        ).filter(
            addresses__street='bar'
        )
        self.assertEqual(str(qs.query).count('JOIN'), 2)

    def test_generic_relation_ordering(self):
        """
        Test that ordering over a generic relation does not include extraneous
        duplicate results, nor excludes rows not participating in the relation.
        """
        p1 = Place.objects.create(name="South Park")
        p2 = Place.objects.create(name="The City")
        c = Company.objects.create(name="Chubby's Intl.")
        Link.objects.create(content_object=p1)
        Link.objects.create(content_object=c)

        places = list(Place.objects.order_by('links__id'))
        def count_places(place):
            return len([p for p in places if p.id == place.id])

        self.assertEqual(len(places), 2)
        self.assertEqual(count_places(p1), 1)
        self.assertEqual(count_places(p2), 1)

    def test_target_model_is_unsaved(self):
        """Test related to #13085"""
        # Fails with another, ORM-level error
        dev1 = Developer(name='Joe')
        note = Note(note='Deserves promotion', content_object=dev1)
        self.assertRaises(IntegrityError, note.save)

    def test_target_model_len_zero(self):
        """Test for #13085 -- __len__() returns 0"""
        team1 = Team.objects.create(name='Backend devs')
        try:
            note = Note(note='Deserve a bonus', content_object=team1)
        except Exception as e:
            if (issubclass(type(e), Exception) and
                    str(e) == 'Impossible arguments to GFK.get_content_type!'):
                self.fail("Saving model with GenericForeignKey to model instance whose "
                          "__len__ method returns 0 shouldn't fail.")
            raise e
        note.save()

    def test_target_model_nonzero_false(self):
        """Test related to #13085"""
        # __nonzero__() returns False -- This actually doesn't currently fail.
        # This test validates that
        g1 = Guild.objects.create(name='First guild')
        note = Note(note='Note for guild', content_object=g1)
        note.save()

    @skipIfDBFeature('interprets_empty_strings_as_nulls')
    def test_gfk_to_model_with_empty_pk(self):
        """Test related to #13085"""
        # Saving model with GenericForeignKey to model instance with an
        # empty CharField PK
        b1 = Board.objects.create(name='')
        tag = Tag(label='VP', content_object=b1)
        tag.save()

    def test_ticket_20378(self):
        hs1 = HasLinkThing.objects.create()
        hs2 = HasLinkThing.objects.create()
        l1 = Link.objects.create(content_object=hs1)
        l2 = Link.objects.create(content_object=hs2)
        self.assertQuerysetEqual(
            HasLinkThing.objects.filter(links=l1),
            [hs1], lambda x: x)
        self.assertQuerysetEqual(
            HasLinkThing.objects.filter(links=l2),
            [hs2], lambda x: x)
        self.assertQuerysetEqual(
            HasLinkThing.objects.exclude(links=l2),
            [hs1], lambda x: x)
        self.assertQuerysetEqual(
            HasLinkThing.objects.exclude(links=l1),
            [hs2], lambda x: x)

    def test_ticket_20564(self):
        b1 = B.objects.create()
        b2 = B.objects.create()
        b3 = B.objects.create()
        c1 = C.objects.create(b=b1)
        c2 = C.objects.create(b=b2)
        c3 = C.objects.create(b=b3)
        A.objects.create(flag=None, content_object=b1)
        A.objects.create(flag=True, content_object=b2)
        self.assertQuerysetEqual(
            C.objects.filter(b__a__flag=None),
            [c1, c3], lambda x: x
        )
        self.assertQuerysetEqual(
            C.objects.exclude(b__a__flag=None),
            [c2], lambda x: x
        )

    def test_ticket_20564_nullable_fk(self):
        b1 = B.objects.create()
        b2 = B.objects.create()
        b3 = B.objects.create()
        d1 = D.objects.create(b=b1)
        d2 = D.objects.create(b=b2)
        d3 = D.objects.create(b=b3)
        d4 = D.objects.create()
        A.objects.create(flag=None, content_object=b1)
        A.objects.create(flag=True, content_object=b1)
        A.objects.create(flag=True, content_object=b2)
        self.assertQuerysetEqual(
            D.objects.exclude(b__a__flag=None),
            [d2], lambda x: x
        )
        self.assertQuerysetEqual(
            D.objects.filter(b__a__flag=None),
            [d1, d3, d4], lambda x: x
        )
        self.assertQuerysetEqual(
            B.objects.filter(a__flag=None),
            [b1, b3], lambda x: x
        )
        self.assertQuerysetEqual(
            B.objects.exclude(a__flag=None),
            [b2], lambda x: x
        )

    def test_extra_join_condition(self):
        # A crude check that content_type_id is taken in account in the
        # join/subquery condition.
        self.assertIn("content_type_id", str(B.objects.exclude(a__flag=None).query).lower())
        # No need for any joins - the join from inner query can be trimmed in
        # this case (but not in the above case as no a objects at all for given
        # B would then fail).
        self.assertNotIn(" join ", str(B.objects.exclude(a__flag=True).query).lower())
        self.assertIn("content_type_id", str(B.objects.exclude(a__flag=True).query).lower())

    def test_editable_generic_rel(self):
        GenericRelationForm = modelform_factory(HasLinkThing, fields='__all__')
        form = GenericRelationForm()
        self.assertIn('links', form.fields)
        form = GenericRelationForm({'links': None})
        self.assertTrue(form.is_valid())
        form.save()
        links = HasLinkThing._meta.get_field_by_name('links')[0].field
        self.assertEqual(links.save_form_data_calls, 1)

    def test_ticket_22998(self):
        related = Related.objects.create()
        content = Content.objects.create(related_obj=related)
        Node.objects.create(content=content)

        # deleting the Related cascades to the Content cascades to the Node,
        # where the pre_delete signal should fire and prevent deletion.
        with self.assertRaises(ProtectedError):
            related.delete()
