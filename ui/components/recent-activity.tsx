"use client";

import { CheckCircle, XCircle, Clock } from "lucide-react";

const activities = [
  {
    id: 1,
    type: "success",
    agent: "DB Discoverer",
    action: "Schema discovery completed",
    time: "2 minutes ago",
  },
  {
    id: 2,
    type: "running",
    agent: "Workflow Engine",
    action: "Migration workflow in progress",
    time: "5 minutes ago",
  },
  {
    id: 3,
    type: "success",
    agent: "Code Converter",
    action: "PL/SQL conversion successful",
    time: "10 minutes ago",
  },
  {
    id: 4,
    type: "error",
    agent: "Validator",
    action: "Syntax validation failed",
    time: "15 minutes ago",
  },
];

export function RecentActivity() {
  return (
    <div className="space-y-4">
      {activities.map((activity) => (
        <div key={activity.id} className="flex items-start gap-3">
          <div className="mt-1">
            {activity.type === "success" && (
              <CheckCircle className="w-5 h-5 text-green-600" />
            )}
            {activity.type === "error" && (
              <XCircle className="w-5 h-5 text-red-600" />
            )}
            {activity.type === "running" && (
              <Clock className="w-5 h-5 text-blue-600" />
            )}
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-900 dark:text-white">
              {activity.action}
            </p>
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
              {activity.agent} • {activity.time}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
