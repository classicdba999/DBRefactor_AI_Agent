"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Database, Search, Loader2, Table, Eye, Code } from "lucide-react";

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
    <div className="h-screen overflow-auto bg-gray-50">
      {/* Header */}
      <div className="sticky top-0 bg-white border-b px-5 py-3 z-10">
        <h1 className="text-lg font-semibold text-gray-900">Discovery</h1>
      </div>

      <div className="p-4 space-y-3">
        {/* Discovery Form */}
        <Card>
          <CardContent className="p-3">
            <div className="flex gap-2">
              <input
                type="text"
                value={schemaName}
                onChange={(e) => setSchemaName(e.target.value)}
                placeholder="Enter schema name (e.g., HR, SALES)"
                className="flex-1 px-3 py-1.5 border border-gray-300 rounded text-xs bg-white text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={loading}
              />
              <button
                onClick={discoverSchema}
                disabled={loading || !schemaName.trim()}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded text-xs font-medium transition-colors"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    Discovering
                  </>
                ) : (
                  <>
                    <Search className="w-3.5 h-3.5" />
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
            {/* Summary Stats - Compact Grid */}
            <div className="grid grid-cols-4 gap-3">
              <Card>
                <CardContent className="p-3">
                  <div className="flex items-center gap-2">
                    <div className="w-7 h-7 bg-blue-100 rounded flex items-center justify-center flex-shrink-0">
                      <Table className="w-4 h-4 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-[10px] text-gray-600">Tables</p>
                      <p className="text-lg font-bold text-gray-900">
                        {result.metadata.summary.total_tables}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-3">
                  <div className="flex items-center gap-2">
                    <div className="w-7 h-7 bg-green-100 rounded flex items-center justify-center flex-shrink-0">
                      <Eye className="w-4 h-4 text-green-600" />
                    </div>
                    <div>
                      <p className="text-[10px] text-gray-600">Views</p>
                      <p className="text-lg font-bold text-gray-900">
                        {result.metadata.summary.total_views}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-3">
                  <div className="flex items-center gap-2">
                    <div className="w-7 h-7 bg-purple-100 rounded flex items-center justify-center flex-shrink-0">
                      <Code className="w-4 h-4 text-purple-600" />
                    </div>
                    <div>
                      <p className="text-[10px] text-gray-600">Procedures</p>
                      <p className="text-lg font-bold text-gray-900">
                        {result.metadata.summary.total_procedures}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-3">
                  <div className="flex items-center gap-2">
                    <div className="w-7 h-7 bg-orange-100 rounded flex items-center justify-center flex-shrink-0">
                      <Database className="w-4 h-4 text-orange-600" />
                    </div>
                    <div>
                      <p className="text-[10px] text-gray-600">Total</p>
                      <p className="text-lg font-bold text-gray-900">
                        {result.metadata.summary.total_objects}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Complexity Table */}
            <Card>
              <CardHeader className="pb-2 pt-3 px-4">
                <CardTitle className="text-sm font-semibold">Complexity Analysis</CardTitle>
              </CardHeader>
              <CardContent className="px-0 pb-0">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-y bg-gray-50 text-gray-600">
                      <th className="text-left py-2 px-4 font-medium">Complexity</th>
                      <th className="text-right py-2 px-4 font-medium">Count</th>
                      <th className="text-left py-2 px-4 font-medium">Description</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b hover:bg-gray-50 transition-colors">
                      <td className="py-3 px-4">
                        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-medium bg-green-100 text-green-800">
                          Simple
                        </span>
                      </td>
                      <td className="text-right py-3 px-4 text-gray-900 font-medium">
                        {result.categorized_objects.simple.length}
                      </td>
                      <td className="py-3 px-4 text-gray-600">
                        Easy to migrate
                      </td>
                    </tr>
                    <tr className="border-b hover:bg-gray-50 transition-colors">
                      <td className="py-3 px-4">
                        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-medium bg-blue-100 text-blue-800">
                          Moderate
                        </span>
                      </td>
                      <td className="text-right py-3 px-4 text-gray-900 font-medium">
                        {result.categorized_objects.moderate.length}
                      </td>
                      <td className="py-3 px-4 text-gray-600">
                        Some dependencies
                      </td>
                    </tr>
                    <tr className="border-b hover:bg-gray-50 transition-colors">
                      <td className="py-3 px-4">
                        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-medium bg-orange-100 text-orange-800">
                          Complex
                        </span>
                      </td>
                      <td className="text-right py-3 px-4 text-gray-900 font-medium">
                        {result.categorized_objects.complex.length}
                      </td>
                      <td className="py-3 px-4 text-gray-600">
                        Multiple dependencies
                      </td>
                    </tr>
                    <tr className="hover:bg-gray-50 transition-colors">
                      <td className="py-3 px-4">
                        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-medium bg-red-100 text-red-800">
                          Very Complex
                        </span>
                      </td>
                      <td className="text-right py-3 px-4 text-gray-900 font-medium">
                        {result.categorized_objects.very_complex.length}
                      </td>
                      <td className="py-3 px-4 text-gray-600">
                        Requires careful planning
                      </td>
                    </tr>
                  </tbody>
                </table>
              </CardContent>
            </Card>
          </>
        )}

        {!result && !loading && (
          <Card>
            <CardContent className="py-12 text-center">
              <Database className="w-10 h-10 text-gray-400 mx-auto mb-3" />
              <p className="text-sm text-gray-500">
                Enter a schema name to begin discovery
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
