import React, {useState, useEffect} from 'react'

export default function AdminKeyForm(){
  const [key, setKey] = useState('')
  const [masked, setMasked] = useState('')

  useEffect(()=>{
    const k = localStorage.getItem('orgchart_admin_api_key') || ''
    setKey(k)
    setMasked(k ? k.replace(/.(?=.{4})/g, '*') : '')
  }, [])

  const save = (e)=>{
    e.preventDefault()
    localStorage.setItem('orgchart_admin_api_key', key)
    setMasked(key ? key.replace(/.(?=.{4})/g, '*') : '')
    alert('Admin API key saved to localStorage (dev only)')
  }

  const clear = ()=>{
    localStorage.removeItem('orgchart_admin_api_key')
    setKey('')
    setMasked('')
  }

  return (
    <div>
      <h3>Admin API Key (dev only)</h3>
      <form onSubmit={save}>
        <input value={key} onChange={(e)=>setKey(e.target.value)} placeholder='Paste admin API key here' style={{width: '400px'}} />
        <button type='submit'>Save</button>
        <button type='button' onClick={clear} style={{marginLeft:8}}>Clear</button>
      </form>
      {masked && <div>Current key: <code>{masked}</code></div>}
      <p style={{fontSize:12,color:'#666'}}>This stores the admin API key in localStorage for the frontend to use when uploading CSVs (dev only). In production use a secure flow.</p>
    </div>
  )
}
