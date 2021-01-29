
function log(message) {
    //console.log(message);
    document.getElementById('log').value += '\n' + message + '\n';
}

function replacer(k, v) { if (v === undefined) { return null; } return v; };

function vlog(voice) {
    return {voiceURI: voice.voiceURI, name: voice.name, lang: voice.lang, default:voice.default};  
}

window.addEventListener('DOMContentLoaded', () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    let last = '';
    if (!isChrome) {
        $('#message').text("Speech Recognistion requires Chrome");
        return;
    }

    if (typeof SpeechRecognition === 'undefined') {
        $('#mic').attr('src', micpng);
        $('#message').text("Unable to start speech recognition.");
    } else {
        let listening = false;
        const recognition = new SpeechRecognition();
        const start = () => {
            log('recognition.start');
            recognition.start();
            $('#mic').attr('src', micgif);
            listening = true;
        };
        const stop = () => {
            log('recognition.stop');
            recognition.stop();
            $('#mic').attr('src', micpng);
            listening = false;
        };
        const onResult = event => {
            log('onResult ' + event.results.length);
            $('#result').innerHTML = '';
            for (const res of event.results) {
                let p = '<p>' + res[0].transcript + '</p>';
                $('#result').append(p);
                if (res.isFinal) {
                    $('#result').last().addClass('final');
                    log(`Transcript: ${res[0].transcript} final: ${res.isFinal}`);
                    stop();
                }
            }
        };
        const onSoundEnd = event => {
            log(`onSoundEnd last: ${last}`);
            const $final = $('.final');
            if ($final.length > 0) {
                const text = $final.children().last().text();
                if (text !== last) {
                    log(`sendInput final: ${text}`);
                    $('.js-text').val(text);
                    submitInput();
                    last = text;
                    $('#result').innerHTML = '';
                    stop();
                }
            }
        }

        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.onresult = onResult;
        recognition.onend = onSoundEnd;

        $('#mic').click( function() {
            listening ? stop() : start();
        });
    }
});


// list of languages is probably not loaded, wait for it
if (window.speechSynthesis.getVoices().length == 0) {
    window.speechSynthesis.addEventListener('voiceschanged', function() {
        log('voiceschanged');
        available_voices = window.speechSynthesis.getVoices();
    });
} else {
    log('no voiceschanged');
    available_voices = window.speechSynthesis.getVoices();
}

function textToSpeech(text) {
    console.log('Text:', text);
    //character.dynamicPlay({ do: 'look-right', say: 'Look over here.' });
    character.dynamicPlay({say: text})
}

function textToSpeech_speechapi(text) {
    // get all voices that browser offers
    var available_voices = window.speechSynthesis.getVoices();
    var english_voice = '';

    // find voice by language locale 'en-US'
    // if not then select the first voice
    for (var i = 0; i < available_voices.length; i++) {
        //    alert(available_voices[i].lang + ' ' + available_voices[i].name);
        if (available_voices[i].lang === 'en-US' && available_voices[i].name.indexOf('Zira') > -1) {
            english_voice = available_voices[i];
            break;
        }
    }
  
    if (english_voice === '') {
        english_voice = available_voices[0];
        log('english_voice' + JSON.stringify(vlog(english_voice), replacer, 4));
    }
  
    // new SpeechSynthesisUtterance object
    var utter = new SpeechSynthesisUtterance();
    utter.rate = 1;
    utter.pitch = 0.5;
    utter.text = text;
    utter.voice = english_voice;

    // event after text has been spoken
    utter.onend = function () {
        // resume listening
        $('#mic').click();
    }

    // speak
    window.speechSynthesis.speak(utter);
}

function say(id) {
    var text = document.getElementById(id).value;
    log('say:' + text);
    textToSpeech(text);
}

function voicePrompt() {
    // Prompt user to click mic
    const user = $('#user').val();
    let prompt = $('input.js-text').attr('placeholder');

    if (!isChrome) {
        prompt = 'My speech recognition only works on Google Chrome.  You will have to <emphasis>type</emphasis><break strength="weak"/>to <emphasis>speak</emphasis> to me.'
        $('#mic').prop('onclick', false)
        $('input.js-text').attr('placeholder','Type something and press Enter.');
    }
    textToSpeech(`Hello ${user}. ${prompt}`);
    //sayText(`Hello ${user}. ${prompt}`,2,1,3);
    document.cookie = 'name=' + user;
}

const user_cookie = document.cookie.split('; ').find(row => row.startsWith('name='));
if (user_cookie) {
    user = user_cookie.split('=')[1];
    $('#user').val(user);
}
