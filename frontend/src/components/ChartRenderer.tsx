/** Dynamic chart renderer component */
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import type { VisualizationConfig } from '../types';

const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#06b6d4'];

export function ChartRenderer({ config }: { config: VisualizationConfig }) {
  const { type, data, config: chartConfig } = config;

  // Prepare data for Recharts
  const chartData = prepareChartData(data, type);

  switch (type) {
    case 'bar':
    case 'horizontal_bar':
      return (
        <div className="w-full h-96">
          <h3 className="text-xl font-semibold mb-4">{chartConfig.title || 'Chart'}</h3>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} layout={type === 'horizontal_bar' ? 'vertical' : 'horizontal'}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey={type === 'horizontal_bar' ? 'value' : 'name'} 
                label={{ value: chartConfig.xLabel, position: 'insideBottom', offset: -5 }}
              />
              <YAxis 
                dataKey={type === 'horizontal_bar' ? 'name' : 'value'}
                label={{ value: chartConfig.yLabel, angle: -90, position: 'insideLeft' }}
              />
              <Tooltip />
              <Legend />
              <Bar dataKey="value" fill={COLORS[0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      );

    case 'line':
      return (
        <div className="w-full h-96">
          <h3 className="text-xl font-semibold mb-4">{chartConfig.title || 'Chart'}</h3>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="x" 
                label={{ value: chartConfig.xLabel, position: 'insideBottom', offset: -5 }}
              />
              <YAxis 
                label={{ value: chartConfig.yLabel, angle: -90, position: 'insideLeft' }}
              />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="y" stroke={COLORS[0]} strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      );

    case 'pie':
      return (
        <div className="w-full h-96">
          <h3 className="text-xl font-semibold mb-4">{chartConfig.title || 'Chart'}</h3>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={120}
                fill="#8884d8"
                dataKey="value"
              >
                {chartData.map((_, index: number) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      );

    case 'scatter':
      return (
        <div className="w-full h-96">
          <h3 className="text-xl font-semibold mb-4">{chartConfig.title || 'Chart'}</h3>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="x" 
                label={{ value: chartConfig.xLabel, position: 'insideBottom', offset: -5 }}
              />
              <YAxis 
                label={{ value: chartConfig.yLabel, angle: -90, position: 'insideLeft' }}
              />
              <Tooltip />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="y" 
                stroke={COLORS[0]} 
                strokeWidth={2}
                dot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      );

    case 'table':
      return (
        <div className="w-full">
          <h3 className="text-xl font-semibold mb-4">{chartConfig.title || 'Data Table'}</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full border-collapse border border-gray-300">
              <thead>
                <tr className="bg-gray-100">
                  {data.columns?.map((col) => (
                    <th key={col} className="border border-gray-300 px-4 py-2 text-left">
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.rows?.slice(0, 100).map((row, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    {data.columns?.map((col) => (
                      <td key={col} className="border border-gray-300 px-4 py-2">
                        {row[col]?.toString() || ''}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
            {data.rows && data.rows.length > 100 && (
              <p className="mt-2 text-sm text-gray-500">
                Showing first 100 of {data.rows.length} rows
              </p>
            )}
          </div>
        </div>
      );

    default:
      return (
        <div className="p-4 bg-yellow-50 border border-yellow-200 rounded">
          <p>Unsupported chart type: {type}</p>
        </div>
      );
  }
}

function prepareChartData(
  data: any,
  type: string
): any[] {
  if (type === 'bar' || type === 'horizontal_bar') {
    return data.labels?.map((label: string, idx: number) => ({
      name: label,
      value: data.values?.[idx] || 0,
    })) || [];
  }

  if (type === 'line') {
    return data.x?.map((x: any, idx: number) => ({
      x,
      y: data.y?.[idx] || 0,
    })) || [];
  }

  if (type === 'pie') {
    return data.labels?.map((label: string, idx: number) => ({
      name: label,
      value: data.values?.[idx] || 0,
    })) || [];
  }

  if (type === 'scatter') {
    return data.x?.map((x: any, idx: number) => ({
      x,
      y: data.y?.[idx] || 0,
    })) || [];
  }

  return [];
}

