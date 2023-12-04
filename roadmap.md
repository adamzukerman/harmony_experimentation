# Audio Application Ideas

## Steps to Making a Harmony Stabilization Application

## Ideas for Next Steps
1. Add another note

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
1. Learn how to generate sines
2. Learn how to interact with keyboard (examples/record_ram_to_disk.py)
3. Make a pitch graph that I can interact with
4. Control a note's frequency with keyboard inputs
5. See if I can graph a note frequency
6. Modify graph to be able to move the note while mouse is clicked
7. Make a graph that updates with time and shows note frequencies as well as previous frequencies

## Handwritten Notes


## Ideas Ideas fort the Distant Future
* Convert this into a viewable web page somehow
  * Could also post a video with the published code
* Create a program that decomposes instruments/sounds into synthesizer settings (like amplitudes of triangle/sine/etc. waves)