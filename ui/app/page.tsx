"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, Database, Workflow, TrendingUp, CheckCircle, Clock, XCircle } from "lucide-react";

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalAgents: 0,
    activeWorkflows: 0,
    completedMigrations: 0,
    successRate: 0,
  });

  useEffect(() => {
    fetch("/api/v1/agents/info")
      .then((res) => res.json())
      .then((data) => {
        setStats({
          totalAgents: data.total_agents || 0,
          activeWorkflows: 0,
          completedMigrations: 0,
          successRate: 95,
        });
      })
      .catch(console.error);
  }, []);

  return (
    <div className="h-screen overflow-auto bg-gray-50">
      {/* Compact Header */}
      <div className="sticky top-0 bg-white border-b px-5 py-3 z-10">
        <h1 className="text-lg font-semibold text-gray-900">Dashboard</h1>
      </div>

      <div className="p-4 space-y-3">
        {/* Compact Stats */}
        <div className="grid gap-3 grid-cols-2 lg:grid-cols-4">
          {[
            { label: "Agents", value: stats.totalAgents, icon: Activity, color: "blue", trend: "+2" },
            { label: "Workflows", value: stats.activeWorkflows, icon: Workflow, color: "purple", trend: "0" },
            { label: "Migrations", value: stats.completedMigrations, icon: Database, color: "green", trend: "+12" },
            { label: "Success Rate", value: `${stats.successRate}%`, icon: TrendingUp, color: "orange", trend: "+5%" },
          ].map((stat, i) => (
            <Card key={i} className={`border-l-4 border-l-${stat.color}-500`}>
              <CardContent className="p-3">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-xs text-gray-600">{stat.label}</p>
                    <p className="text-xl font-bold mt-0.5">{stat.value}</p>
                    <p className="text-xs text-gray-500 mt-0.5">{stat.trend}</p>
                  </div>
                  <stat.icon className={`w-4 h-4 text-${stat.color}-500`} />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid gap-3 lg:grid-cols-3">
          {/* Activity */}
          <Card className="lg:col-span-2">
            <CardHeader className="pb-2 pt-3 px-4">
              <CardTitle className="text-sm font-semibold">Recent Activity</CardTitle>
            </CardHeader>
            <CardContent className="px-4 pb-3">
              <div className="space-y-2">
                {[
                  { type: "success", agent: "DB Discoverer", action: "Schema discovery completed", time: "2m" },
                  { type: "running", agent: "Workflow Engine", action: "Migration workflow in progress", time: "5m" },
                  { type: "success", agent: "Code Converter", action: "PL/SQL conversion successful", time: "10m" },
                  { type: "error", agent: "Validator", action: "Syntax validation failed", time: "15m" },
                  { type: "success", agent: "Executor", action: "DDL execution completed", time: "20m" },
                ].map((activity, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs py-1.5 px-2 hover:bg-gray-50 rounded">
                    {activity.type === "success" && <CheckCircle className="w-3.5 h-3.5 text-green-600 flex-shrink-0" />}
                    {activity.type === "running" && <Clock className="w-3.5 h-3.5 text-blue-600 flex-shrink-0" />}
                    {activity.type === "error" && <XCircle className="w-3.5 h-3.5 text-red-600 flex-shrink-0" />}
                    <span className="flex-1 truncate text-gray-900">{activity.action}</span>
                    <span className="text-gray-500 text-[10px]">{activity.time}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader className="pb-2 pt-3 px-4">
              <CardTitle className="text-sm font-semibold">Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="px-4 pb-3 space-y-1.5">
              {[
                { icon: Database, label: "Discover Schema", color: "blue" },
                { icon: Workflow, label: "New Workflow", color: "green" },
                { icon: Activity, label: "Monitor Agents", color: "purple" },
              ].map((action, i) => (
                <button
                  key={i}
                  className="w-full flex items-center gap-2 p-2 text-left text-sm hover:bg-gray-50 rounded transition-colors"
                >
                  <action.icon className={`w-4 h-4 text-${action.color}-600`} />
                  <span className="text-gray-900">{action.label}</span>
                </button>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Agent Performance - Compact Table */}
        <Card>
          <CardHeader className="pb-2 pt-3 px-4">
            <CardTitle className="text-sm font-semibold">Agent Performance</CardTitle>
          </CardHeader>
          <CardContent className="px-4 pb-3">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b text-gray-600">
                  <th className="text-left py-2 font-medium">Agent</th>
                  <th className="text-right py-2 font-medium">Tasks</th>
                  <th className="text-right py-2 font-medium">Success</th>
                  <th className="text-right py-2 font-medium">Rate</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { name: "DB Discoverer", tasks: 156, success: 153, rate: 98 },
                  { name: "Code Converter", tasks: 89, success: 82, rate: 92 },
                  { name: "Validator", tasks: 234, success: 225, rate: 96 },
                  { name: "Executor", tasks: 67, success: 67, rate: 100 },
                  { name: "Logger", tasks: 412, success: 412, rate: 100 },
                ].map((agent, i) => (
                  <tr key={i} className="border-b last:border-0 hover:bg-gray-50">
                    <td className="py-2 font-medium text-gray-900">{agent.name}</td>
                    <td className="text-right text-gray-600">{agent.tasks}</td>
                    <td className="text-right text-gray-600">{agent.success}</td>
                    <td className="text-right">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium ${
                        agent.rate === 100 ? 'bg-green-100 text-green-800' :
                        agent.rate >= 95 ? 'bg-blue-100 text-blue-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {agent.rate}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
