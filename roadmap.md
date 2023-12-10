# Audio Application Ideas

## Steps to Making a Harmony Stabilization Application

## Ideas for Next Steps
* Add a smooth slider for note1 that can recreate the peaks in the dissonance I say on music Stack Exchange
* Add a trail for note2
* Set y-axis ticks to show octaves

## Bigger Ideas
* Make a GUI with slider that controls sine waves
* Create options to add notes
* Create options to adjust step size of frequency shifting buttons for fine-tuning

## Code Improvement Ideas
* Create a class for notes
   * a note has a set of overtones with various strengths (a timber)
   * a note has its own circular array for its history
* Create a class for the circular array that's used to store the frequency history
   * It should have get_next_index() and to_list() functions

### Completed
* Convert tone_graph to using matplotlib animation API
* Make the yaxis limits adapt to maximum values as they come 
* make the dissonance look more like the moving note values instead of the bar graph
* Create a circular list for holding running histories
* Modify the dissonance calculation to take into account all the overtones of the tones
* create a tone class that captures the harmonic spectrum of a sound.
* put a log scale to the graph
* Create and test the dissonance function http://www.acousticslab.org/learnmoresra/moremodel.html
* On the second graph, put the dissonance between the notes
* Learn how to generate sines
* Learn how to interact with keyboard (examples/record_ram_to_disk.py)
* Make a pitch graph that I can interact with
* Control a note's frequency with keyboard inputs
* See if I can graph a note frequency
* Modify graph to be able to move the note while mouse is clicked
* Make a graph that updates with time and shows note frequencies as well as previous frequencies
* Add another note
* Create a second graph in the same window
* on the second graph, put the distance between the notes

## Handwritten Notes


## Ideas Ideas fort the Distant Future
* Convert this into a viewable web page somehow
  * Could also post a video with the published code
* Create a program that decomposes instruments/sounds into synthesizer settings (like amplitudes of triangle/sine/etc. waves)