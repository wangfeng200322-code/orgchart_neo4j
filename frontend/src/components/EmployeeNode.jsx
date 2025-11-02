import React from 'react';
import { Handle, Position } from 'reactflow';

const EmployeeNode = ({ data }) => {
  return (
    <div style={{
      padding: '15px',
      border: '2px solid #007bff',
      borderRadius: '10px',
      backgroundColor: 'white',
      width: '220px',
      boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
      fontFamily: 'Arial, sans-serif'
    }}>
      <Handle
        type="target"
        position={Position.Top}
        style={{ 
          background: '#007bff',
          width: '12px',
          height: '12px',
          borderRadius: '50%'
        }}
      />
      
      <div style={{ 
        textAlign: 'center',
        marginBottom: '10px'
      }}>
        <div style={{ 
          fontWeight: 'bold', 
          fontSize: '16px',
          color: '#333',
          marginBottom: '5px'
        }}>
          {data.label}
        </div>
        
        {data.email && (
          <div style={{ 
            fontSize: '14px',
            color: '#666',
            marginBottom: '3px'
          }}>
            📧 {data.email}
          </div>
        )}
        
        {data.phone && (
          <div style={{ 
            fontSize: '14px',
            color: '#666',
            marginBottom: '3px'
          }}>
            📞 {data.phone}
          </div>
        )}
        
        {data.address && (
          <div style={{ 
            fontSize: '13px',
            color: '#888',
            marginTop: '5px',
            fontStyle: 'italic'
          }}>
            📍 {data.address}
          </div>
        )}
      </div>
      
      <Handle
        type="source"
        position={Position.Bottom}
        style={{ 
          background: '#007bff',
          width: '12px',
          height: '12px',
          borderRadius: '50%'
        }}
      />
    </div>
  );
};

export default EmployeeNode;