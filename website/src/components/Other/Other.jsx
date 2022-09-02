import { Link, Outlet } from "react-router-dom";

import './Other.css'
import '../../App.css'


const Other = () => {

    return (
        <div className='Other'>
            <div className="cards">
                <Link to={'estimate'}><button>Cost Estimator</button></Link>
                <Link to={'usage'}><button>Feature Request</button></Link>
            </div>
            <Outlet />
        </div>
    )

}
export default Other;




