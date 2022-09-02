import { React } from 'react';
import { Route, Routes, BrowserRouter as Router } from 'react-router-dom';
import { Controls, Document, Estimate, Navbar, Other, Text, Image, NotFound } from './components/components'

import './App.css'

const App = () => {

  return (
    <>
      <Router>
        <Navbar />
        <div className='App'>
          <Routes>
            <Route index element={<Text />} />
            <Route exact path="/document" element={<Document />} />
            <Route exact path="/other" element={<Other />}>
              <Route index element={<Estimate />} />
              <Route path="estimate" element={<Estimate />} />
              <Route path="usage" element={<Document />} />
            </Route>
            <Route exact path="/image" element={<Image />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </div>
      </Router>
    </>

  );
}

export default App;

