import {BrowserRouter as Router, Route} from 'react-router-dom'
import Home from './pages/Home';
import Cart from './pages/Cart';

/**
 * App that lists routes and the pages that get routed to using react-router-dom package. This is rendered at the root of the DOM.
 *
 * @author Eric Doppelt
 */
function App() {
  return (
    <div className="App">
      <Router>
        <Route exact path="/" component={Home}/>
        <Route exact path="/cart" component={Cart}/>

      </Router>
    </div>
  );
}

export default App;
