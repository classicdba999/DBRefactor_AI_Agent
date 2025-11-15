"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Plus, Play, CheckCircle, XCircle, Clock, Loader2, ChevronRight } from "lucide-react";

interface WorkflowItem {
  workflow_id: string;
  name: string;
  description: string;
  status: string;
  total_steps: number;
  created_at: string;
}

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<WorkflowItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchWorkflows();
  }, []);

  const fetchWorkflows = async () => {
    try {
      const res = await fetch("/api/v1/workflows/");
      const data = await res.json();
      setWorkflows(data);
    } catch (error) {
      console.error("Failed to fetch workflows:", error);
    } finally {
      setLoading(false);
    }
  };

  const executeWorkflow = async (workflowId: string) => {
    try {
      await fetch(`/api/v1/workflows/${workflowId}/execute`, {
        method: "POST",
      });
      setTimeout(fetchWorkflows, 1000);
    } catch (error) {
      console.error("Failed to execute workflow:", error);
    }
  };

  if (loading) {
    return (
      <div className="h-screen overflow-auto bg-gray-50">
        <div className="sticky top-0 bg-white border-b px-5 py-3">
          <div className="h-5 bg-gray-200 rounded w-24 animate-pulse"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen overflow-auto bg-gray-50">
      {/* Header */}
      <div className="sticky top-0 bg-white border-b px-5 py-3 z-10 flex items-center justify-between">
        <h1 className="text-lg font-semibold text-gray-900">Workflows</h1>
        <button className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-medium transition-colors">
          <Plus className="w-3.5 h-3.5" />
          New
        </button>
      </div>

      <div className="p-4">
        <Card>
          <CardHeader className="pb-2 pt-3 px-4">
            <CardTitle className="text-sm font-semibold">All Workflows</CardTitle>
          </CardHeader>
          <CardContent className="px-0 pb-0">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-y bg-gray-50 text-gray-600">
                  <th className="text-left py-2 px-4 font-medium">Workflow</th>
                  <th className="text-left py-2 px-4 font-medium">Status</th>
                  <th className="text-right py-2 px-4 font-medium">Steps</th>
                  <th className="text-left py-2 px-4 font-medium">Created</th>
                  <th className="text-center py-2 px-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {workflows.map((workflow) => (
                  <tr key={workflow.workflow_id} className="border-b last:border-0 hover:bg-gray-50 transition-colors">
                    <td className="py-3 px-4">
                      <div>
                        <div className="font-medium text-gray-900">
                          {workflow.name}
                        </div>
                        <div className="text-[10px] text-gray-500 mt-0.5 line-clamp-1">
                          {workflow.description}
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      {workflow.status === "completed" && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-green-100 text-green-800">
                          <CheckCircle className="w-3 h-3" />
                          Completed
                        </span>
                      )}
                      {workflow.status === "failed" && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-red-100 text-red-800">
                          <XCircle className="w-3 h-3" />
                          Failed
                        </span>
                      )}
                      {workflow.status === "running" && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-blue-100 text-blue-800">
                          <Loader2 className="w-3 h-3 animate-spin" />
                          Running
                        </span>
                      )}
                      {workflow.status === "pending" && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-gray-100 text-gray-600">
                          <Clock className="w-3 h-3" />
                          Pending
                        </span>
                      )}
                    </td>
                    <td className="text-right py-3 px-4 text-gray-900 font-medium">
                      {workflow.total_steps}
                    </td>
                    <td className="py-3 px-4 text-gray-600">
                      {new Date(workflow.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center justify-center gap-1">
                        {workflow.status === "pending" && (
                          <button
                            onClick={() => executeWorkflow(workflow.workflow_id)}
                            className="p-1.5 rounded bg-blue-100 text-blue-600 hover:bg-blue-200 transition-colors"
                            title="Execute"
                          >
                            <Play className="w-3.5 h-3.5" />
                          </button>
                        )}
                        <button
                          className="p-1.5 rounded bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors"
                          title="View Details"
                        >
                          <ChevronRight className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {workflows.length === 0 && (
              <div className="py-12 text-center text-sm text-gray-500">
                No workflows created yet
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
