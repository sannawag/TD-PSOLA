# TD-PSOLA
A simple pitch shifting script (Time-Domain Pitch Synchronous Overlap and Add)

This script applies time-domain pitch shifting using the peak detection technique described in 
- https://courses.engr.illinois.edu/ece420/lab5/lab/#overlap-add-algorithm
- Charpentier, Ff, and M. Stella. "Diphone synthesis using an overlap-add
  technique for speech waveforms concatenation."
  ICASSP'86. IEEE International Conference on Acoustics, Speech,
  and Signal Processing. Vol. 11. IEEE, 1986.
  
 It uses the linear cross-fading technique from SOLA
 - https://www.surina.net/article/time-and-pitch-scaling.html
 - https://gitlab.com/soundtouch (This program is used in Audacity for the simpler pitch shifting algorithm)
 
Dependencies:
- Librosa (for audio reading and writing: can be replaced with other packages like scipy.signal)
- Matplotlib (can be removed if not plotting the results)
- Numpy 

Note:
- The signal is expected to be voiced. Unexpected results may occur in the case of unvoiced signals
- The parameters in the program such as frequency thresholds are designed for singing voice. They can be adjusted for other instruments.
- The program is designed not to allow too much variation in pitch as this could result in glitches. Shifting every short audio segment (note) separately is recommended. Another option would be to use a more robust peak detection algorithm, for example, pYIN (https://code.soundsoftware.ac.uk/projects/pyin) 
- The result should not contain many artifacts when the shift is small enough (e.g., up to 700 cents). Sound quality degrades if the shift is too large.
