import { Link } from "react-router-dom";
import React from 'react'

import './Navbar.css'
import '../../App.css'
import { getAllByTitle } from "@testing-library/react";

const Navbar = () => {
    return (
        <div className="Navbar">
            <header>
                <Link to={'/'} className="logo" key='Text' id="switcher">Translate</Link>
                <div className="mean-toggle"></div>
                <nav>
                    <ul>
                        <li><Link to="/">Text</Link></li>
                        <li><Link to="/document" >Document</Link></li>
                        {/* <li><Link to="/image" >Image</Link></li> */}
                        {/* <li><Link to="/other">Other</Link></li> */}
                        {/* <li><a >Settings</a></li> */}
                    </ul>
                </nav>
                <div className="clear"></div>
            </header>
        </div>
    )
}
export default Navbar;