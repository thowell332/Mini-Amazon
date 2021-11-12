import {BrowserRouter as Router, Route} from 'react-router-dom'
import Home from './pages/Home';
import Login from './pages/Login';

function App() {
  return (
    <div className="App">
      <Router>
        <Route exact path="/" component={Home}/>
        <Route exact path="/login" component={Login}/>

      </Router>
    </div>
  );
}

export default App;
