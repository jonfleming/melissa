
function log(message) {
    //console.log(message);
    document.getElementById('log').value += '\n' + message + '\n';
}

function replacer(k, v) { if (v === undefined) { return null; } return v; };

function vlog(voice) {
    return {voiceURI: voice.voiceURI, name: voice.name, lang: voice.lang, default:voice.default};  
}

function rem(time) {
    var now = Date.now();
    return (time-now) / 1000;
}

window.addEventListener('DOMContentLoaded', () => {
    const $micButton = $('#mic');
    const $result = $('#result');
    const $message = $('#message');
    const $input = $('.js-text');
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    let last = '';

    if (typeof SpeechRecognition === 'undefined') {
        $micButton.attr('src', micpng);
        $message.text("Unable to start speech recognition.");
    } else {
        let listening = false;
        const recognition = new SpeechRecognition();
        const start = () => {
            log('recognition.start');
            recognition.start();
            $micButton.attr('src', micgif);
            listening = true;
        };
        const stop = () => {
            log('recognition.stop');
            recognition.stop();
            $micButton.attr('src', micpng);
            listening = false;
        };
        const onResult = event => {
            log('onResult ' + event.results.length);
            $result.innerHTML = '';
            for (const res of event.results) {
                let p = '<p>' + res[0].transcript + '</p>';
                $result.append(p);
                if (res.isFinal) {
                    $result.last().addClass('final');
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
                    $input.val(text);
                    submitInput();
                    last = text;
                    $result.innerHTML = '';
                    stop();
                }
            }
        }

        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.onresult = onResult;
        recognition.onend = onSoundEnd;

        $micButton.click( function() {
            listening ? stop() : start();
        });

//        function sendInput(text) {
//            var req = new XMLHttpRequest();
//            var url = document.location.href + 'input?text=' + text;
//        
//            log.value += 'User: ' + text + '\n'; 
//            
//            req.onreadystatechange = function (e) {
//                log(`readystatechange: ${this.readyState} status: ${this.status}`);
//                if (this.readyState === 4 && this.status === 200) {
//                    var response = JSON.parse(this.responseText);
//                    if (Array.isArray(response.reply)) {
//                        response.reply.forEach(item => {
//                            log.value += '\nMelissa: ' + item;
//                            textToSpeech(item);
//                        });
//                    } else {
//                        log.value += 'No response for AI\n'; 
//                    }
//                    log.value += '\n'; 
//                }
//            }
//        
//            log(`Request: ${url}`);
//            req.responseType = 'text';
//            req.open('GET', url);
//            req.timeout = 5000;
//            req.send();
//        }
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
        $micButton.click();
    }

    // speak
    window.speechSynthesis.speak(utter);
}

function say(id) {
    var text = document.getElementById(id).value;
    log('say:' + text);
    textToSpeech(text);
}