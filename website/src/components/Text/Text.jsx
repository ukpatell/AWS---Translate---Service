import { React, useState } from 'react'
import axios from 'axios'
import { Controls } from '../components'

import '../../App.css'
import './Text.css'
import secrets from '../../secrets.json'

const Text = () => {

    // Character Count
    const [input, setInput] = useState("");

    const inputHandler = (e) => {
        if (e.target.value === '') {
            document.getElementById('copy-btn').innerHTML = 'Copy'
            document.getElementById('output-box').innerHTML = "";
        }
        setInput(e.target.value);
    };

    // Copy to Clipboard Function
    function copyToClipboard(e) {
        // navigator.clipboard.writeText(document.getElementById('output-box').innerHTML)
        // document.getElementById('copy-btn').innerHTML = 'Copied'
        var textToCopy = document.getElementById('output-box').innerHTML;
        if (navigator.clipboard && window.isSecureContext) {
        document.getElementById('copy-btn').innerHTML = 'Copied'

            // navigator clipboard api method'
            return navigator.clipboard.writeText(textToCopy);
        } else {
            // text area method
            let textArea = document.createElement("textarea");
            textArea.value = textToCopy;
            // make the textarea out of viewport
            textArea.style.position = "fixed";
            textArea.style.left = "-999999px";
            textArea.style.top = "-999999px";
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            document.getElementById('copy-btn').innerHTML = 'Copied'
            
            return new Promise((res, rej) => {
                // here the magic happens
                document.execCommand('copy') ? res() : rej();
                textArea.remove();
            });
        }
    }


    // Translates The Text
    const translateText = () => {
        const txt = document.getElementById('text-area').value;
        const src = document.getElementById('from-lang-picker').value;
        const tgt = document.getElementById('to-lang-picker').value;
        const output = document.getElementById('output-box');

        if (txt.length > 2) {
            const api = secrets['TranslateServiceStack']['APIURLTRANSLATETEXT']
            const data = {
                text: txt,
                source: src,
                target: tgt
            };

            axios
                .post(api, data)
                .then((response) => {
                    output.innawserHTML = ""
                    output.innerHTML = response['data'];
                })
                .catch((error) => {
                    console.log(console.error);
                })
        }
        else {
            alert('Please provide input greater than length: 2')
        }


    }

    return (
        <div className="Text">
            < Controls />
            <div className="output-box">
                <div className="t-from">
                    <div className="translate-from-box">
                        <textarea className="translate-from-input text-result-box" placeholder="Enter your text"
                            onChange={inputHandler} maxLength="5000" id='text-area' onKeyPress={(e) => e.key === 'Enter' && translateText()}></textarea>
                        <div id="the-count">
                            <span id="current">{input.length}</span>
                            <span id="maximum">/ 5000</span>
                        </div>
                    </div>
                </div>
                <div className="t-to">
                    <div className="translate-to-box">
                        <textarea className="translate-to-result text-result-box"
                            placeholder="Your translated text will appear here"
                            readOnly="readOnly" id="output-box"
                        >
                        </textarea>
                        <div className="translate-to-response">
                            <button id='copy-btn' className="copy-btn" onClick={copyToClipboard}>Copy</button>
                            {/* <button id='copy-btn' className="copy-btn" onClick={copyToClipboard}>Voice</button> */}
                        </div>
                    </div>
                </div>
            </div>
            <button className='translateBtn' onClick={translateText}>
                Translate
            </button>
        </div>
    )
}
export default Text;




