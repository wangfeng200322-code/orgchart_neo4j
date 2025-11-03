import React, {useState} from 'react'
import UploadForm from './components/UploadForm'
import SearchForm from './components/SearchForm'
import AdminKeyForm from './components/AdminKeyForm'
import OrgChart from './components/OrgChart'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function App(){
  const [data, setData] = useState(null)
  const [searchedName, setSearchedName] = useState('')
  
  // Function to transform the API response into a tree structure
  const transformData = (apiData) => {
    if (!apiData || !apiData.nodes || apiData.nodes.length === 0) {
      return null
    }
    
    // Create a map of all nodes by their ID
    const nodeMap = {}
    apiData.nodes.forEach(node => {
      nodeMap[node.id] = {
        ...node,
        children: []
      }
    })
    
    // Build the tree structure by connecting nodes based on links
    apiData.links.forEach(link => {
      const parent = nodeMap[link.from_id]
      const child = nodeMap[link.to_id]
      
      if (parent && child) {
        parent.children.push(child)
      }
    })
    
    // Find the root node (the one we searched for)
    // It should be the first node in the array or we can find it by checking
    // which node doesn't have any incoming links
    return nodeMap[apiData.nodes[0].id]
  }
  
  const handleResult = (resultData, name) => {
    setData(transformData(resultData))
    setSearchedName(name)
  }

  return (
    <div style={{padding: 20}}>
      <h1>OrgChart Demo</h1>
      <AdminKeyForm />
      <UploadForm apiUrl={API} />
      <hr />
      <SearchForm apiUrl={API} onResult={handleResult} />
      {data === null && searchedName ? (
        <div style={{ margin: '20px 0', color: '#666' }}>
          No employee found with the name "{searchedName}". Please check the name and try again.
        </div>
      ) : data ? (
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