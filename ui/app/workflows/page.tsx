"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Workflow, Plus, Play, CheckCircle, XCircle, Clock, Loader2 } from "lucide-react";

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
      // Refresh workflows
      setTimeout(fetchWorkflows, 1000);
    } catch (error) {
      console.error("Failed to execute workflow:", error);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case "failed":
        return <XCircle className="w-5 h-5 text-red-600" />;
      case "running":
        return <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400";
      case "failed":
        return "bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400";
      case "running":
        return "bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400";
      default:
        return "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-400";
    }
  };

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/4 mb-4"></div>
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-8"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Workflows
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Create and manage migration workflows
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors">
          <Plus className="w-4 h-4" />
          New Workflow
        </button>
      </div>

      {/* Workflows List */}
      <div className="space-y-4">
        {workflows.map((workflow) => (
          <Card key={workflow.workflow_id}>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <CardTitle className="flex items-center gap-2">
                    <Workflow className="w-5 h-5" />
                    {workflow.name}
                  </CardTitle>
                  <CardDescription className="mt-2">
                    {workflow.description}
                  </CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <span
                    className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(
                      workflow.status
                    )}`}
                  >
                    {getStatusIcon(workflow.status)}
                    {workflow.status}
                  </span>
                  {workflow.status === "pending" && (
                    <button
                      onClick={() => executeWorkflow(workflow.workflow_id)}
                      className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                      title="Execute workflow"
                    >
                      <Play className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                    </button>
                  )}
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-6 text-sm text-gray-600 dark:text-gray-400">
                <div>
                  <span className="font-medium">{workflow.total_steps}</span> steps
                </div>
                <div>
                  Created{" "}
                  {new Date(workflow.created_at).toLocaleDateString()}
                </div>
                <div className="ml-auto">
                  <button className="text-blue-600 hover:text-blue-700 font-medium">
                    View Details →
                  </button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {workflows.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center">
            <Workflow className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              No workflows created yet
            </p>
            <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors">
              Create Your First Workflow
            </button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
