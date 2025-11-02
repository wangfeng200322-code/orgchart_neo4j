import React, {useState} from 'react'
import UploadForm from './components/UploadForm'
import SearchForm from './components/SearchForm'
import AdminKeyForm from './components/AdminKeyForm'
import OrgChart from './components/OrgChart'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function App(){
  const [data, setData] = useState(null)
  
  // Function to transform the API response into a tree structure
  const transformData = (apiData) => {
    if (!apiData || !apiData.nodes || apiData.nodes.length === 0) {
      return null
    }
    
    return apiData
  }
  
  const handleResult = (resultData) => {
    setData(transformData(resultData))
  }

  return (
    <div style={{padding: 20}}>
      <h1>OrgChart Demo</h1>
      <AdminKeyForm />
      <UploadForm apiUrl={API} />
      <hr />
      <SearchForm apiUrl={API} onResult={handleResult} />
      {data ? (
        <div>
          <h2>Org Chart</h2>
          <OrgChart data={data} />
        </div>
      ) : (
        <div style={{ margin: '20px 0', color: '#666' }}>
          Search for an employee to display the organizational chart
        </div>
      )}
    </div>
  )
}