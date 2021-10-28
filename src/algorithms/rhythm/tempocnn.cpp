/*
 * Copyright (C) 2006-2021  Music Technology Group - Universitat Pompeu Fabra
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
 * You should have received a copy of the Affero GNU General Public License
 * version 3 along with this program.  If not, see http://www.gnu.org/licenses/
 */

#include "tempocnn.h"

using namespace std;
using namespace essentia;
using namespace standard;

const char* TempoCNN::name = "TempoCNN";
const char* TempoCNN::category = "Rhythm";
const char* TempoCNN::description = DOC(
  "This algorithm estimates tempo using TempoCNN-based models.\n"
  "\n"
  "Internally, this algorithm is a wrapper to aggregate the predictions "
  "generated by TensorflowPredictTempoCNN. `localTempo` is a vector containing "
  "the most likely BPM estimated each ~6 seconds by default. "
  "`localTempoProbabilities` contains the probabilities attached to the tempo "
  "estimations and can be used as a confidence measure. `globalTempo` is an "
  "aggregation of localTempo using an `aggregationMethod`. We strongly "
  "recommend to use majority voting when assuming constant tempo in the input "
  "audio.\n"
  "\n"
  "See TensorflowPredictTempoCNN for details about the rest of parameters.\n"
  "The recommended pipeline is as follows::\n"
  "\n"
  "  MonoLoader(sampleRate=11025) >> TempoCNN\n"
  "\n"
  "Note: This algorithm does not make any check on the input model so it is "
  "the user's responsibility to make sure it is a valid one.\n"
  "\n"
  "References:\n"
  "\n"
  "1. Hendrik Schreiber, Meinard Müller, A Single-Step Approach to Musical "
  "Tempo Estimation Using a Convolutional Neural Network Proceedings of the "
  "19th International Society for Music Information Retrieval Conference "
  "(ISMIR), Paris, France, Sept. 2018.\n"
  "\n"
  "2. Hendrik Schreiber, Meinard Müller, Musical Tempo and Key Estimation "
  "using Convolutional Neural Networks with Directional Filters Proceedings of "
  "the Sound and Music Computing Conference (SMC), Málaga, Spain, 2019.\n"
  "\n"
  "3. Original models and code at https://github.com/hendriks73/tempo-cnn\n"
  "\n"
  "4. Supported models at https://essentia.upf.edu/models/\n\n");


// TempoCNN models output a softmax distribution of length 256.
// The first index of the distribution is equivalent to 30 BPM, the second to 31 and so on.
const Real _BPMOffset = 30.f;


void TempoCNN::configure() {
  _tensorflowPredictTempoCNN->configure(INHERIT("graphFilename"),
                                        INHERIT("savedModel"),
                                        INHERIT("input"),
                                        INHERIT("output"),
                                        INHERIT("patchHopSize"),
                                        INHERIT("lastPatchMode"),
                                        INHERIT("batchSize"));

  _aggregationMethod = parameter("aggregationMethod").toLower();
}


void TempoCNN::compute() {
  const vector<Real>& audio = _audio.get();
  Real& globalTempo = _globalTempo.get();
  vector<Real>& localTempo = _localTempo.get();
  vector<Real>& localTempoProbs = _localTempoProbs.get();

  _tensorflowPredictTempoCNN->input("signal").set(audio);
  _tensorflowPredictTempoCNN->output("predictions").set(_predictions);
  _tensorflowPredictTempoCNN->compute();

  localTempo.resize(_predictions.size());
  localTempoProbs.resize(_predictions.size());

  for (int i = 0; i < (int)_predictions.size(); i++) {
    int index = argmax(_predictions[i]);
    localTempo[i] = (Real)index + _BPMOffset;
    localTempoProbs[i] = _predictions[i][index];
  }


  if (_aggregationMethod == "mean") {
    globalTempo = mean(localTempo);
  }
  else if (_aggregationMethod == "median") {
    globalTempo = median(localTempo);
  }
  else if (_aggregationMethod == "majority") {
    int mostVotedCandidate = localTempo[0], secondCandidate = localTempo[0];
    int mostVotedVotes = 0, secondVotes = 0;
    int candidate, votes;
    vector<int> checked;

    for (int i = 0; i < (int)_predictions.size(); i++) {
      candidate = (int)localTempo[i];

      if (find(checked.begin(), checked.end(), candidate) != checked.end()) continue;

      votes = count(localTempo.begin(), localTempo.end(), candidate);

      if (votes > mostVotedVotes) {
        secondCandidate = mostVotedCandidate;
        secondVotes = mostVotedVotes;
        mostVotedCandidate = candidate;
        mostVotedVotes = votes;
      }

      checked.push_back(candidate);
    }

    globalTempo = (Real)mostVotedCandidate;

    if (secondVotes == mostVotedVotes) {
      E_WARNING("TempoCNN: On the computation of majority voting, the second candidate, "
                << secondCandidate << ", obtained the same number of votes as the winning candidate, "
                << mostVotedCandidate);
    }
  }
  else {
    throw EssentiaException("TempoCNN: Bad 'aggregationMethod' parameter");
  }

}
