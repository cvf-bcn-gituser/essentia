#!/usr/bin/env python

# Copyright (C) 2006-2016  Music Technology Group - Universitat Pompeu Fabra
#
# This file is part of Essentia
#
# Essentia is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation (FSF), either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the Affero GNU General Public License
# version 3 along with this program. If not, see http://www.gnu.org/licenses/


from essentia_test import *
import essentia

class TestHarmonicBpm(TestCase):

    def testInvalidParam(self):
        # Test that we must give valid frequency ranges or order
        self.assertConfigureFails(HarmonicBpm(), {'bpm': 0})
        self.assertConfigureFails(HarmonicBpm(), {'threshold': 0 })
        self.assertConfigureFails(HarmonicBpm(), {'tolerance': -1 })

    def testConstantInput(self):
        # constant input reports bpms 0
        testBpms = [120, 120, 120, 120, 120, 120, 120]
        harmonicBpms = HarmonicBpm(bpm=120)(testBpms)
        self.assertEqual(harmonicBpms, 120)
  
    def testZeros(self):
        # Ensure that an exception is thrown if any element contains a zero
        testBpms = [0, 100]
        self.assertRaises(EssentiaException, lambda: HarmonicBpm()(testBpms))
        testBpms = [100, 100, 100, 100, 0]
        self.assertRaises(EssentiaException, lambda: HarmonicBpm()(testBpms))
        testBpms = zeros(100)
        self.assertRaises(EssentiaException, lambda: HarmonicBpm()(testBpms))

    # Perform a series of 4 RTs that vary parameters
    def testRegressionStandard(self):
        testBpms = [100, 101, 102, 103, 104]
        harmonicBpms = HarmonicBpm(bpm=100)(testBpms)
        expectedBpm = 100
        self.assertEqual(harmonicBpms, expectedBpm)

    # Check the value below threshold is not included in harmonicBpms
    def testRegressionThresholdLimit(self):
        testBpms = [99, 100, 101, 102, 103, 104, 250]
        harmonicBpms = HarmonicBpm(bpm=100, threshold=99)(testBpms)
        expectedBpm = 100
        self.assertEqual(harmonicBpms, expectedBpm)

    # Reduce tolerance parameter
    def testRegressionLowTolerance(self):
        testBpms = [100, 101, 102, 103, 104]
        harmonicBpms = HarmonicBpm(bpm=100, tolerance=1)(testBpms)
        expectedBpm = [100., 101.]
        self.assertEqualVector(harmonicBpms, expectedBpm)

    # Check for bpm outside of input range
    def testRegressionBpmHigh(self):
        testBpms = [100, 101, 102, 103, 104]
        harmonicBpms = HarmonicBpm(bpm=105)(testBpms)    
        expectedBpm =  104
        self.assertEqual(harmonicBpms, expectedBpm)

    # Do a regression test on a tempo impulse that varies a bit, for 2 octaves
    def testRegressionMultipleOctave(self):
        testBpms = [100, 101, 102, 103, 104, 200, 202, 204, 206, 208, 300, 302, 304, 306, 308]
        harmonicBpms = HarmonicBpm(bpm=100)(testBpms)   
        expectedBpm =[100.0, 200.0, 300.0]
        self.assertEqualVector(harmonicBpms, expectedBpm)

    def testEmpty(self):
        # nothing should be computed and the resulting pool should be empty
        harmonicBpms = HarmonicBpm(bpm=100)([])
        self.assertEqualVector(harmonicBpms, [])


suite = allTests(TestHarmonicBpm)

if __name__ == '__main__':
    TextTestRunner(verbosity=2).run(suite)
