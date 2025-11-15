"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, Database, Workflow, TrendingUp } from "lucide-react";
import { StatsCard } from "@/components/stats-card";
import { RecentActivity } from "@/components/recent-activity";
import { AgentStatusChart } from "@/components/agent-status-chart";

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalAgents: 0,
    activeWorkflows: 0,
    completedMigrations: 0,
    successRate: 0,
  });

  useEffect(() => {
    // Fetch dashboard stats from API
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
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Dashboard
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Welcome to DBRefactor AI Agent - Your intelligent database migration assistant
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
        <StatsCard
          title="Total Agents"
          value={stats.totalAgents}
          icon={Activity}
          trend="+2 from last month"
          trendUp
        />
        <StatsCard
          title="Active Workflows"
          value={stats.activeWorkflows}
          icon={Workflow}
          trend="Running now"
        />
        <StatsCard
          title="Completed Migrations"
          value={stats.completedMigrations}
          icon={Database}
          trend="+12 this week"
          trendUp
        />
        <StatsCard
          title="Success Rate"
          value={`${stats.successRate}%`}
          icon={TrendingUp}
          trend="+5% from last month"
          trendUp
        />
      </div>

      {/* Charts and Activity */}
      <div className="grid gap-6 md:grid-cols-2 mb-8">
        <Card>
          <CardHeader>
            <CardTitle>Agent Performance</CardTitle>
            <CardDescription>Task success rates by agent</CardDescription>
          </CardHeader>
          <CardContent>
            <AgentStatusChart />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Latest agent and workflow events</CardDescription>
          </CardHeader>
          <CardContent>
            <RecentActivity />
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Common tasks to get started</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <button className="flex flex-col items-start p-4 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
              <Database className="h-8 w-8 mb-2 text-blue-600" />
              <h3 className="font-semibold mb-1">Discover Schema</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Analyze database objects and dependencies
              </p>
            </button>
            <button className="flex flex-col items-start p-4 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
              <Workflow className="h-8 w-8 mb-2 text-green-600" />
              <h3 className="font-semibold mb-1">Create Workflow</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Build a new migration workflow
              </p>
            </button>
            <button className="flex flex-col items-start p-4 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
              <Activity className="h-8 w-8 mb-2 text-purple-600" />
              <h3 className="font-semibold mb-1">Monitor Agents</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                View agent status and performance
              </p>
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
