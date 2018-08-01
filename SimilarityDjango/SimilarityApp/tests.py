from django.test import TestCase
import os

# Create your tests here.
file = '123.txt.xls'

print(os.path.splitext(file)[1])