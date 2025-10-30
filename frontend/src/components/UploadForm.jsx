import React, {useState} from 'react'

export default function UploadForm({apiUrl}){
  const [file, setFile] = useState(null)
  const [msg, setMsg] = useState('')
  const onSubmit = async (e)=>{
    e.preventDefault()
    if(!file) return setMsg('Choose a CSV file')
    const fd = new FormData()
    fd.append('file', file)
    const res = await fetch(apiUrl + '/upload', {method: 'POST', body: fd})
    const j = await res.json()
    setMsg(JSON.stringify(j))
  }
  return (
    <div>
      <h3>Admin CSV Upload</h3>
      <form onSubmit={onSubmit}>
        <input type='file' accept='.csv' onChange={(e)=>setFile(e.target.files[0])} />
        <button type='submit'>Upload</button>
      </form>
      <div>{msg}</div>
    </div>
  )
}
