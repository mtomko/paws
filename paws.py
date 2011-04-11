'''
Created on Dec 28, 2010

@author: Mark Tomko
'''

class PAWSError(Exception):
  '''
  This is a general exception raised by PAWS classes and functions.
  '''
  def __init__(self, value):
    '''
    Constructor
    '''
    self.value = value
  def __str__(self):
    return repr(self.value)

