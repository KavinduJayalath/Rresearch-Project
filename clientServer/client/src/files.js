import React, { useState, useEffect } from 'react';
import download from 'downloadjs';
import axios from 'axios';
import { confirm } from "react-confirm-box";
import Card from "react-bootstrap/Card";

function App() {

  const [filesList, setFilesList] = useState([]);
  const [errorMsg, setErrorMsg] = useState('');

  const [select, setSelect] = useState("");

  useEffect(() => {
    const getFilesList = async () => {
      try {
        const { data } = await axios.get(`http://localhost:8060/violation/get`);
        setErrorMsg('');
        setFilesList(data);
      } catch (error) {
        error.response && setErrorMsg(error.response.data);
      }
    };

    getFilesList();
  }, []);

  const downloadFile = async (id, path, mimetype) => {
    try {
      const result = await axios.get(`http://localhost:8060/violation/download/${id}`, {
        responseType: 'blob'
      });
      const split = path.split('/');
      const filename = split[split.length - 1];
      setErrorMsg('');
      return download(result.data, filename, mimetype);
    } catch (error) {
      if (error.response && error.response.status === 400) {
        setErrorMsg('Error while downloading file. Try again later');
      }
    }
  };

  const deleteFile = async (id) => {
    console.log(id);

    const result1 = await confirm("Are you sure do you want to delete?");
    
    if (result1) {
      const result2 = await confirm("This file wil be permenantly deleted!!!");
      if(result2){
        axios.delete(`http://localhost:8060/violation/delete/${id}`).then((res) => {
            alert("Deleted");
            window.location.reload(false);
        }).catch((err) => {
            alert(err);
        });
      
      }
      
    }
  };

  return (
    <div className="container" align='center'>
      <br/><br/>
      <h1>Violations Detected</h1>
      <h1>count : {filesList.length}</h1>
      <div align='right' style={{width:'80rem'}}>
          <input type='text' placeholder='Search by date,time,location,cam' style={{width:'20rem', borderColor:'transparent'}}
          onChange={(e) => {
              setSelect(e.target.value);
          }}
          required />&nbsp;
      </div>
        <div align='cenetr'>
        <br/><br/>
        </div>
      {errorMsg && <p className="errorMsg">{errorMsg}</p>}
        <div className="row">
          {filesList.length > 0 ? (
            filesList.map(
              ({ _id, file_path, file_mimetype, time, location, camId, type}) => {
                if(select === ""){
                return(
                <div className="col-4" align="center" key={_id}>
                    <Card style={{ width: '15rem', backgroundColor: 'transparent' }}>
                    <Card.Body>
                        <Card.Text>
                        <img class="card-img-top" src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRUFW6qa0mtd1Q1jYqXwooAQCT3wboD5WSR6Q&usqp=CAU" alt="Card image" />
                        </Card.Text>
                        &nbsp;
                        <h5>{type}</h5>
                        <h7>{time}</h7>
                        &nbsp;
                        {/* <h7>{location}</h7> */}
                
                        &nbsp;
                        <table>
                          <tr>
                            <h7>{camId}</h7>
                          </tr>
                          <tr>
                          <a href={location} target='0'>
                          <button type="button" className="btn btn-success mt-2" style={{width: '13rem'}}>
                          Location
                          </button>
                          </a>
                          </tr>
                        </table>
                        &nbsp;
                        <button type="button" className="btn btn-primary" style={{width: '13rem'}} onClick={() => downloadFile(_id, file_path, file_mimetype)}>
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" className="bi bi-download" viewBox="0 0 16 16">
                            <path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"/>
                            <path d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"/>
                        </svg>&nbsp;&nbsp;&nbsp;Download File
                        </button>
                        &nbsp;
                        <button type="button" className="btn btn-danger mt-2" style={{width: '3rem'}} onClick={() => deleteFile(_id)}>
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-trash3" viewBox="0 0 16 16">
                          <path d="M6.5 1h3a.5.5 0 0 1 .5.5v1H6v-1a.5.5 0 0 1 .5-.5ZM11 2.5v-1A1.5 1.5 0 0 0 9.5 0h-3A1.5 1.5 0 0 0 5 1.5v1H2.506a.58.58 0 0 0-.01 0H1.5a.5.5 0 0 0 0 1h.538l.853 10.66A2 2 0 0 0 4.885 16h6.23a2 2 0 0 0 1.994-1.84l.853-10.66h.538a.5.5 0 0 0 0-1h-.995a.59.59 0 0 0-.01 0H11Zm1.958 1-.846 10.58a1 1 0 0 1-.997.92h-6.23a1 1 0 0 1-.997-.92L3.042 3.5h9.916Zm-7.487 1a.5.5 0 0 1 .528.47l.5 8.5a.5.5 0 0 1-.998.06L5 5.03a.5.5 0 0 1 .47-.53Zm5.058 0a.5.5 0 0 1 .47.53l-.5 8.5a.5.5 0 1 1-.998-.06l.5-8.5a.5.5 0 0 1 .528-.47ZM8 4.5a.5.5 0 0 1 .5.5v8.5a.5.5 0 0 1-1 0V5a.5.5 0 0 1 .5-.5Z"/>
                        </svg>
                        </button>
                    </Card.Body>
                    </Card><br/><br/><br/>
                </div>
                )
                }else if((time+location+camId).toLowerCase().includes(select.toLowerCase())){
                  return(
                    <div className="col-4" align="center" key={_id}>
                        <Card style={{ width: '15rem', backgroundColor: 'transparent' }}>
                        <Card.Body>
                            <Card.Text>
                            <img class="card-img-top" src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRUFW6qa0mtd1Q1jYqXwooAQCT3wboD5WSR6Q&usqp=CAU" alt="Card image" />
                            </Card.Text>
                            &nbsp;
                            <h7>{time}</h7>
                            &nbsp;
                            <h7>{location}</h7>
                            &nbsp;
                            <h7>{camId}</h7>
                            <button type="button" className="btn btn-primary" style={{width: '13rem'}} onClick={() => downloadFile(_id, file_path, file_mimetype)}>
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" className="bi bi-download" viewBox="0 0 16 16">
                                <path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"/>
                                <path d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"/>
                            </svg>&nbsp;&nbsp;&nbsp;Download File
                            </button>
                            &nbsp;
                            <button type="button" className="btn btn-danger mt-2" style={{width: '3rem'}} onClick={() => deleteFile(_id)}>
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-trash3" viewBox="0 0 16 16">
                              <path d="M6.5 1h3a.5.5 0 0 1 .5.5v1H6v-1a.5.5 0 0 1 .5-.5ZM11 2.5v-1A1.5 1.5 0 0 0 9.5 0h-3A1.5 1.5 0 0 0 5 1.5v1H2.506a.58.58 0 0 0-.01 0H1.5a.5.5 0 0 0 0 1h.538l.853 10.66A2 2 0 0 0 4.885 16h6.23a2 2 0 0 0 1.994-1.84l.853-10.66h.538a.5.5 0 0 0 0-1h-.995a.59.59 0 0 0-.01 0H11Zm1.958 1-.846 10.58a1 1 0 0 1-.997.92h-6.23a1 1 0 0 1-.997-.92L3.042 3.5h9.916Zm-7.487 1a.5.5 0 0 1 .528.47l.5 8.5a.5.5 0 0 1-.998.06L5 5.03a.5.5 0 0 1 .47-.53Zm5.058 0a.5.5 0 0 1 .47.53l-.5 8.5a.5.5 0 1 1-.998-.06l.5-8.5a.5.5 0 0 1 .528-.47ZM8 4.5a.5.5 0 0 1 .5.5v8.5a.5.5 0 0 1-1 0V5a.5.5 0 0 1 .5-.5Z"/>
                            </svg>
                            </button>
                        </Card.Body>
                        </Card><br/><br/><br/>
                    </div>
                    )
                }
              }
            )
          ) : (
            <p>No files found.</p>
          )}
        </div>
    </div>
  );
}

export default App;
