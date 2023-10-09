import './App.css';
import axios from 'axios';
import { Button } from 'semantic-ui-react'

function App() {

  async function metodoGet(){
    const data = await axios.get('http://localhost:4000/');
    console.log(data.data.message)
  }




  metodoGet();

    const metodoPost = () => {

      var json = {
        "nombre": "Juan",
        "apellido": "Perez"
      }
 
      axios.post("http://localhost:4000/saludo", JSON.stringify(json),  {headers:{ 'Content-Type':'multipart/form-data'}})
      .then(response => {
            console.log(response.data);
          }
        ).catch(error => {
          console.log(error);
        });
      }


  return (
    <div className="App">
      <header className="App-header">
      <Button inverted color='red' onClick={metodoPost}>
        POST
      </Button>
      </header>
    </div>
  );
}

export default App;
