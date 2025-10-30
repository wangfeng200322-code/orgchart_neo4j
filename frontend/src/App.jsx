import React, {useState} from 'react'
import UploadForm from './components/UploadForm'
import SearchForm from './components/SearchForm'

const API = process.env.REACT_APP_API_URL || 'http://localhost:8000'

export default function App(){
  const [data, setData] = useState(null)
  return (
    <div style={{padding: 20}}>
      <h1>OrgChart Demo</h1>
      <UploadForm apiUrl={API} />
      <hr />
      <SearchForm apiUrl={API} onResult={setData} />
      {data && (
        <div>
          <h2>Org Chart</h2>
          <pre>{JSON.stringify(data, null, 2)}</pre>
        </div>
      )}
    </div>
  )
}
