import { React, useState } from 'react'

import './Estimate.css'
import '../../App.css'


const Estimate = () => {
    // Character Count
    const [input, setInput] = useState("");

    const inputHandler = (e) => {
        if (e.target.value === '') {
            const btn = document.getElementById('my-estimate').innerHTML = 'Estimate'
        }
        setInput(e.target.value);
    };

    function calculate() {
        const value = document.getElementById('char-input').value;
        const btn = document.getElementById('my-estimate')

        if (value != 0) {
            const selected = document.getElementById('service-list').value;
            btn.innerHTML = ""
            btn.innerHTML += "$ " + selected * value + " / month";
        }
        else {
            alert('Input Field Error!')
        }
    }
    return (
        <div className='Estimate'>
            <div className='service-card'>
                <select className="service-list" id="service-list">
                    <option value="0.000015">Standard Translation</option>
                    <option value="0.000060">Active Custome Translation</option>
                </select>
                <input id="char-input" type="number" min="0" max="9999999999" onChange={inputHandler}></input>
                <label>characters (per month)</label>
            </div>
            <div>
                <button className='my-estimate' id="my-estimate" onClick={calculate}>Estimate</button>
            </div>

        </div>
    )

}
export default Estimate;




