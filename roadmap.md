# Audio Application Ideas

## Steps to Making a Harmony Stabilization Application

## Ideas for Next Steps
* create a tone class that captures the harmonic spectrum of a sound.
* Create a circular list for holding running histories
* make the dissonance look more like the moving note values instead of the bar graph

## Bigger Ideas
* Create another graph that shows the dissonance of the given notes (after adding at least one more note)
   - Use this resource to calculate dissonance: https://music.stackexchange.com/questions/4439/is-there-a-way-to-measure-the-consonance-or-dissonance-of-a-chord
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