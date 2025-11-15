"use client";

import { useState, useCallback } from "react";
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  MiniMap,
} from "reactflow";
import "reactflow/dist/style.css";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { GitBranch, Loader2 } from "lucide-react";

const initialNodes: Node[] = [
  {
    id: "1",
    type: "default",
    data: { label: "TABLE: employees" },
    position: { x: 250, y: 0 },
    style: { background: "#3b82f6", color: "white" },
  },
  {
    id: "2",
    type: "default",
    data: { label: "TABLE: departments" },
    position: { x: 100, y: 100 },
    style: { background: "#3b82f6", color: "white" },
  },
  {
    id: "3",
    type: "default",
    data: { label: "VIEW: emp_dept_view" },
    position: { x: 250, y: 200 },
    style: { background: "#10b981", color: "white" },
  },
  {
    id: "4",
    type: "default",
    data: { label: "PROCEDURE: update_salary" },
    position: { x: 400, y: 100 },
    style: { background: "#8b5cf6", color: "white" },
  },
];

const initialEdges: Edge[] = [
  { id: "e1-2", source: "1", target: "2", label: "FK", animated: true },
  { id: "e1-3", source: "1", target: "3", animated: true },
  { id: "e2-3", source: "2", target: "3", animated: true },
  { id: "e1-4", source: "1", target: "4", animated: true },
];

export default function DependenciesPage() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [schemaName, setSchemaName] = useState("");
  const [loading, setLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const analyzeDependencies = async () => {
    if (!schemaName.trim()) return;

    setLoading(true);
    try {
      const res = await fetch("/api/v1/discovery/analyze-dependencies", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          schema_name: schemaName,
          include_system_objects: false,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        setAnalysisResult(data);
        // TODO: Transform API data into nodes and edges
      }
    } catch (error) {
      console.error("Dependency analysis failed:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-screen overflow-auto bg-gray-50">
      {/* Header */}
      <div className="sticky top-0 bg-white border-b px-5 py-3 z-10">
        <h1 className="text-lg font-semibold text-gray-900">Dependencies</h1>
      </div>

      <div className="p-4 space-y-3">
        {/* Analysis Form - Compact */}
        <Card>
          <CardContent className="p-3">
            <div className="flex gap-2">
              <input
                type="text"
                value={schemaName}
                onChange={(e) => setSchemaName(e.target.value)}
                placeholder="Enter schema name (e.g., HR, SALES)"
                className="flex-1 px-3 py-1.5 border border-gray-300 rounded text-xs bg-white text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={loading}
              />
              <button
                onClick={analyzeDependencies}
                disabled={loading || !schemaName.trim()}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded text-xs font-medium transition-colors"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    Analyzing
                  </>
                ) : (
                  <>
                    <GitBranch className="w-3.5 h-3.5" />
                    Analyze
                  </>
                )}
              </button>
            </div>
          </CardContent>
        </Card>

        {/* Main Content - Graph and Sidebar */}
        <div className="grid gap-3 lg:grid-cols-4">
          <div className="lg:col-span-3">
            <Card className="h-[calc(100vh-180px)]">
              <CardHeader className="pb-2 pt-3 px-4">
                <CardTitle className="text-sm font-semibold">Dependency Graph</CardTitle>
              </CardHeader>
              <CardContent className="h-[calc(100%-50px)] p-0">
                <ReactFlow
                  nodes={nodes}
                  edges={edges}
                  onNodesChange={onNodesChange}
                  onEdgesChange={onEdgesChange}
                  onConnect={onConnect}
                  fitView
                >
                  <Background />
                  <Controls />
                  <MiniMap />
                </ReactFlow>
              </CardContent>
            </Card>
          </div>

          <div className="space-y-3">
            {/* Stats - Compact */}
            <Card>
              <CardHeader className="pb-2 pt-3 px-3">
                <CardTitle className="text-xs font-semibold">Summary</CardTitle>
              </CardHeader>
              <CardContent className="px-3 pb-3 space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-[10px] text-gray-600">Objects</span>
                  <span className="text-xs font-semibold text-gray-900">{nodes.length}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-[10px] text-gray-600">Dependencies</span>
                  <span className="text-xs font-semibold text-gray-900">{edges.length}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-[10px] text-gray-600">Circular</span>
                  <span className="text-xs font-semibold text-green-600">0</span>
                </div>
              </CardContent>
            </Card>

            {/* Legend - Compact */}
            <Card>
              <CardHeader className="pb-2 pt-3 px-3">
                <CardTitle className="text-xs font-semibold">Legend</CardTitle>
              </CardHeader>
              <CardContent className="px-3 pb-3 space-y-1.5">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-blue-600 rounded"></div>
                  <span className="text-[10px] text-gray-600">Tables</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-green-600 rounded"></div>
                  <span className="text-[10px] text-gray-600">Views</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-purple-600 rounded"></div>
                  <span className="text-[10px] text-gray-600">Procedures</span>
                </div>
              </CardContent>
            </Card>

            {/* Migration Order - Compact */}
            <Card>
              <CardHeader className="pb-2 pt-3 px-3">
                <CardTitle className="text-xs font-semibold">Migration Order</CardTitle>
              </CardHeader>
              <CardContent className="px-3 pb-3 space-y-1.5">
                {initialNodes.map((node, idx) => (
                  <div
                    key={node.id}
                    className="flex items-center gap-2 p-1.5 bg-gray-50 rounded"
                  >
                    <span className="flex items-center justify-center w-4 h-4 bg-blue-600 text-white rounded-full text-[9px] font-bold flex-shrink-0">
                      {idx + 1}
                    </span>
                    <span className="text-[10px] text-gray-900 truncate">
                      {node.data.label}
                    </span>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
