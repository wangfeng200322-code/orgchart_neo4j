import React from 'react';

const TreeNode = ({ node, level = 0 }) => {
  if (!node) return null;
  
  const hasChildren = node.children && node.children.length > 0;
  
  return (
    <div className={`tree-node level-${level}`}>
      <div className="node-content">
        <div className="employee-name">{node.name}</div>
        <div className="employee-title">{node.title}</div>
      </div>
      
      {hasChildren && (
        <div className="children">
          {node.children.map((child, index) => (
            <TreeNode key={child.id || index} node={child} level={level + 1} />
          ))}
        </div>
      )}
    </div>
  );
};

const OrgChart = ({ data }) => {
  if (!data) return null;
  
  return (
    <div className="org-chart">
      <TreeNode node={data} />
    </div>
  );
};

export default OrgChart;