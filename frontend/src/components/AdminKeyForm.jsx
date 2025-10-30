import React, {useState, useEffect} from 'react'

export default function AdminKeyForm(){
  const [key, setKey] = useState('')
  const [masked, setMasked] = useState('')
  const [useSession, setUseSession] = useState(false)

  useEffect(()=>{
    const kLocal = localStorage.getItem('orgchart_admin_api_key') || ''
    const kSession = sessionStorage.getItem('orgchart_admin_api_key') || ''
    if(kSession){
      setKey(kSession)
      setUseSession(true)
      setMasked(kSession ? kSession.replace(/.(?=.{4})/g, '*') : '')
    } else if(kLocal){
      setKey(kLocal)
      setUseSession(false)
      setMasked(kLocal ? kLocal.replace(/.(?=.{4})/g, '*') : '')
    }
  }, [])

  const save = (e)=>{
    e.preventDefault()
    if(useSession){
      sessionStorage.setItem('orgchart_admin_api_key', key)
      localStorage.removeItem('orgchart_admin_api_key')
    } else {
      localStorage.setItem('orgchart_admin_api_key', key)
      sessionStorage.removeItem('orgchart_admin_api_key')
    }
    setMasked(key ? key.replace(/.(?=.{4})/g, '*') : '')
    alert('Admin API key saved (dev only)')
  }

  const clear = ()=>{
    localStorage.removeItem('orgchart_admin_api_key')
    sessionStorage.removeItem('orgchart_admin_api_key')
    setKey('')
    setMasked('')
  }

  return (
    <div>
      <h3>Admin API Key (dev only)</h3>
      <form onSubmit={save}>
        <input value={key} onChange={(e)=>setKey(e.target.value)} placeholder='Paste admin API key here' style={{width: '420px'}} />
        <label style={{marginLeft:8}}>
          <input type='checkbox' checked={useSession} onChange={(e)=>setUseSession(e.target.checked)} /> Use sessionStorage (clears on tab close)
        </label>
        <div style={{marginTop:8}}>
          <button type='submit'>Save</button>
          <button type='button' onClick={clear} style={{marginLeft:8}}>Clear</button>
        </div>
      </form>
      {masked ? <div style={{marginTop:8}}>Current key: <code>{masked}</code></div> : <div style={{marginTop:8,color:'#b00'}}>No admin key saved — uploads will be blocked unless a key is provided.</div>}
      <p style={{fontSize:12,color:'#666'}}>This stores the admin API key in localStorage or sessionStorage for development convenience. Do not use in production.</p>
    </div>
  )
}
