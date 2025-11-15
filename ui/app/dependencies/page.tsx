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
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { GitBranch, Loader2, AlertCircle, CheckCircle } from "lucide-react";

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
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Dependency Analysis
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Visualize and analyze database object dependencies
        </p>
      </div>

      {/* Analysis Form */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Analyze Dependencies</CardTitle>
          <CardDescription>
            Build dependency graph for schema objects
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="flex-1">
              <input
                type="text"
                value={schemaName}
                onChange={(e) => setSchemaName(e.target.value)}
                placeholder="Enter schema name (e.g., HR, SALES)"
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={loading}
              />
            </div>
            <button
              onClick={analyzeDependencies}
              disabled={loading || !schemaName.trim()}
              className="flex items-center gap-2 px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-colors"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <GitBranch className="w-4 h-4" />
                  Analyze
                </>
              )}
            </button>
          </div>
        </CardContent>
      </Card>

      {/* Dependency Graph */}
      <div className="grid gap-6 lg:grid-cols-3 mb-8">
        <div className="lg:col-span-2">
          <Card className="h-[600px]">
            <CardHeader>
              <CardTitle>Dependency Graph</CardTitle>
              <CardDescription>
                Interactive visualization of object dependencies
              </CardDescription>
            </CardHeader>
            <CardContent className="h-[500px] p-0">
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

        <div className="space-y-6">
          {/* Migration Order */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
                Migration Order
              </CardTitle>
              <CardDescription>
                Recommended order for object creation
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {initialNodes.map((node, idx) => (
                  <div
                    key={node.id}
                    className="flex items-center gap-3 p-2 bg-gray-50 dark:bg-gray-800 rounded"
                  >
                    <span className="flex items-center justify-center w-6 h-6 bg-blue-600 text-white rounded-full text-xs font-bold">
                      {idx + 1}
                    </span>
                    <span className="text-sm text-gray-900 dark:text-white">
                      {node.data.label}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Statistics */}
          <Card>
            <CardHeader>
              <CardTitle>Analysis Summary</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  Total Objects
                </span>
                <span className="font-semibold text-gray-900 dark:text-white">
                  {nodes.length}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  Dependencies
                </span>
                <span className="font-semibold text-gray-900 dark:text-white">
                  {edges.length}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  Circular Dependencies
                </span>
                <span className="font-semibold text-green-600">0</span>
              </div>
            </CardContent>
          </Card>

          {/* Legend */}
          <Card>
            <CardHeader>
              <CardTitle>Legend</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-blue-600 rounded"></div>
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  Tables
                </span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-green-600 rounded"></div>
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  Views
                </span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-purple-600 rounded"></div>
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  Procedures/Functions
                </span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
