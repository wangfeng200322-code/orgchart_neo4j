import React, {useState} from 'react'

export default function SearchForm({apiUrl, onResult}){
  const [name, setName] = useState('')
  const [err, setErr] = useState('')
  const onSearch = async (e)=>{
    e.preventDefault()
    if(!name) return setErr('Enter full name')
    setErr('')
    const res = await fetch(`${apiUrl}/employee?name=${encodeURIComponent(name)}`)
    const j = await res.json()
    onResult(j)
  }
  return (
    <div>
      <h3>Search Employee</h3>
      <form onSubmit={onSearch}>
        <input value={name} onChange={(e)=>setName(e.target.value)} placeholder='First Last' />
        <button type='submit'>Search</button>
      </form>
      <div style={{color:'red'}}>{err}</div>
    </div>
  )
}
