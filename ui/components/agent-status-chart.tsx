"use client";

import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

export function AgentStatusChart() {
  const [data, setData] = useState<any[]>([]);

  useEffect(() => {
    // Fetch agent stats from API
    fetch("/api/v1/agents/info")
      .then((res) => res.json())
      .then((apiData) => {
        if (apiData.agents) {
          const chartData = Object.entries(apiData.agents).map(([name, agent]: [string, any]) => ({
            name,
            successRate: Math.round((agent.stats?.success_rate || 0) * 100),
            tasks: agent.stats?.tasks_executed || 0,
          }));
          setData(chartData);
        }
      })
      .catch(console.error);
  }, []);

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        No agent data available
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" />
        <YAxis />
        <Tooltip />
        <Bar dataKey="successRate" fill="#3b82f6" name="Success Rate %" />
      </BarChart>
    </ResponsiveContainer>
  );
}
