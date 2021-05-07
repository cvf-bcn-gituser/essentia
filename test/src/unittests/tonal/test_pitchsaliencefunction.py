#!/usr/bin/env python

# Copyright (C) 2006-2021  Music Technology Group - Universitat Pompeu Fabra
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

from numpy import *
from essentia_test import *

#define useful constants for the Test cases
defaultBinResolution = 10
fiveOctaveFullRange = 6000

class TestPitchSalienceFunction(TestCase):
  
    def testInvalidParam(self):
        self.assertConfigureFails(PitchSalienceFunction(), {'binResolution': -1})
        self.assertConfigureFails(PitchSalienceFunction(), {'binResolution': 0})        
        self.assertConfigureFails(PitchSalienceFunction(), {'harmonicWeight': -1})
        self.assertConfigureFails(PitchSalienceFunction(), {'harmonicWeight': 2})
        self.assertConfigureFails(PitchSalienceFunction(), {'magnitudeCompression': 0})        
        self.assertConfigureFails(PitchSalienceFunction(), {'magnitudeCompression': -1})
        self.assertConfigureFails(PitchSalienceFunction(), {'magnitudeCompression': 2})        
        self.assertConfigureFails(PitchSalienceFunction(), {'magnitudeThreshold': -1})
        self.assertConfigureFails(PitchSalienceFunction(), {'numberHarmonics': 0})
        self.assertConfigureFails(PitchSalienceFunction(), {'numberHarmonics': -1})        
        self.assertConfigureFails(PitchSalienceFunction(), {'referenceFrequency': -1})
        self.assertConfigureFails(PitchSalienceFunction(), {'referenceFrequency': 0})        

    def testEmpty(self): 
        self.assertEqualVector(PitchSalienceFunction()([], []), zeros(int(fiveOctaveFullRange/defaultBinResolution)))

    # Provide a single input peak with a unit magnitude at the reference frequency, and 
    # validate that the output salience function has only one non-zero element at the first bin.
    # Check also the remaining elements are zeros.
    def testSinglePeak(self):        
        binResolution = defaultBinResolution        
        # We have a non-zero element in bin 1. From then on, its all zeros.
        # Length of expectedPitchSalience = 11
        expectedPitchSalience = [1.0000000e+00, 9.7552824e-01, 9.0450847e-01, 7.9389262e-01, 6.5450847e-01,
        5.0000000e-01, 3.4549147e-01, 2.0610739e-01, 9.5491491e-02, 2.4471754e-02, 3.7493994e-33]
        freq_speaks = [55] 
        mag_speaks = [1] 
        outputLength  = int(fiveOctaveFullRange/binResolution)        
        calculatedPitchSalience = PitchSalienceFunction()(freq_speaks,mag_speaks)
        self.assertEqual(len(calculatedPitchSalience), int(fiveOctaveFullRange/binResolution))        
        # Check the first 11 elements. The first has value "1" 
        # The next 10 values are decreasing in magnitude.
        self.assertAlmostEqualVector(calculatedPitchSalience[:11], expectedPitchSalience, 8)
        # Check remaining elements are zeros
        self.assertEqualVector(calculatedPitchSalience[12:outputLength], zeros(outputLength-(12)))

    # Same as above, but tweaking the bin resolution to ensure output length is consistent
    def testSinglePeakNonDefaultBR(self):   
        binResolution = defaultBinResolution*4 # Lets test for a bin resolution of 40
        # Larger bin resolution reduces the number of non zero values in salience function
        # Length of expectedPitchSalience = 3        
        expectedPitchSalience = [1.0000000e+00, 5.0000000e-01, 3.7493994e-33]
        freq_speaks = [55] 
        mag_speaks = [1] 
        outputLength  = int(fiveOctaveFullRange/binResolution)        
        calculatedPitchSalience = PitchSalienceFunction(binResolution=binResolution)(freq_speaks,mag_speaks)
        self.assertEqual(len(calculatedPitchSalience), outputLength)
        # Check the first 3 elements. The first has value "1" 
        self.assertAlmostEqualVector(calculatedPitchSalience[:3], expectedPitchSalience, 8)
        # Check remaining elements are zeros
        self.assertEqualVector(calculatedPitchSalience[4:outputLength], zeros(outputLength-4))

    # Provide multiple duplicate peaks at the reference frequency.    
    def test3DuplicatePeaks(self):
        freq_speaks = [55, 55, 55] 
        mag_speaks = [1, 1, 1] 
        binResolution = defaultBinResolution
        outputLength  = int(fiveOctaveFullRange/binResolution)
        # The same expectedPitchSalience from testSinglePeak test case
        expectedPitchSalience = [1.0000000e+00, 9.7552824e-01, 9.0450847e-01, 7.9389262e-01, 6.5450847e-01,
        5.0000000e-01, 3.4549147e-01, 2.0610739e-01, 9.5491491e-02, 2.4471754e-02, 3.7493994e-33]

        # For 3 duplicate peaks, the expectedPitchSalience needs to be scaled by a factor of 3
        arrayExpectedPitchSalience = 3*array(expectedPitchSalience)
        calculatedPitchSalience = PitchSalienceFunction()(freq_speaks,mag_speaks) 
        # The next 10 values are decreasing in magnitude   
        self.assertAlmostEqualVector(calculatedPitchSalience[:binResolution+1], expectedPitchSalience, 8)
        # Check remaining elements are zeros
        self.assertEqualVector(calculatedPitchSalience[binResolution+2:outputLength], zeros(outputLength-(binResolution+2)))

    # Test for diverse frequency peaks.
    def test3Peaks(self):
        freq_speaks = [55, 100, 340] 
        mag_speaks = [1, 1, 1] 
        binResolution = defaultBinResolution
        outputLength  = int(fiveOctaveFullRange/binResolution)        
        calculatedPitchSalience = PitchSalienceFunction()(freq_speaks, mag_speaks)    
        # First check the length of the ouput is 600 
        self.assertEqual(len(calculatedPitchSalience), int(fiveOctaveFullRange/binResolution))        
        # This test case with diverser frequency to save ouput to NPY file since the output is more complex.
        # (i.e. the remining elements after salience fucntion  array element 11 are not all zeros)
        save('calculatedPitchSalience_test3Peaks.npy', calculatedPitchSalience)
        # Reference samples are loaded as expected values
        expectedPitchSalience = load(join(filedir(), 'pitchsalience/calculatedPitchSalience_test3Peaks.npy'))
        expectedPitchSalienceList = expectedPitchSalience.tolist()
        self.assertAlmostEqualVectorFixedPrecision(expectedPitchSalienceList, calculatedPitchSalience, 8)

    def testSinglePeakHw0(self):
        freq_speaks = [55] 
        mag_speaks = [1] 
        binResolution = defaultBinResolution
        outputLength  = int(fiveOctaveFullRange/binResolution)        
        calculatedPitchSalience = PitchSalienceFunction(harmonicWeight=0)(freq_speaks, mag_speaks)            
        self.assertEqual(calculatedPitchSalience[0], 1)
        self.assertEqualVector(calculatedPitchSalience[1:outputLength], zeros(outputLength-1))
        self.assertEqual(len(calculatedPitchSalience), int(fiveOctaveFullRange/binResolution))
                
    def testSinglePeakHw1(self):   
        freq_speaks = [55] 
        mag_speaks = [1] 
        binResolution = defaultBinResolution
        outputLength  = int(fiveOctaveFullRange/binResolution)        
        expectedPitchSalience = [1.0000000e+00, 9.7552824e-01, 9.0450847e-01, 7.9389262e-01, 6.5450847e-01,
        5.0000000e-01, 3.4549147e-01, 2.0610739e-01, 9.5491491e-02, 2.4471754e-02, 3.7493994e-33]
        calculatedPitchSalience = PitchSalienceFunction(harmonicWeight=1)(freq_speaks, mag_speaks)     
        self.assertEqual(len(calculatedPitchSalience), int(fiveOctaveFullRange/binResolution))        
        # Check the first 11 elements. The first has value "1" 
        # The next 10 values are decreasing in magnitude.
        self.assertAlmostEqualVector(calculatedPitchSalience[:11], expectedPitchSalience, 8)
        # Check remaining elements are zeros
        self.assertEqualVector(calculatedPitchSalience[12:outputLength], zeros(outputLength-(12)))

    def test3PeaksHw1(self):
        freq_speaks = [55, 100, 340] 
        mag_speaks = [1, 1, 1] 
        calculatedPitchSalience = PitchSalienceFunction(harmonicWeight=1)(freq_speaks, mag_speaks) 
        save('calculatedPitchSalience_test3PeaksHw1.npy', calculatedPitchSalience)
        # Reference samples are loaded as expected values
        expectedPitchSalience = load(join(filedir(), 'pitchsalience/calculatedPitchSalience_test3PeaksHw1.npy'))
        expectedPitchSalienceList = expectedPitchSalience.tolist()
        self.assertAlmostEqualVectorFixedPrecision(expectedPitchSalienceList, calculatedPitchSalience, 8)
        
    def testDifferentPeaks(self):
        freq_speaks = [55, 85] 
        mag_speaks = [1, 1] 
        calculatedPitchSalience1 = PitchSalienceFunction()(freq_speaks,mag_speaks)             
        save('calculatedPitchSalience_testDifferentPeaks1.npy', calculatedPitchSalience1)

        mag_speaks = [0.5, 2] 
        calculatedPitchSalience2 = PitchSalienceFunction()(freq_speaks,mag_speaks)
        save('calculatedPitchSalience_testDifferentPeaks2.npy', calculatedPitchSalience2)
 
        self.assertAlmostEqual(calculatedPitchSalience1[0], 0.5, 3)        
        self.assertAlmostEqual(calculatedPitchSalience2[0], 1.5, 3)

        expectedPitchSalience = load(join(filedir(), 'pitchsalience/calculatedPitchSalience_testDifferentPeaks1.npy'))
        expectedPitchSalienceList = expectedPitchSalience.tolist()
        self.assertAlmostEqualVectorFixedPrecision(expectedPitchSalienceList, calculatedPitchSalience1, 8)
        
        expectedPitchSalience = load(join(filedir(), 'pitchsalience/calculatedPitchSalience_testDifferentPeaks2.npy'))
        expectedPitchSalienceList = expectedPitchSalience.tolist()
        self.assertAlmostEqualVectorFixedPrecision(expectedPitchSalienceList, calculatedPitchSalience2, 8)
        
    # Provide a single input peak below the reference frequency, so that the result is an empty pitch 
    # salience function
    def testBelowReferenceFrequency1(self):
        freq_speaks = [50] 
        mag_speaks = [1] 
        binResolution = defaultBinResolution        
        outputLength  = int(fiveOctaveFullRange/binResolution)   
        expectedPitchSalience = zeros(outputLength)
        calculatedPitchSalience = PitchSalienceFunction()(freq_speaks, mag_speaks)            
        self.assertEqualVector(calculatedPitchSalience, expectedPitchSalience)

    def testBelowReferenceFrequency2(self):
        freq_speaks = [30] 
        mag_speaks = [1] 
        binResolution = defaultBinResolution             
        outputLength  = int(fiveOctaveFullRange/binResolution)           
        expectedPitchSalience = zeros(outputLength)
        calculatedPitchSalience = PitchSalienceFunction(referenceFrequency=40)(freq_speaks, mag_speaks)        
        self.assertEqualVector(calculatedPitchSalience, expectedPitchSalience)      

    def testMustContainPostiveFreq(self):
        # Throw in a zero Freq to see what happens. 
        freq_speaks = [0, 250, 400, 1300, 2200, 3300] # length 6
        mag_speaks = [1, 1, 1, 1, 1, 1] # length 6 
        self.assertRaises(RuntimeError, lambda: PitchSalienceFunction()(freq_speaks, mag_speaks))

    def testUnequalInputs(self):
        # Choose a sample set of frequencies and magnitude vectors of unequal length
        freq_speaks = [250, 400, 1300, 2200, 3300] # length 5
        mag_speaks = [1, 1, 1, 1] # length 4
        self.assertRaises(EssentiaException, lambda: PitchSalienceFunction()(freq_speaks, mag_speaks))

    """ FIXME

    The following test case has uncovered a situation where  divide by zero or some other 
    illegal operation has taken place because a NAN vlaue is found in output array element zero.

    def testBinResolutionTooHigh(self):        
        freq_speaks = [55] 
        mag_speaks = [1] 
        calculatedPitchSalience = PitchSalienceFunction(binResolution=55*2)(freq_speaks,mag_speaks)       
        print(calculatedPitchSalience)

        result:  calculatedPitchSalience[0] contains "nan"

    """  
    def testNegativeMagnitudeTest(self):
        freqs = [250, 500, 1000] # length 3
        mag_speaks = [1, -1, 1] # length 3
        self.assertRaises(EssentiaException, lambda: PitchSalienceFunction()(freqs, mag_speaks))

    def testRegressionTest(self):
        filename = join(testdata.audio_dir, 'recorded', 'vignesh.wav')
        audio = MonoLoader(filename=filename, sampleRate=44100)()
        frameSize = 2048
        sampleRate = 44100
        guessUnvoiced = True
        hopSize = 512

        #truncate the audio to take 0.5 sec (keep npy file size low)
        audio = audio[:22050]

        run_windowing = Windowing(type='hann', zeroPadding=3*frameSize) # Hann window with x4 zero padding
        run_spectrum = Spectrum(size=frameSize * 4)
        run_spectral_peaks = SpectralPeaks(minFrequency=1,
                                           maxFrequency=20000,
                                           maxPeaks=100,
                                           sampleRate=sampleRate,
                                           magnitudeThreshold=0,
                                           orderBy="magnitude")
        run_pitch_salience_function = PitchSalienceFunction()
       
        # Now we are ready to start processing.
        # 1. pass it through the equal-loudness filter
        audio = EqualLoudness()(audio)
        calculatedPitchSalience = []

        # 2. Cut audio into frames and compute for each frame:
        #    spectrum -> spectral peaks -> pitch salience function -> pitch salience function peaks
        for frame in FrameGenerator(audio, frameSize=frameSize, hopSize=hopSize):
            frame = run_windowing(frame)
            spectrum = run_spectrum(frame)
            peak_frequencies, peak_magnitudes = run_spectral_peaks(spectrum)
            salience = run_pitch_salience_function(peak_frequencies, peak_magnitudes)
            calculatedPitchSalience.append(salience)

        save('calculatedPitchSalience_vignesh.npy', calculatedPitchSalience)
        expectedPitchSalience = load(join(filedir(), 'pitchsalience/calculatedPitchSalience_vignesh.npy'))
        expectedPitchSalienceList = expectedPitchSalience.tolist()

        index=0
        for frame in FrameGenerator(audio, frameSize=frameSize, hopSize=hopSize):
            self.assertAlmostEqualVectorFixedPrecision(expectedPitchSalienceList[index], calculatedPitchSalience[index], 8)
            index+=1        

    def testRegressionSynthetic(self):
        # Use synthetic audio for Regression Test. This keeps NPY files size low.
        # First, create our algorithms:
        hopSize = 128
        frameSize = 2048
        sampleRate = 44100
        guessUnvoiced = True

        run_windowing = Windowing(type='hann', zeroPadding=3*frameSize) # Hann window with x4 zero padding
        run_spectrum = Spectrum(size=frameSize * 4)
        run_spectral_peaks = SpectralPeaks(minFrequency=1,
                                           maxFrequency=20000,
                                           maxPeaks=100,
                                           sampleRate=sampleRate,
                                           magnitudeThreshold=0,
                                           orderBy="magnitude")
        run_pitch_salience_function = PitchSalienceFunction()
        run_pitch_salience_function_peaks = PitchSalienceFunctionPeaks()
        run_pitch_contours = PitchContours(hopSize=hopSize)
        run_pitch_contours_melody = PitchContoursMelody(guessUnvoiced=guessUnvoiced,
                                                        hopSize=hopSize)
        signalSize = frameSize * 10
        # Here are generated sine waves for each note of the scale, e.g. C3 is 130.81 Hz, etc
        c3 = 0.5 * numpy.sin((array(range(signalSize))/44100.) * 130.81 * 2*math.pi)
        d3 = 0.5 * numpy.sin((array(range(signalSize))/44100.) * 146.83 * 2*math.pi)
        e3 = 0.5 * numpy.sin((array(range(signalSize))/44100.) * 164.81 * 2*math.pi)
        f3 = 0.5 * numpy.sin((array(range(signalSize))/44100.) * 174.61 * 2*math.pi)
        g3 = 0.5 * numpy.sin((array(range(signalSize))/44100.) * 196.00 * 2*math.pi)
        a3 = 0.5 * numpy.sin((array(range(signalSize))/44100.) * 220.00 * 2*math.pi)
        b3 = 0.5 * numpy.sin((array(range(signalSize))/44100.) * 246.94 * 2*math.pi)
        c4 = 0.5 * numpy.sin((array(range(signalSize))/44100.) * 261.63 * 2*math.pi)
    
        # This signal is a "major scale ladder"
        scale = concatenate([c3, d3, e3, f3, g3, a3, b3, c4])

        # Now we are ready to start processing.
        # 1. Load audio and pass it through the equal-loudness filter
        audio = EqualLoudness()(scale)

        # 2. Cut audio into frames and compute for each frame:
        #    spectrum -> spectral peaks -> pitch salience function -> pitch salience function peaks
        for frame in FrameGenerator(audio, frameSize=frameSize, hopSize=hopSize):
            frame = run_windowing(frame)
            spectrum = run_spectrum(frame)
            peak_frequencies, peak_magnitudes = run_spectral_peaks(spectrum)
            salience = run_pitch_salience_function(peak_frequencies, peak_magnitudes)
            salience_peaks_bins, salience_peaks_saliences = run_pitch_salience_function_peaks(salience)
                
        expectedBins = [270., 150. ,80. ,30.]
        expectedPeaks =  [0.09777679, 0.07822143, 0.06257715, 0.05006172]
        self.assertAlmostEqualVectorFixedPrecision(expectedBins, salience_peaks_bins, 8)
        self.assertAlmostEqualVectorFixedPrecision(expectedPeaks, salience_peaks_saliences, 8)

suite = allTests(TestPitchSalienceFunction)

if __name__ == '__main__':
    TextTestRunner(verbosity=2).run(suite)
