"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle, XCircle, Power, PowerOff, ChevronRight } from "lucide-react";

interface Agent {
  name: string;
  description: string;
  version: string;
  enabled: boolean;
  tools: string[];
  stats: {
    tasks_executed: number;
    tasks_succeeded: number;
    tasks_failed: number;
    success_rate: number;
  };
}

export default function AgentsPage() {
  const [agents, setAgents] = useState<Record<string, Agent>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      const res = await fetch("/api/v1/agents/info");
      const data = await res.json();
      setAgents(data.agents || {});
    } catch (error) {
      console.error("Failed to fetch agents:", error);
    } finally {
      setLoading(false);
    }
  };

  const toggleAgent = async (agentName: string, enable: boolean) => {
    try {
      const endpoint = enable ? "enable" : "disable";
      await fetch(`/api/v1/agents/${agentName}/${endpoint}`, {
        method: "POST",
      });
      fetchAgents();
    } catch (error) {
      console.error(`Failed to ${enable ? "enable" : "disable"} agent:`, error);
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
      <div className="sticky top-0 bg-white border-b px-5 py-3 z-10">
        <h1 className="text-lg font-semibold text-gray-900">Agents</h1>
      </div>

      <div className="p-4">
        <Card>
          <CardHeader className="pb-2 pt-3 px-4">
            <CardTitle className="text-sm font-semibold">Registered Agents</CardTitle>
          </CardHeader>
          <CardContent className="px-0 pb-0">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-y bg-gray-50 text-gray-600">
                  <th className="text-left py-2 px-4 font-medium">Agent</th>
                  <th className="text-left py-2 px-4 font-medium">Status</th>
                  <th className="text-right py-2 px-4 font-medium">Tasks</th>
                  <th className="text-right py-2 px-4 font-medium">Success Rate</th>
                  <th className="text-left py-2 px-4 font-medium">Tools</th>
                  <th className="text-center py-2 px-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(agents).map(([name, agent]) => (
                  <tr key={name} className="border-b last:border-0 hover:bg-gray-50 transition-colors">
                    <td className="py-3 px-4">
                      <div>
                        <div className="font-medium text-gray-900 flex items-center gap-1.5">
                          {name}
                          <span className="text-[10px] text-gray-500 font-normal">v{agent.version}</span>
                        </div>
                        <div className="text-[10px] text-gray-500 mt-0.5 line-clamp-1">
                          {agent.description}
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      {agent.enabled ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-green-100 text-green-800">
                          <div className="w-1.5 h-1.5 rounded-full bg-green-600"></div>
                          Active
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-gray-100 text-gray-600">
                          <div className="w-1.5 h-1.5 rounded-full bg-gray-400"></div>
                          Inactive
                        </span>
                      )}
                    </td>
                    <td className="text-right py-3 px-4 text-gray-900 font-medium">
                      {agent.stats.tasks_executed}
                    </td>
                    <td className="text-right py-3 px-4">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium ${
                        agent.stats.success_rate >= 0.95 ? 'bg-green-100 text-green-800' :
                        agent.stats.success_rate >= 0.80 ? 'bg-blue-100 text-blue-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {Math.round(agent.stats.success_rate * 100)}%
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex flex-wrap gap-1">
                        {agent.tools.slice(0, 2).map((tool) => (
                          <span
                            key={tool}
                            className="inline-block px-1.5 py-0.5 rounded text-[10px] bg-blue-50 text-blue-700"
                          >
                            {tool}
                          </span>
                        ))}
                        {agent.tools.length > 2 && (
                          <span className="inline-block px-1.5 py-0.5 rounded text-[10px] bg-gray-100 text-gray-600">
                            +{agent.tools.length - 2}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center justify-center gap-1">
                        <button
                          onClick={() => toggleAgent(name, !agent.enabled)}
                          className={`p-1.5 rounded transition-colors ${
                            agent.enabled
                              ? "bg-green-100 text-green-600 hover:bg-green-200"
                              : "bg-gray-100 text-gray-400 hover:bg-gray-200"
                          }`}
                          title={agent.enabled ? "Disable" : "Enable"}
                        >
                          {agent.enabled ? <Power className="w-3.5 h-3.5" /> : <PowerOff className="w-3.5 h-3.5" />}
                        </button>
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

            {Object.keys(agents).length === 0 && (
              <div className="py-12 text-center text-sm text-gray-500">
                No agents registered
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
