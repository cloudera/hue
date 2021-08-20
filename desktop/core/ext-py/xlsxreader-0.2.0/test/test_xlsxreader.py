import unittest
import os
import sys

if sys.version_info[0] == 3:
    from pathlib import Path
else:
    from pathlib2 import Path
    ModuleNotFoundError = ImportError

try:
    from xlsxreader import readxlsx

except ModuleNotFoundError:
    sys.path.append('..')
    from xlsxreader import readxlsx

if 'test' in os.listdir('.'):
    os.chdir('./test')

class TestXlsxReaderOutput(unittest.TestCase):
    
    def test_path_dates_styles_output(self):
        with open('./testbook1.csv', encoding='utf-8-sig') as file:
            correct_out = file.read()
        test_file = readxlsx('./testbook1.xlsx')
        test_file.seek(0)
        test_out = str(test_file.read(), encoding='utf-8')
        self.assertEqual(correct_out, test_out)

    def test_path_large_input_output(self):
        with open('./testbook2.csv', encoding='utf-8-sig') as file:
            correct_out = file.read()
        test_file = readxlsx('./testbook2.xlsx')
        test_file.seek(0)
        test_out = str(test_file.read(), encoding='utf-8')
        with open('test.txt', 'w') as file:
            file.write(test_out)
        self.assertEqual(correct_out, test_out)

class TestXlsxReaderBadinput(unittest.TestCase):

    def test_bad_type(self):
        with self.assertRaises(UserWarning) as e:
            _  = readxlsx(file_name=3)
            self.assertEqual('Not a file path string ({}).'.format(('3')), e)

    def test_does_not_exist(self):
        with self.assertRaises(UserWarning) as e:
            _  = readxlsx(file_name='noexist')
            self.assertEqual('File ({}) does not exist.'.format(('noexist')), e)

    def test_bad_extension(self):
        with self.assertRaises(UserWarning) as e:
            _  = readxlsx(file_name='test_xlsxreader.py')
            self.assertEqual('Must be a .xlsx file.', e)

if __name__ == '__main__':
    unittest.main()