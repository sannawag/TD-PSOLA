# TD-PSOLA
This repository provides a script for pitch shifting using the "time-domain pitch synchronous overlap and add (TD-PSOLA)" algorithm. The original PSOLA algorithm was introduced in [1].

## Description
The main script ```td_psola.py``` takes raw audio as input and applies steps similar to those described in [2]. First, it locates the time-domain peaks using auto-correlation. It then shifts windows centered at the peaks closer or further apart in time to change the periodicity of the signal, which shifts the pitch without affecting the formant. It applies linear cross-fading as introduced in [3] and implemented in [4], the algorithm used for [Audacity[(https://www.audacityteam.org/)'s simple pitch shifter. 

## Usage
Make sure that ```pip``` and ```python3``` are installed (The program was written using Python 3.6) and install the script's dependencies. Note: ```Librosa``` is used for audio reading and writing but can be replaced with other packages such as ```scipy.signal```. ```Matplotlib``` can be removed if not plotting the results. 

```
pip3 install -r requirements.txt
```

The script can be run through

```python td_psola.py``` or imported into another program by ```from td_psola import shift_pitch```.

To test it, simply run ```python td_psola.py``` with the default settings and compare the output with ```female_scale_transposed_target_0.89.wav```.

### Notes
- Some parameters in the program related to frequency are hardcoded for singing voice. They can be adjusted for other usages.
- The program is designed to process sounds whose pitch does not vary too much, as this could result in glitches in peak detection (e.g., octave errors). Processing audio in short segment (e.g., notes or words) is recommended. Another option would be to use a more robust peak detection algorithm, for example, pYIN [5]
- Small pitch shifts (e.g., up to 700 cents) should not produce many artifacts. Sound quality degrades if the shift is too large.
- The signal is expected to be voiced. Unexpected results may occur in the case of unvoiced signals

## References
1. F. Charpentier and M. Stella. "Diphone synthesis using an overlap-add technique for speech waveforms concatenation." In *Int. Conf. Acoustics, Speech, and Signal Processing (ICASSP)*. Vol. 11. IEEE, 1986. 
2. [Overlap and add algorithm exercise from UIUC](https://courses.engr.illinois.edu/ece420/lab5/lab/#overlap-add-algorithm)
3. [Time and pitch scaling using SOLA](https://www.surina.net/article/time-and-pitch-scaling.html)
4. [Soundtouch](https://gitlab.com/soundtouch)
5. [Probabilistic YIN (pYIN)](https://code.soundsoftware.ac.uk/projects/pyin)
