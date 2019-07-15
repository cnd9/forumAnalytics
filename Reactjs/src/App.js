import logo from './logo.svg';
import './App.css';


import ReactDOM from 'react-dom';
import React, { Component } from 'react';
class Form1 extends Component{
  render(){
    return(
        <div class="form">
            <form action="/result" method="get">
                <input type="text" name="place" />
                <input type="submit" />
            </form>
        </div>
    );
  }
}
ReactDOM.render(
<Form1/>,
document.getElementById('root')
);

function App() {
  return (
    <div className="App">
      <div class="form">
        <form action="http://localhost:5000/rec14er/" method="get">
          Username: <input type="text" name="Username"/>
          <input type="submit" value="Submit"/>
        </form>
      </div>
    </div>

  );
}

export default App;
