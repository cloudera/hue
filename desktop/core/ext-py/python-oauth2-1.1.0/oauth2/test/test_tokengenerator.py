import re
from oauth2.test import unittest
from oauth2.tokengenerator import URandomTokenGenerator, Uuid4

class URandomTokenGeneratorTestCase(unittest.TestCase):
    def test_generate(self):
        length = 20
        
        generator = URandomTokenGenerator(length=length)
        
        result = generator.generate()
        
        self.assertTrue(isinstance(result, str))
        self.assertEqual(len(result), length)

class Uuid4TestCase(unittest.TestCase):
    def setUp(self):
        self.uuid_regex = r"^[a-z0-9]{8}\-[a-z0-9]{4}\-[a-z0-9]{4}\-[a-z0-9]{4}-[a-z0-9]{12}$"
    
    def test_create_access_token_data_no_expiration(self):
        generator = Uuid4()
        
        result = generator.create_access_token_data('test_grant_type')
        
        self.assertRegexpMatches(result["access_token"], self.uuid_regex)
        self.assertEqual(result["token_type"], "Bearer")
    
    def test_create_access_token_data_with_expiration(self):
        generator = Uuid4()
        generator.expires_in = {'test_grant_type':600}
        
        result = generator.create_access_token_data('test_grant_type')
        
        self.assertRegexpMatches(result["access_token"], self.uuid_regex)
        self.assertEqual(result["token_type"], "Bearer")
        self.assertRegexpMatches(result["refresh_token"], self.uuid_regex)
        self.assertEqual(result["expires_in"], 600)
    
    def test_generate(self):
        generator = Uuid4()
        
        result = generator.generate()
        
        regex = re.compile(self.uuid_regex)
        
        match = regex.match(result)
        
        self.assertEqual(result, match.group())

if __name__ == "__main__":
    unittest.main()
