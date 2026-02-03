/*jshint esversion: 6 */

//Init new Polyphonic synth
var synth = new Tone.PolySynth(Tone.Synth, 8).toDestination();

// Ensure audio context starts on user interaction
document.addEventListener('click', async () => {
  if (Tone.context.state !== 'running') {
    await Tone.start();
  }
}, { once: true });
//Keyboard note array
var notes = ["C", "D", "E", "F", "G", "A", "B"];
//empty html string
var html = "";
//Creates 2 octaves(2 containers of all piano key divs in notes array)
for (var octave = 0; octave < 2; octave++) {
  //Creates a piano key for each note in note array
  for (var i = 0; i < notes.length; i++) {
    var note = notes[i];
    var has_sharp = true;

    //Notes 'E' and 'B' don't have sharps. changes their "has_sharp" bool to false.
    if (note == "E" || note == "B") has_sharp = false;
    //Creates white piano keys
    html += `<div class='white_note' onmousedown='note_down(this,false)' onmouseup='note_up(this,false)' onmouseleave='note_up(this,false)' data-note='${note +
      (octave + 4)}'>`;
    //For notes except 'E' and 'B', adds black piano key after a white key
    if (has_sharp) {
      html += `<div class='black_note' onmousedown='note_down(this,true)' onmouseup='note_up(this,true)' onmouseleave='note_up(this,true)' data-note='${note +
        "#" +
        (octave + 4)}'></div>`;
    }
    //Add div to end of the note container to start next one
    html += `</div>`;
  }
}
window.addEventListener("keydown", check_key_press, false);
window.addEventListener("keyup", check_key_release, false);
var qwerty = [
  "65",
  "87",
  "83",
  "69",
  "68",
  "70",
  "84",
  "71",
  "89",
  "72",
  "85",
  "74"
];
var piano_notes = [
  "C4",
  "C#4",
  "D4",
  "D#4",
  "E4",
  "F4",
  "F#4",
  "G4",
  "G#4",
  "A4",
  "A#4",
  "B4"
];
var pressed_keys = {};
function check_key_press(key) {
  // Prevent default behavior and event bubbling
  key.preventDefault();
  
  for (var x = 0; x < qwerty.length; x++) {
    var qwerty_index = qwerty[x];
    if (key.keyCode == qwerty_index && !pressed_keys[key.keyCode]) {
      pressed_keys[key.keyCode] = true;
      synth.triggerAttack(piano_notes[x]);
      break; // Only trigger one note per keypress
    }
  }
}
function check_key_release(key) {
  for (var x = 0; x < qwerty.length; x++) {
    var qwerty_index = qwerty[x];
    if (key.keyCode == qwerty_index && pressed_keys[key.keyCode]) {
      pressed_keys[key.keyCode] = false;
      synth.triggerRelease(piano_notes[x]);
      break; // Only release the specific note
    }
  }
}
//Assign all lower functions to 'key_container' divs
document.getElementById("key_container").innerHTML = html;

// Debug: Log how many keys were created
console.log('Created', document.querySelectorAll('.white_note').length, 'white keys');
console.log('Created', document.querySelectorAll('.black_note').length, 'black keys');

// Safety: Release all notes if mouse leaves keyboard area
document.getElementById("key_container").addEventListener("mouseleave", function() {
  synth.releaseAll();
});

// Safety: Release all notes on window blur (user switches tabs/apps)
window.addEventListener("blur", function() {
  synth.releaseAll();
  pressed_keys = {}; // Reset keyboard state
});
//Changes black notes back to #333, and turn #ddd into white
function note_up(elem, is_sharp) {
  event.stopPropagation();
  console.log('Note up:', elem.dataset.note, 'is_sharp:', is_sharp);
  var note = elem.dataset.note;
  elem.style.background = is_sharp ? "#333" : "white";
  synth.triggerRelease(note);
}
//Trigger press animation and sound.
function note_down(elem, is_sharp) {
  //Prevents overlapping buttons from both pressing. ie: if your press C#, C or D won't also play.
  event.stopPropagation();
  console.log('Note down:', elem.dataset.note, 'is_sharp:', is_sharp);
  var note = elem.dataset.note;
  elem.style.background = is_sharp ? "black" : "#ddd";
  synth.triggerAttack(note);
}
