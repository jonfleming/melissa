
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

window.addEventListener("DOMContentLoaded", () => {
    const button = document.getElementById("button");
    const result = document.getElementById("result");
    const transcript = document.getElementById("transcript");
    const main = document.getElementsByTagName("main")[0];

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    let last = '';

    if (typeof SpeechRecognition === "undefined") {
        button.remove();
        const message = document.getElementById("message");
        message.removeAttribute("hidden");
        message.setAttribute("aria-hidden", "false");
    } else {
        let listening = false;
        const recognition = new SpeechRecognition();
        const start = () => {
            log("recognition.start");
            recognition.start();
            button.textContent = "Stop listening";
            main.classList.add("speaking");
            listening = true;
        };
        const stop = () => {
            log("recognition.stop");
            recognition.stop();
            button.textContent = "Start listening";
            main.classList.remove("speaking");
            listening = false;
        };
        const onResult = event => {
            log("onResult " + event.results.length);
            result.innerHTML = "";
            for (const res of event.results) {
                const text = document.createTextNode(res[0].transcript);                
                const p = document.createElement("p");
                if (res.isFinal) {
                    p.classList.add("final");
                }                
                p.appendChild(text);
                result.appendChild(p);                
                log(`Transcript: ${res[0].transcript} final: ${res.isFinal}`);
            }
        };
        const onsoundend = event => {
            log(`onSoundEnd last: ${last}`);
            var final = document.getElementsByClassName("final");
            if (final.length > 0) {
                var text = final[0].innerText;
                if (text !== last) {
                    log(`sendInput final: ${text}`);
                    sendInput(text);
                    last = text;
                    result.innerHTML = "";
                    stop();
                }
            }
        }

        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.addEventListener("result", onResult);
        recognition.addEventListener("result", onsoundend);

        button.addEventListener("click", () => {
            listening ? stop() : start();
        });

        function sendInput(text) {
            var req = new XMLHttpRequest();
            var url = document.location.href + "input?text=" + text;
        
            transcript.value += 'User: ' + text + '\n'; 
            
            req.onreadystatechange = function (e) {
                log(`readystatechange: ${this.readyState} status: ${this.status}`);
                if (this.readyState === 4 && this.status === 200) {
                    var response = JSON.parse(this.responseText);
                    if (Array.isArray(response.reply)) {
                        response.reply.forEach(item => {
                            transcript.value += '\nMelissa: ' + item;
                            textToSpeech(item);
                        });
                    } else {
                        transcript.value += 'No response for AI\n'; 
                    }
                    transcript.value += '\n'; 
                }
            }
        
            log(`Request: ${url}`);
            req.responseType = 'text';
            req.open("GET", url);
            req.timeout = 5000;
            req.send();
        }
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

    // find voice by language locale "en-US"
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
        document.getElementById("button").click();
    }

    // speak
    window.speechSynthesis.speak(utter);
}

function say(id) {
    var text = document.getElementById(id).value;
    log('say:' + text);
    textToSpeech(text);
}