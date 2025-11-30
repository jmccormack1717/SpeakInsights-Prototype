/** Dynamic chart renderer component */
import type { ChartData } from '../types'
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
  ScatterChart,
  Scatter,
} from 'recharts';
import type { VisualizationConfig } from '../types';

const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#06b6d4'];

function correlationToColor(value: number): string {
  if (isNaN(value)) return '#ffffff';
  const norm = (value + 1) / 2; // [-1,1] -> [0,1]
  const start = { r: 239, g: 246, b: 255 }; // light blue
  const end = { r: 30, g: 64, b: 175 }; // deep blue
  const r = Math.round(start.r + norm * (end.r - start.r));
  const g = Math.round(start.g + norm * (end.g - start.g));
  const b = Math.round(start.b + norm * (end.b - start.b));
  return `rgb(${r}, ${g}, ${b})`;
}

export function ChartRenderer({ config }: { config: VisualizationConfig }) {
  const { type, data, config: chartConfig, metadata } = config;

  // Common axis label helpers with sensible fallbacks
  const xAxisLabel = chartConfig.xLabel || metadata?.x_axis || undefined;
  const yAxisLabel = chartConfig.yLabel || metadata?.y_axis || undefined;

  // Prepare data for Recharts
  const chartData = prepareChartData(data, type);

  switch (type) {
    case 'bar':
    case 'horizontal_bar':
      return (
        <div className="w-full">
          {chartConfig.title && (
            <h3 className="text-lg font-semibold text-gray-800 mb-4">{chartConfig.title}</h3>
          )}
          <div className="h-96">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={chartData}
                layout={type === 'horizontal_bar' ? 'vertical' : 'horizontal'}
                margin={{ top: 20, right: 30, left: 20, bottom: 40 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" opacity={0.3} />
                <XAxis 
                  dataKey={type === 'horizontal_bar' ? 'value' : 'name'}
                  stroke="#6b7280"
                  tick={{ fill: '#6b7280' }}
                  label={
                    xAxisLabel
                      ? {
                          value: xAxisLabel,
                          position: type === 'horizontal_bar' ? 'insideTopRight' : 'insideBottom',
                          offset: type === 'horizontal_bar' ? 0 : -10,
                          fill: '#6b7280',
                        }
                      : undefined
                  }
                />
                <YAxis 
                  dataKey={type === 'horizontal_bar' ? 'name' : 'value'}
                  stroke="#6b7280"
                  tick={{ fill: '#6b7280' }}
                  label={
                    yAxisLabel
                      ? {
                          value: yAxisLabel,
                          angle: -90,
                          position: 'insideLeft',
                          offset: 10,
                          fill: '#6b7280',
                        }
                      : undefined
                  }
                />
                <Tooltip
                  cursor={false}
                  wrapperStyle={{ zIndex: 50 }}
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                  }}
                />
                <Legend wrapperStyle={{ paddingTop: '20px' }} />
                <Bar dataKey="value" fill={COLORS[0]} radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      );

    case 'histogram':
      // Render histograms as a specialized bar chart
      return (
        <div className="w-full">
          {chartConfig.title && (
            <h3 className="text-lg font-semibold text-gray-800 mb-4">{chartConfig.title}</h3>
          )}
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 24, left: 16, bottom: 40 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" opacity={0.3} />
                <XAxis
                  dataKey="name"
                  stroke="#6b7280"
                  tick={{ fill: '#6b7280' }}
                  angle={-20}
                  textAnchor="end"
                  height={60}
                  label={
                    xAxisLabel
                      ? {
                          value: xAxisLabel,
                          position: 'insideBottom',
                          offset: -5,
                          fill: '#6b7280',
                        }
                      : undefined
                  }
                />
                <YAxis
                  stroke="#6b7280"
                  tick={{ fill: '#6b7280' }}
                  label={
                    yAxisLabel
                      ? {
                          value: yAxisLabel,
                          angle: -90,
                          position: 'insideLeft',
                          offset: 10,
                          fill: '#6b7280',
                        }
                      : undefined
                  }
                />
                <Tooltip
                  cursor={false}
                  wrapperStyle={{ zIndex: 50 }}
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                  }}
                />
                <Bar dataKey="value" fill={COLORS[0]} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      );

    case 'line':
      return (
        <div className="w-full">
          {chartConfig.title && (
            <h3 className="text-lg font-semibold text-gray-800 mb-4">{chartConfig.title}</h3>
          )}
          <div className="h-96">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 40 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" opacity={0.3} />
                <XAxis 
                  dataKey="x"
                  stroke="#6b7280"
                  tick={{ fill: '#6b7280' }}
                  label={
                    xAxisLabel
                      ? {
                          value: xAxisLabel,
                          position: 'insideBottom',
                          offset: -10,
                          fill: '#6b7280',
                        }
                      : undefined
                  }
                />
                <YAxis 
                  stroke="#6b7280"
                  tick={{ fill: '#6b7280' }}
                  label={
                    yAxisLabel
                      ? {
                          value: yAxisLabel,
                          angle: -90,
                          position: 'insideLeft',
                          offset: 10,
                          fill: '#6b7280',
                        }
                      : undefined
                  }
                />
                <Tooltip
                  cursor={false}
                  wrapperStyle={{ zIndex: 50 }}
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                  }}
                />
                <Legend wrapperStyle={{ paddingTop: '20px' }} />
                <Line 
                  type="monotone" 
                  dataKey="y" 
                  stroke={COLORS[0]} 
                  strokeWidth={3}
                  dot={{ fill: COLORS[0], r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      );

    case 'pie':
      return (
        <div className="w-full">
          {chartConfig.title && (
            <h3 className="text-lg font-semibold text-gray-800 mb-6 text-center">{chartConfig.title}</h3>
          )}
          <div className="h-96">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {chartData.map((_, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  cursor={false}
                  wrapperStyle={{ zIndex: 50 }}
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      );

    case 'scatter':
      return (
        <div className="w-full">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            {chartConfig.title || 'Relationship'}
          </h3>
          <div className="h-96">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 20, right: 30, left: 20, bottom: 40 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" opacity={0.3} />
                <XAxis
                  dataKey="x"
                  name={chartConfig.xLabel}
                  stroke="#6b7280"
                  tick={{ fill: '#6b7280' }}
                  label={
                    xAxisLabel
                      ? {
                          value: xAxisLabel,
                          position: 'insideBottom',
                          offset: -10,
                          fill: '#6b7280',
                        }
                      : undefined
                  }
                />
                <YAxis
                  dataKey="y"
                  name={chartConfig.yLabel}
                  stroke="#6b7280"
                  tick={{ fill: '#6b7280' }}
                  label={
                    yAxisLabel
                      ? {
                          value: yAxisLabel,
                          angle: -90,
                          position: 'insideLeft',
                          offset: 10,
                          fill: '#6b7280',
                        }
                      : undefined
                  }
                />
                <Tooltip
                  cursor={{ strokeDasharray: '3 3' }}
                  wrapperStyle={{ zIndex: 50 }}
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                  }}
                />
                <Scatter name="points" data={chartData} fill={COLORS[0]} />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </div>
      );

    case 'correlation_matrix': {
      const labels = data.labels || [];
      const matrix = data.matrix || [];

      return (
        <div className="w-full">
          {chartConfig.title && (
            <h3 className="text-lg font-semibold text-gray-800 mb-4">
              {chartConfig.title}
            </h3>
          )}
          <div className="overflow-x-auto rounded-lg border border-gray-200">
            <table className="min-w-full border-collapse text-xs">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-2 py-2 text-[10px] font-semibold text-gray-500 text-left" />
                  {labels.map((label: string) => (
                    <th
                      key={label}
                      className="px-2 py-2 text-[10px] font-semibold text-gray-700 text-center"
                    >
                      {label}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {matrix.map((row: number[], i: number) => (
                  <tr key={labels[i] || i}>
                    <th className="px-2 py-2 text-[10px] font-semibold text-gray-700 bg-gray-50 text-right">
                      {labels[i] || i}
                    </th>
                    {row.map((val: number, j: number) => (
                      <td
                        key={`${i}-${j}`}
                        className="px-1 py-1 text-[10px] text-center"
                        style={{
                          backgroundColor: correlationToColor(val),
                          color: Math.abs(val) > 0.7 ? '#ffffff' : '#111827',
                        }}
                        title={`${labels[i] || i} vs ${labels[j] || j}: ${val.toFixed(2)}`}
                      >
                        {val.toFixed(2)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      );
    }

    case 'table':
      return (
        <div className="w-full">
          {chartConfig.title && (
            <h3 className="text-lg font-semibold text-gray-800 mb-4">{chartConfig.title}</h3>
          )}
          <div className="overflow-x-auto rounded-lg border border-gray-200">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  {data.columns?.map((col) => (
                    <th key={col} className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {data.rows?.slice(0, 100).map((row, idx) => (
                  <tr key={idx} className="hover:bg-gray-50 transition-colors">
                    {data.columns?.map((col) => (
                      <td key={col} className="px-4 py-3 text-sm text-gray-900 whitespace-nowrap">
                        {row[col]?.toString() || ''}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
            {data.rows && data.rows.length > 100 && (
              <div className="bg-gray-50 px-4 py-3 text-sm text-gray-500 text-center border-t border-gray-200">
                Showing first 100 of {data.rows.length} rows
              </div>
            )}
          </div>
        </div>
      );

    default:
      if (data?.columns && data?.rows) {
        const columns = data.columns as string[];
        const rows = data.rows as Record<string, unknown>[];

        return (
          <div className="w-full">
            {chartConfig.title && (
              <h3 className="text-lg font-semibold text-gray-800 mb-4">
                {chartConfig.title}
              </h3>
            )}
            <div className="overflow-x-auto rounded-lg border border-gray-200">
              <table className="min-w-full divide-y divide-gray-200 text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    {columns.map((col) => (
                      <th
                        key={col}
                        className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider"
                      >
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {rows.slice(0, 50).map((row, idx) => (
                    <tr key={idx} className="hover:bg-gray-50 transition-colors">
                      {columns.map((col) => (
                        <td key={col} className="px-4 py-3 text-gray-900 whitespace-nowrap">
                          {row[col]?.toString() || ''}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        );
      }

      return (
        <div className="p-4 bg-blue-50 border border-blue-100 rounded">
          <p className="text-sm text-blue-800">
            We couldn&apos;t draw a chart for this answer, but the key insights are summarized below.
          </p>
        </div>
      );
  }
}

interface ChartDataPoint {
  name?: string;
  value?: number;
  x?: string | number;
  y?: number;
}

function prepareChartData(
  data: ChartData,
  type: string
): ChartDataPoint[] {
  if (type === 'bar' || type === 'horizontal_bar') {
    return data.labels?.map((label: string, idx: number) => ({
      name: label,
      value: data.values?.[idx] || 0,
    })) || [];
  }

  if (type === 'line') {
    return data.x?.map((x: string | number, idx: number) => ({
      x,
      y: data.y?.[idx] || 0,
    })) || [];
  }

  if (type === 'pie' || type === 'histogram') {
    return data.labels?.map((label: string, idx: number) => ({
      name: label,
      value: data.values?.[idx] || 0,
    })) || [];
  }

  if (type === 'scatter') {
    return data.x?.map((x: string | number, idx: number) => ({
      x,
      y: data.y?.[idx] || 0,
    })) || [];
  }

  return [];
}

