/* 
 * Copyright (C) 2006-2013  Music Technology Group - Universitat Pompeu Fabra
 *
 * This file is part of Essentia
 * 
 * Essentia is free software: you can redistribute it and/or modify it under 
 * the terms of the GNU Affero General Public License as published by the Free 
 * Software Foundation (FSF), either version 3 of the License, or (at your 
 * option) any later version.
 * 
 * This program is distributed in the hope that it will be useful, but WITHOUT 
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS 
 * FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more 
 * details.
 * 
 * You should have received a copy of the GNU General Public License along with 
 * this program.  If not, see http://www.gnu.org/licenses/
 */

#include "spectralpeaks.h"

using namespace std;
using namespace essentia;
using namespace standard;

const char* SpectralPeaks::name = "SpectralPeaks";
const char* SpectralPeaks::description = DOC("This algorithm extracts peaks from a spectrum. It is important to note that the peak algorithm is independent of an input that is linear or in dB, so one has to adapt the threshold to fit with the type of data fed to it. The exactness of the peak-searching depends heavily on the windowing type. It gives best results with dB input, a blackman-harris 92dB window and interpolation set to true. For further information about the peak detection, see the description of the PeakDetection algorithm.\n"
"\n"
"It is recommended that the input \"spectrum\" be computed by the Spectrum algorithm. This algorithm uses PeakDetection. See documentation for possible exceptions and input requirements on input \"spectrum\".\n");


void SpectralPeaks::configure() {
  // adapt config from spectral to generic
  ParameterMap config;
  config.add("range", parameter("sampleRate").toReal()/2.0);
  config.add("maxPeaks", parameter("maxPeaks"));
  config.add("minPosition", parameter("minFrequency"));
  config.add("maxPosition", parameter("maxFrequency"));
  config.add("threshold", parameter("magnitudeThreshold"));

  string orderBy = parameter("orderBy").toLower();
  if (orderBy == "magnitude") {
    config.add("orderBy", "amplitude");
  }
  else if (orderBy == "frequency") {
    config.add("orderBy", "position");
  }
  else {
    throw EssentiaException("Unsupported ordering type: '" + orderBy + "'");
  }

  _peakDetect->configure(config);
}

void SpectralPeaks::compute() {

  const std::vector<Real>& spectrum = _spectrum.get();
  std::vector<Real>& peakMagnitude = _magnitudes.get();
  std::vector<Real>& peakFrequency = _frequencies.get();

  _peakDetect->input("array").set(spectrum);
  _peakDetect->output("positions").set(peakFrequency);
  _peakDetect->output("amplitudes").set(peakMagnitude);

  _peakDetect->compute();
}
