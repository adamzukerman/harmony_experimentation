# Audio Application Ideas

## Steps to Making a Harmony Stabilization Application

## Where I Left Off

## Ideas for Next Steps
* Create a piano-like input using the keyboard. 
  * TODO: Resolve conflicts with matplotlib keybindings
  * Also, this feature feels really crappy. It seems hard to make an intuitive mapping from keyboard to piano keys without an additional graphic
* Redo how I set random overtones. It's currently not anything related to real sounds

## Bigger Ideas
* Refactor to an events-based framework for performance. 
* Make a GUI with slider that controls sine waves
* Create options to adjust step size of frequency shifting buttons for fine-tuning

## Code Improvement Ideas
* stop building the set of notes from the middle out

### Completed
* Change structure of code to support an arbitrary number of notes
* Create options to add notes
  * Have a running list of active notes.
  * Have a method to add and remove active notes
  * Have a currently selected note.
    * This note should be made visually more obvious
* Make the resolver move notes smoothly
* Find method to optimize dissonance of note1
* Create an axis that shows nearby dissonances if note1 were to slide
* Moving all input handling to input.py
* Find a way to handle the global variables about MOUSE_PRESSED and PIANO_MODE
* Flip the axes of the note axis so notes are shifted horizontally
* Add a trail for note2
* Create a class for notes
   * a note has a set of overtones with various strengths (a timber)
   * a note has its own circular array for its history
* Create a class for the circular array that's used to store the frequency history
   * It should have get_next_index() and to_list() functions
* Fix range modification so that setting ticks does not impact the range of the y axis. Only set ticks within given range
* Convert tone_graph to using matplotlib animation API
* Make the yaxis limits adapt to maximum values as they come 
* Make the dissonance look more like the moving note values instead of the bar graph
* Create a circular list for holding running histories
* Modify the dissonance calculation to take into account all the overtones of the tones
* Create a tone class that captures the harmonic spectrum of a sound.
* Put a log scale to the graph
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

## Ideas for the Distant Future
* Convert this into a viewable web page somehow
  * Could also post a video with the published code
* Create a program that decomposes instruments/sounds into synthesizer settings (like amplitudes of triangle/sine/etc. waves)
* Give users more control over the timbre of the tones