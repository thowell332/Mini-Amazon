import {BrowserRouter as Router, Route} from 'react-router-dom'
import Home from './pages/Home';
import Cart from './pages/Cart';
import {React, useState} from 'react';

/**
 * App that lists routes and the pages that get routed to using react-router-dom package. This is rendered at the root of the DOM.
 *
 * @author Eric Doppelt
 */
function App() {

  // Set user ID once they log in.
  const [userId, setUserID] = useState('');

  return (
    <div className="App">
      <Router>
        <Route exact path="/" render={() => <Home/>}/>
        <Route exact path="/cart" render={() => <Cart/>}/>
      </Router>
    </div>
  );
}

export default App;
