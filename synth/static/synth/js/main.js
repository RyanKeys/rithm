/*jshint esversion: 6 */

//Init new Polyphonic synth
var synth = new Tone.PolySynth(Tone.Synth, 8).toMaster();
//Keyboard note array
var notes = ["C", "D", "E", "F", "G", "A", "B"];
//empty html string
var html = "";
//Creates 2 octaves(2 containers of all piano key divs in notes array)
for (var octave = 0; octave < 2; octave++) {
  //Creates a piano key for each note in note array
  for (var i = 0; i < notes.length; ) {
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
var allowed = true;
function check_key_press(key) {
  for (var x = 0; x < qwerty.length; ) {
    var qwerty_index = qwerty[x];
    if (key.keyCode == qwerty_index && allowed) {
      console.log(qwerty[x]);
      synth.triggerAttack(piano_notes[x]);
      allowed = false;
    }
  }
}
function check_key_release(key) {
  for (var x = 0; x < qwerty.length; ) {
    allowed = true;
    synth.triggerRelease(piano_notes[x]);
  }
}
//Assign all lower functions to 'key_container' divs
document.getElementById("key_container").innerHTML = html;
//Changes black notes back to #333, and turn #ddd into white
function note_up(elem, is_sharp) {
  var note = elem.dataset.note;
  elem.style.background = is_sharp ? "#333" : "white";
  synth.triggerRelease(note, "16n");
}
//Trigger press animation and sound.
function note_down(elem, is_sharp) {
  var note = elem.dataset.note;
  elem.style.background = is_sharp ? "black" : "#ddd";
  synth.triggerAttack(note, "16n");
  //Prevents overlapping buttons from both pressing. ie: if your press C#, C or D won't also play.
  event.stopPropagation();
}
