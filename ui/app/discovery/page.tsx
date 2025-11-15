"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Database, Search, Loader2, CheckCircle, Table, Eye, Code, Zap } from "lucide-react";

interface DiscoveryResult {
  schema_name: string;
  metadata: {
    summary: {
      total_tables: number;
      total_views: number;
      total_procedures: number;
      total_functions: number;
      total_triggers: number;
      total_objects: number;
    };
  };
  categorized_objects: {
    simple: string[];
    moderate: string[];
    complex: string[];
    very_complex: string[];
  };
}

export default function DiscoveryPage() {
  const [schemaName, setSchemaName] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DiscoveryResult | null>(null);

  const discoverSchema = async () => {
    if (!schemaName.trim()) return;

    setLoading(true);
    try {
      const res = await fetch("/api/v1/discovery/discover", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          schema_name: schemaName,
          include_system_objects: false,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        setResult(data);
      }
    } catch (error) {
      console.error("Discovery failed:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Database Discovery
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Discover and analyze database schema objects and their properties
        </p>
      </div>

      {/* Discovery Form */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Schema Discovery</CardTitle>
          <CardDescription>
            Enter a schema name to discover all database objects
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="flex-1">
              <input
                type="text"
                value={schemaName}
                onChange={(e) => setSchemaName(e.target.value)}
                placeholder="Enter schema name (e.g., HR, SALES)"
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={loading}
              />
            </div>
            <button
              onClick={discoverSchema}
              disabled={loading || !schemaName.trim()}
              className="flex items-center gap-2 px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-colors"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Discovering...
                </>
              ) : (
                <>
                  <Search className="w-4 h-4" />
                  Discover
                </>
              )}
            </button>
          </div>
        </CardContent>
      </Card>

      {/* Discovery Results */}
      {result && (
        <>
          {/* Summary Stats */}
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Tables
                    </p>
                    <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                      {result.metadata.summary.total_tables}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
                    <Table className="w-6 h-6 text-blue-600" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Views
                    </p>
                    <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                      {result.metadata.summary.total_views}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-green-100 dark:bg-green-900/20 rounded-lg flex items-center justify-center">
                    <Eye className="w-6 h-6 text-green-600" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Procedures
                    </p>
                    <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                      {result.metadata.summary.total_procedures}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/20 rounded-lg flex items-center justify-center">
                    <Code className="w-6 h-6 text-purple-600" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Total Objects
                    </p>
                    <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                      {result.metadata.summary.total_objects}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-orange-100 dark:bg-orange-900/20 rounded-lg flex items-center justify-center">
                    <Database className="w-6 h-6 text-orange-600" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Categorized Objects */}
          <Card>
            <CardHeader>
              <CardTitle>Object Complexity</CardTitle>
              <CardDescription>
                Objects categorized by migration complexity
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <div className="p-4 border border-green-200 dark:border-green-800 rounded-lg bg-green-50 dark:bg-green-900/10">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="w-5 h-5 text-green-600" />
                    <h3 className="font-semibold text-green-900 dark:text-green-400">
                      Simple
                    </h3>
                  </div>
                  <p className="text-2xl font-bold text-green-900 dark:text-green-400 mb-2">
                    {result.categorized_objects.simple.length}
                  </p>
                  <p className="text-xs text-green-700 dark:text-green-500">
                    Easy to migrate
                  </p>
                </div>

                <div className="p-4 border border-blue-200 dark:border-blue-800 rounded-lg bg-blue-50 dark:bg-blue-900/10">
                  <div className="flex items-center gap-2 mb-2">
                    <Zap className="w-5 h-5 text-blue-600" />
                    <h3 className="font-semibold text-blue-900 dark:text-blue-400">
                      Moderate
                    </h3>
                  </div>
                  <p className="text-2xl font-bold text-blue-900 dark:text-blue-400 mb-2">
                    {result.categorized_objects.moderate.length}
                  </p>
                  <p className="text-xs text-blue-700 dark:text-blue-500">
                    Some dependencies
                  </p>
                </div>

                <div className="p-4 border border-orange-200 dark:border-orange-800 rounded-lg bg-orange-50 dark:bg-orange-900/10">
                  <div className="flex items-center gap-2 mb-2">
                    <Database className="w-5 h-5 text-orange-600" />
                    <h3 className="font-semibold text-orange-900 dark:text-orange-400">
                      Complex
                    </h3>
                  </div>
                  <p className="text-2xl font-bold text-orange-900 dark:text-orange-400 mb-2">
                    {result.categorized_objects.complex.length}
                  </p>
                  <p className="text-xs text-orange-700 dark:text-orange-500">
                    Multiple dependencies
                  </p>
                </div>

                <div className="p-4 border border-red-200 dark:border-red-800 rounded-lg bg-red-50 dark:bg-red-900/10">
                  <div className="flex items-center gap-2 mb-2">
                    <Code className="w-5 h-5 text-red-600" />
                    <h3 className="font-semibold text-red-900 dark:text-red-400">
                      Very Complex
                    </h3>
                  </div>
                  <p className="text-2xl font-bold text-red-900 dark:text-red-400 mb-2">
                    {result.categorized_objects.very_complex.length}
                  </p>
                  <p className="text-xs text-red-700 dark:text-red-500">
                    Requires careful planning
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      )}

      {!result && !loading && (
        <Card>
          <CardContent className="py-12 text-center">
            <Database className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 dark:text-gray-400">
              Enter a schema name and click Discover to begin
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
