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
    <div className="flex flex-col w-14 bg-gray-900 border-r border-gray-800">
      {/* Logo */}
      <div className="flex items-center justify-center h-14 border-b border-gray-800">
        <Database className="w-6 h-6 text-blue-400" />
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-2 space-y-1">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              title={item.name}
              className={cn(
                "flex items-center justify-center h-11 mx-1 rounded transition-all group relative",
                isActive
                  ? "bg-blue-600 text-white"
                  : "text-gray-400 hover:bg-gray-800 hover:text-gray-200"
              )}
            >
              <item.icon className="w-5 h-5" />
              <span className="absolute left-full ml-2 px-2 py-1 bg-gray-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap transition-opacity z-50">
                {item.name}
              </span>
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="h-14 flex items-center justify-center border-t border-gray-800">
        <div className="w-2 h-2 rounded-full bg-green-500"></div>
      </div>
    </div>
  );
}
