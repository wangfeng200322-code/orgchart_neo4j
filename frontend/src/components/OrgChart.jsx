import React, { useCallback } from 'react';
import ReactFlow, { MiniMap, Controls, Background, useNodesState, useEdgesState, addEdge } from 'reactflow';
import 'reactflow/dist/style.css';
import EmployeeNode from './EmployeeNode';

const nodeTypes = {
  employee: EmployeeNode,
};

const OrgChart = ({ data }) => {
  const getNodeTree = useCallback((node, xPos = 0, yPos = 0, level = 0) => {
    if (!node) return { nodes: [], edges: [], width: 0 };
    
    const nodeId = `node-${node.id}`;
    const nodeElement = {
      id: nodeId,
      type: 'employee',
      position: { x: xPos, y: yPos },
      data: { 
        label: node.fullName,
        email: node.email,
        phone: node.phone,
        address: node.address
      },
    };
    
    let nodes = [nodeElement];
    let edges = [];
    let totalWidth = 150; // Width of current node
    
    if (node.children && node.children.length > 0) {
      let currentX = xPos - (node.children.length * 75);
      
      node.children.forEach((child, index) => {
        const childResult = getNodeTree(child, currentX + (index * 150), yPos + 150, level + 1);
        nodes = [...nodes, ...childResult.nodes];
        edges = [...edges, ...childResult.edges];
        edges.push({
          id: `edge-${node.id}-${child.id}`,
          source: nodeId,
          target: `node-${child.id}`,
          animated: true,
          style: { stroke: '#007bff' }
        });
        totalWidth += childResult.width;
      });
    }
    
    return { nodes, edges, width: totalWidth };
  }, []);
  
  const initialData = useCallback(() => {
    if (!data) return { nodes: [], edges: [] };
    
    const result = getNodeTree(data, 0, 0);
    return { nodes: result.nodes, edges: result.edges };
  }, [data, getNodeTree]);
  
  const [nodes, setNodes, onNodesChange] = useNodesState(initialData().nodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialData().edges);
  
  const onConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds)), []);

  if (!data) return null;

  return (
    <div style={{ width: '100%', height: '600px', border: '1px solid #ccc' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        fitView
      >
        <Controls />
        <MiniMap />
        <Background variant="dots" gap={12} size={1} />
      </ReactFlow>
    </div>
  );
};

export default OrgChart;