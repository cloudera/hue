import unittest

from south.creator.changes import AutoChanges

class TestComparison(unittest.TestCase):
    
    """
    Tests the comparison methods of startmigration.
    """
    
    def test_no_change(self):
        "Test with a completely unchanged definition."
        
        self.assertEqual(
            AutoChanges.different_attributes(
                ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['southdemo.Lizard']"}),
                ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['southdemo.Lizard']"}),
            ),
            False,
        )
        
        self.assertEqual(
            AutoChanges.different_attributes(
                ('django.db.models.fields.related.ForeignKey', ['ohhai', 'there'], {'to': "somewhere", "from": "there"}),
                ('django.db.models.fields.related.ForeignKey', ['ohhai', 'there'], {"from": "there", 'to': "somewhere"}),
            ),
            False,
        )
    
    
    def test_pos_change(self):
        "Test with a changed positional argument."
        
        self.assertEqual(
            AutoChanges.different_attributes(
                ('django.db.models.fields.CharField', ['hi'], {'to': "foo"}),
                ('django.db.models.fields.CharField', [], {'to': "foo"}),
            ),
            True,
        )
        
        self.assertEqual(
            AutoChanges.different_attributes(
                ('django.db.models.fields.CharField', [], {'to': "foo"}),
                ('django.db.models.fields.CharField', ['bye'], {'to': "foo"}),
            ),
            True,
        )
        
        self.assertEqual(
            AutoChanges.different_attributes(
                ('django.db.models.fields.CharField', ['pi'], {'to': "foo"}),
                ('django.db.models.fields.CharField', ['pi'], {'to': "foo"}),
            ),
            False,
        )
        
        self.assertEqual(
            AutoChanges.different_attributes(
                ('django.db.models.fields.CharField', ['pisdadad'], {'to': "foo"}),
                ('django.db.models.fields.CharField', ['pi'], {'to': "foo"}),
            ),
            True,
        )
        
        self.assertEqual(
            AutoChanges.different_attributes(
                ('django.db.models.fields.CharField', ['hi'], {}),
                ('django.db.models.fields.CharField', [], {}),
            ),
            True,
        )
        
        self.assertEqual(
            AutoChanges.different_attributes(
                ('django.db.models.fields.CharField', [], {}),
                ('django.db.models.fields.CharField', ['bye'], {}),
            ),
            True,
        )
        
        self.assertEqual(
            AutoChanges.different_attributes(
                ('django.db.models.fields.CharField', ['pi'], {}),
                ('django.db.models.fields.CharField', ['pi'], {}),
            ),
            False,
        )
        
        self.assertEqual(
            AutoChanges.different_attributes(
                ('django.db.models.fields.CharField', ['pi'], {}),
                ('django.db.models.fields.CharField', ['45fdfdf'], {}),
            ),
            True,
        )
    
    
    def test_kwd_change(self):
        "Test a changed keyword argument"
        
        self.assertEqual(
            AutoChanges.different_attributes(
                ('django.db.models.fields.CharField', ['pi'], {'to': "foo"}),
                ('django.db.models.fields.CharField', ['pi'], {'to': "blue"}),
            ),
            True,
        )
        
        self.assertEqual(
            AutoChanges.different_attributes(
                ('django.db.models.fields.CharField', [], {'to': "foo"}),
                ('django.db.models.fields.CharField', [], {'to': "blue"}),
            ),
            True,
        )
        
        self.assertEqual(
            AutoChanges.different_attributes(
                ('django.db.models.fields.CharField', ['b'], {'to': "foo"}),
                ('django.db.models.fields.CharField', ['b'], {'to': "blue"}),
            ),
            True,
        )
        
        self.assertEqual(
            AutoChanges.different_attributes(
                ('django.db.models.fields.CharField', [], {'to': "foo"}),
                ('django.db.models.fields.CharField', [], {}),
            ),
            True,
        )
        
        self.assertEqual(
            AutoChanges.different_attributes(
                ('django.db.models.fields.CharField', ['a'], {'to': "foo"}),
                ('django.db.models.fields.CharField', ['a'], {}),
            ),
            True,
        )
        
        self.assertEqual(
            AutoChanges.different_attributes(
                ('django.db.models.fields.CharField', [], {}),
                ('django.db.models.fields.CharField', [], {'to': "foo"}),
            ),
            True,
        )
        
        self.assertEqual(
            AutoChanges.different_attributes(
                ('django.db.models.fields.CharField', ['a'], {}),
                ('django.db.models.fields.CharField', ['a'], {'to': "foo"}),
            ),
            True,
        )
        
    
    
    def test_backcompat_nochange(self):
        "Test that the backwards-compatable comparison is working"
        
        self.assertEqual(
            AutoChanges.different_attributes(
                ('models.CharField', [], {}),
                ('django.db.models.fields.CharField', [], {}),
            ),
            False,
        )
        
        self.assertEqual(
            AutoChanges.different_attributes(
                ('models.CharField', ['ack'], {}),
                ('django.db.models.fields.CharField', ['ack'], {}),
            ),
            False,
        )
        
        self.assertEqual(
            AutoChanges.different_attributes(
                ('models.CharField', [], {'to':'b'}),
                ('django.db.models.fields.CharField', [], {'to':'b'}),
            ),
            False,
        )
        
        self.assertEqual(
            AutoChanges.different_attributes(
                ('models.CharField', ['hah'], {'to':'you'}),
                ('django.db.models.fields.CharField', ['hah'], {'to':'you'}),
            ),
            False,
        )
        
        self.assertEqual(
            AutoChanges.different_attributes(
                ('models.CharField', ['hah'], {'to':'you'}),
                ('django.db.models.fields.CharField', ['hah'], {'to':'heh'}),
            ),
            True,
        )
        
        self.assertEqual(
            AutoChanges.different_attributes(
                ('models.CharField', ['hah'], {}),
                ('django.db.models.fields.CharField', [], {'to':"orm['appname.hah']"}),
            ),
            False,
        )
        
        self.assertEqual(
            AutoChanges.different_attributes(
                ('models.CharField', ['hah'], {}),
                ('django.db.models.fields.CharField', [], {'to':'hah'}),
            ),
            True,
        )
        
        self.assertEqual(
            AutoChanges.different_attributes(
                ('models.CharField', ['hah'], {}),
                ('django.db.models.fields.CharField', [], {'to':'rrr'}),
            ),
            True,
        )
        
        self.assertEqual(
            AutoChanges.different_attributes(
                ('models.CharField', ['hah'], {}),
                ('django.db.models.fields.IntField', [], {'to':'hah'}),
            ),
            True,
        )