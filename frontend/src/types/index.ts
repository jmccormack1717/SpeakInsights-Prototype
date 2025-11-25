/** TypeScript type definitions */

export interface QueryRequest {
  user_id: string;
  dataset_id: string;
  query: string;
}

export interface QueryResponse {
  sql: string;
  results: Record<string, any>[];
  visualization: VisualizationConfig;
  analysis: TextualAnalysis;
  data_structure: DataStructure;
}

export interface VisualizationConfig {
  type:
    | 'bar'
    | 'line'
    | 'pie'
    | 'scatter'
    | 'histogram'
    | 'table'
    | 'horizontal_bar'
    | 'correlation_matrix';
  data: ChartData;
  config: {
    title?: string;
    xLabel?: string;
    yLabel?: string;
    sort?: 'ascending' | 'descending' | 'none';
    colors?: string[];
    bins?: number;
  };
  metadata?: {
    x_axis?: string;
    y_axis?: string;
    labels?: string;
    values?: string;
  };
}

export interface ChartData {
  labels?: string[];
  values?: number[];
  x?: (string | number)[];
  y?: number[];
  rows?: Record<string, any>[];
  columns?: string[];
  matrix?: number[][];
}

export interface TextualAnalysis {
  summary: string;
  key_findings: string[];
  patterns: string[];
  recommendations: string[];
}

export interface DataStructure {
  row_count: number;
  column_count: number;
  columns: Record<string, ColumnInfo>;
  numeric_columns: string[];
  categorical_columns: string[];
  datetime_columns: string[];
  has_time_series: boolean;
  cardinality: Record<string, number>;
}

export interface ColumnInfo {
  type: 'numeric' | 'categorical' | 'datetime' | 'text';
  nullable: boolean;
  statistics?: {
    min: number;
    max: number;
    mean: number;
    median: number;
  };
}

export interface Dataset {
  dataset_id: string;
  name: string;
  created_at?: number;
}

