"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Home,
  Activity,
  Workflow,
  Database,
  Settings,
  GitBranch,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navigation = [
  { name: "Dashboard", href: "/", icon: Home },
  { name: "Agents", href: "/agents", icon: Activity },
  { name: "Workflows", href: "/workflows", icon: Workflow },
  { name: "Discovery", href: "/discovery", icon: Database },
  { name: "Dependencies", href: "/dependencies", icon: GitBranch },
  { name: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="flex flex-col w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700">
      {/* Logo */}
      <div className="flex items-center h-16 px-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <Database className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-gray-900 dark:text-white">
              DBRefactor AI
            </h1>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Migration Agent
            </p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                isActive
                  ? "bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400"
                  : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
              )}
            >
              <item.icon className="w-5 h-5" />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <div className="px-3 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg">
          <p className="text-xs text-gray-600 dark:text-gray-400">
            Version 1.0.0
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
            Framework Status: Active
          </p>
        </div>
      </div>
    </div>
  );
}
