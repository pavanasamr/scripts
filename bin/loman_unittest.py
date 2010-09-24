#!/usr/bin/python

# Copyright (c) 2010 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Unittests for loman."""

import os
import StringIO
import sys
import tempfile
import unittest

import loman

_TEST_MANIFEST1 = """<manifest>
<project name="foo" path="path/to/foo" workon="True" />
</manifest>"""

class LocalManifestTest(unittest.TestCase):

  def setUp(self):
    self.utf8 = "<?xml version='1.0' encoding='UTF-8'?>\n"
    self.tiny_manifest = '<manifest>\n</manifest>'

  def testSimpleParse(self):
    ptree = loman.LocalManifest()
    ptree.Parse()

  def testParse(self):
    ptree = loman.LocalManifest(self.tiny_manifest)
    ptree.Parse()
    self.assertEqual(ptree.ToString(), self.utf8 + self.tiny_manifest)

  def testUTF8Parse(self):
    ptree = loman.LocalManifest(self.utf8 + self.tiny_manifest)
    ptree.Parse()
    self.assertEqual(ptree.ToString(), self.utf8 + self.tiny_manifest)

  def testGetProject(self):
    ptree = loman.LocalManifest('<manifest>\n</manifest>')
    ptree.Parse()
    ptree.AddProject('foo', 'path/to/foo')
    project = ptree.GetProject('foo')
    self.assertEqual(project.attrib['name'], 'foo')

  def testAddNew(self):
    ptree = loman.LocalManifest('<manifest>\n</manifest>')
    ptree.Parse()
    self.assertTrue(ptree.AddWorkonProject('foo', 'path/to/foo'))
    self.assertEqual(
      ptree.ToString(),
      self.utf8 + '<manifest>\n'
      '<project name="foo" path="path/to/foo" workon="True" />\n'
      '</manifest>')

  def testAddNewElement(self):
    dtree = loman.LocalManifest('<manifest>\n</manifest>')
    dtree.Parse()
    dtree.AddProject('foo', 'path/to/foo')
    ptree = loman.LocalManifest('<manifest>\n</manifest>')
    ptree.Parse()
    ptree.AddWorkonProjectElement(dtree.GetProject('foo'))
    self.assertEqual(
      ptree.ToString(),
      self.utf8 + '<manifest>\n'
      '<project name="foo" path="path/to/foo" workon="True" />\n'
      '</manifest>')

  def testAddDup(self):
    ptree = loman.LocalManifest('<manifest>\n</manifest>')
    ptree.Parse()
    ptree.AddWorkonProject('foo', 'path/to/foo')
    self.assertTrue(ptree.AddWorkonProject('foo', 'path/to/foo'))
    self.assertTrue(not ptree.AddWorkonProject('foo', 'path/foo'))
    self.assertTrue(not ptree.AddWorkonProject('foobar', 'path/to/foo'))

class MainTest(unittest.TestCase):

  def setUp(self):
    self.utf8 = "<?xml version='1.0' encoding='UTF-8'?>\n"
    self.tiny_manifest = '<manifest>\n</manifest>'
    self.stderr = sys.stderr
    sys.stderr = StringIO.StringIO()

  def tearDown(self):
    sys.stderr = self.stderr

  def testNotEnoughArgs(self):
    err_msg = 'Not enough arguments\n'
    self.assertRaises(SystemExit, loman.main, ['loman'])
    self.assertTrue(sys.stderr.getvalue().endswith(err_msg))

  def testNotWorkon(self):
    err_msg = 'Adding of non-workon projects is currently unsupported.\n'
    self.assertRaises(SystemExit, loman.main, ['loman', 'add', 'foo', 'path'])
    self.assertTrue(sys.stderr.getvalue().endswith(err_msg))

  def testBadCommand(self):
    err_msg = 'Unsupported command: bad.\n'
    self.assertRaises(SystemExit, loman.main, ['loman', 'bad', 'foo', 'path'])
    self.assertTrue(sys.stderr.getvalue().endswith(err_msg))

  def testSimpleAdd(self):
    default = tempfile.NamedTemporaryFile('w')
    print >> default, '<manifest>\n' \
      '<project name="foo" path="path/to/foo" />\n' \
      '</manifest>\n'
    default.flush()
    os.fsync(default.fileno())
    temp = tempfile.NamedTemporaryFile('w')
    print >> temp, '<manifest>\n</manifest>'
    temp.flush()
    os.fsync(temp.fileno())
    loman.main(['loman', 'add', '--workon', '-f', temp.name,
                '-d', default.name, 'foo'])
    self.assertEqual(
      open(temp.name, 'r').read(),
      self.utf8 + '<manifest>\n'
      '<project name="foo" path="path/to/foo" workon="True" />\n'
      '</manifest>\n')

  def testIgnoredPath(self):
    default = tempfile.NamedTemporaryFile('w')
    print >> default, '<manifest>\n' \
      '<project name="foo" path="path/to/foo" />\n' \
      '</manifest>\n'
    default.flush()
    os.fsync(default.fileno())
    temp = tempfile.NamedTemporaryFile('w')
    print >> temp, '<manifest>\n</manifest>'
    temp.flush()
    os.fsync(temp.fileno())
    loman.main(['loman', 'add', '--workon', '-f', temp.name,
                '-d', default.name, 'foo'])

  def testAddDup(self):
    default = tempfile.NamedTemporaryFile('w')
    print >> default, '<manifest>\n' \
      '<project name="foo" path="path/to/foo" />\n' \
      '</manifest>\n'
    default.flush()
    os.fsync(default.fileno())
    temp = tempfile.NamedTemporaryFile('w')
    print >> temp, '<manifest>\n' \
      '<project name="foo" path="bad/path/to/foo" />\n' \
      '</manifest>\n'
    temp.flush()
    os.fsync(temp.fileno())
    self.assertRaises(SystemExit, loman.main,
                      ['loman', 'add', '--workon', '-f', temp.name,
                       '-d', default.name, 'foo'])

  def testAddNonexistant(self):
    default = tempfile.NamedTemporaryFile('w')
    print >> default, '<manifest>\n' \
      '<project name="foo" path="path/to/foo" />\n' \
      '</manifest>\n'
    default.flush()
    os.fsync(default.fileno())
    temp = tempfile.NamedTemporaryFile('w')
    print >> temp, '<manifest>\n</manifest>'
    temp.flush()
    os.fsync(temp.fileno())
    self.assertRaises(SystemExit, loman.main,
                      ['loman', 'add', '--workon', '-f', temp.name,
                       '-d', default.name, 'bar'])


if __name__ == '__main__':
  unittest.main()
