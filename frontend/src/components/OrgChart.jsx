import React, { useCallback } from 'react';
import { 
  ReactFlow, 
  MiniMap, 
  Controls, 
  Background, 
  useNodesState, 
  useEdgesState, 
  addEdge,
  MarkerType
} from 'reactflow';
import 'reactflow/dist/style.css';
import EmployeeNode from './EmployeeNode';

const nodeTypes = {
  employee: EmployeeNode,
};

const OrgChart = ({ data }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  // Transform API data to React Flow nodes and edges
  const transformData = useCallback((apiData) => {
    if (!apiData || !apiData.nodes || apiData.nodes.length === 0) {
      return { nodes: [], edges: [] };
    }

    // Create nodes
    const nodes = apiData.nodes.map((node, index) => ({
      id: node.id.toString(),
      type: 'employee',
      position: { x: 0, y: 0 }, // Will be positioned later
      data: { 
        label: node.fullName,
        email: node.email,
        phone: node.phone,
        firstName: node.firstName,
        lastName: node.lastName,
        address: node.address
      },
    }));

    // Create edges
    const edges = apiData.links.map((link, index) => ({
      id: `edge-${index}`,
      source: link.from_id.toString(),
      target: link.to_id.toString(),
      markerEnd: {
        type: MarkerType.ArrowClosed,
      },
      type: 'smoothstep',
    }));

    return { nodes, edges };
  }, []);

  // Auto-layout the nodes in a tree structure
  const layoutNodes = useCallback((nodes, edges) => {
    if (nodes.length === 0) return nodes;

    // Create a map of nodes by ID
    const nodeMap = {};
    nodes.forEach(node => {
      nodeMap[node.id] = { ...node };
    });

    // Find root nodes (nodes that are not targets of any edge)
    const targetIds = new Set(edges.map(edge => edge.target));
    const rootIds = nodes.filter(node => !targetIds.has(node.id)).map(node => node.id);

    // Simple tree layout algorithm
    const visited = new Set();
    let yLevel = 0;
    const levelHeight = 200;
    const nodeWidth = 250;
    
    const positionNode = (nodeId, x, y) => {
      if (visited.has(nodeId)) return x;
      
      visited.add(nodeId);
      nodeMap[nodeId].position = { x, y };
      
      // Find children of this node
      const childEdges = edges.filter(edge => edge.source === nodeId);
      const childIds = childEdges.map(edge => edge.target);
      
      // Position children
      let currentX = x - (childIds.length - 1) * nodeWidth / 2;
      childIds.forEach(childId => {
        currentX = positionNode(childId, currentX, y + levelHeight) + nodeWidth;
      });
      
      return currentX;
    };
    
    // Position all root nodes
    let startX = 0;
    rootIds.forEach(rootId => {
      startX = positionNode(rootId, startX, 0) + nodeWidth * 2;
    });
    
    return Object.values(nodeMap);
  }, []);

  // Initialize the chart when data changes
  React.useEffect(() => {
    const { nodes: initialNodes, edges: initialEdges } = transformData(data);
    const positionedNodes = layoutNodes(initialNodes, initialEdges);
    setNodes(positionedNodes);
    setEdges(initialEdges);
  }, [data, transformData, layoutNodes, setNodes, setEdges]);

  const onConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds)), [setEdges]);

  // Custom node renderer
  const nodeColor = (node) => {
    switch (node.type) {
      case 'employee': return '#007bff';
      default: return '#ffffff';
    }
  };

  return (
    <div style={{ width: '100%', height: '70vh' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
        nodeTypes={nodeTypes}
        attributionPosition="bottom-left"
      >
        <Controls />
        <MiniMap nodeColor={nodeColor} nodeStrokeWidth={3} zoomable pannable />
        <Background color="#aaa" gap={16} />
      </ReactFlow>
    </div>
  );
};

export default OrgChart;