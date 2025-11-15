"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, CheckCircle, XCircle, Power, PowerOff } from "lucide-react";

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
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Agents
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Manage and monitor all registered agents in the system
        </p>
      </div>

      {/* Agent Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {Object.entries(agents).map(([name, agent]) => (
          <Card key={name} className="relative">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="w-5 h-5" />
                    {name}
                  </CardTitle>
                  <CardDescription className="mt-2">
                    {agent.description}
                  </CardDescription>
                </div>
                <button
                  onClick={() => toggleAgent(name, !agent.enabled)}
                  className={`p-2 rounded-lg transition-colors ${
                    agent.enabled
                      ? "bg-green-100 dark:bg-green-900/20 text-green-600 hover:bg-green-200"
                      : "bg-gray-100 dark:bg-gray-700 text-gray-400 hover:bg-gray-200"
                  }`}
                  title={agent.enabled ? "Disable agent" : "Enable agent"}
                >
                  {agent.enabled ? (
                    <Power className="w-4 h-4" />
                  ) : (
                    <PowerOff className="w-4 h-4" />
                  )}
                </button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Status Badge */}
                <div className="flex items-center gap-2">
                  {agent.enabled ? (
                    <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400">
                      <CheckCircle className="w-3 h-3" />
                      Active
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-400">
                      <XCircle className="w-3 h-3" />
                      Inactive
                    </span>
                  )}
                  <span className="text-xs text-gray-500">v{agent.version}</span>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-gray-600 dark:text-gray-400">
                      Tasks Executed
                    </p>
                    <p className="text-lg font-semibold text-gray-900 dark:text-white">
                      {agent.stats.tasks_executed}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600 dark:text-gray-400">
                      Success Rate
                    </p>
                    <p className="text-lg font-semibold text-gray-900 dark:text-white">
                      {Math.round(agent.stats.success_rate * 100)}%
                    </p>
                  </div>
                </div>

                {/* Tools */}
                <div>
                  <p className="text-xs text-gray-600 dark:text-gray-400 mb-2">
                    Tools ({agent.tools.length})
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {agent.tools.slice(0, 3).map((tool) => (
                      <span
                        key={tool}
                        className="inline-flex items-center px-2 py-1 rounded text-xs bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400"
                      >
                        {tool}
                      </span>
                    ))}
                    {agent.tools.length > 3 && (
                      <span className="inline-flex items-center px-2 py-1 rounded text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-400">
                        +{agent.tools.length - 3} more
                      </span>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                  <button className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors">
                    View Details
                  </button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {Object.keys(agents).length === 0 && (
        <Card>
          <CardContent className="py-12 text-center">
            <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 dark:text-gray-400">
              No agents registered
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
