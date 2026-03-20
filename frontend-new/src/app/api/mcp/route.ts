import { NextRequest, NextResponse } from 'next/server';
import {
  buildCapabilitySnapshot,
  buildRoundtablePlan,
  listAgentRoster,
  recommendExpert,
  searchDatabases,
} from '@/lib/medroundtable-mcp';

export const dynamic = 'force-dynamic';

type JsonRpcId = string | number | null;

interface JsonRpcRequest {
  jsonrpc?: string;
  id?: JsonRpcId;
  method: string;
  params?: Record<string, unknown>;
}

const SERVER_INFO = {
  name: 'MedRoundTable MCP',
  version: '1.0.0',
};

const MCP_PROTOCOL_VERSION = '2024-11-05';
const MCP_ENDPOINT_PATH = '/api/mcp';

const TOOL_DEFINITIONS = [
  {
    name: 'triage_research_question',
    description: '根据临床问题推荐首位 Agent、SecondMe 阵容和启动动作。',
    annotations: { readOnlyHint: true },
    inputSchema: {
      type: 'object',
      additionalProperties: false,
      properties: {
        clinicalQuestion: { type: 'string', description: '用户的临床或科研问题' },
        title: { type: 'string', description: '可选，用户给圆桌自定义标题' },
      },
      required: ['clinicalQuestion'],
    },
  },
  {
    name: 'build_roundtable_plan',
    description: '生成一个可直接带回 MedRoundTable 的圆桌启动计划和 handoff URL。',
    annotations: { readOnlyHint: true },
    inputSchema: {
      type: 'object',
      additionalProperties: false,
      properties: {
        clinicalQuestion: { type: 'string', description: '临床或科研问题' },
        title: { type: 'string', description: '可选标题' },
      },
      required: ['clinicalQuestion'],
    },
  },
  {
    name: 'list_agent_roster',
    description: '查看 14 位医学科研 Agent 的分组、定位和擅长问题。',
    annotations: { readOnlyHint: true },
    inputSchema: {
      type: 'object',
      additionalProperties: false,
      properties: {
        group: { type: 'string', description: '可选，按团队分组过滤' },
        query: { type: 'string', description: '可选，按关键词搜索专家' },
      },
    },
  },
  {
    name: 'search_public_databases',
    description: '按问题方向查找适合接入的公开医学数据库和推荐 Agent。',
    annotations: { readOnlyHint: true },
    inputSchema: {
      type: 'object',
      additionalProperties: false,
      properties: {
        query: { type: 'string', description: '疾病、设计或数据方向关键词' },
        category: { type: 'string', description: '可选数据库分类，如文献、临床试验、队列' },
        limit: { type: 'number', description: '返回条数，默认 5' },
      },
    },
  },
  {
    name: 'get_platform_snapshot',
    description: '查看 MedRoundTable 当前平台能力快照，包括 Agent、数据库和能力链路。',
    annotations: { readOnlyHint: true },
    inputSchema: {
      type: 'object',
      additionalProperties: false,
      properties: {},
    },
  },
];

function createCorsHeaders() {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Max-Age': '86400',
  };
}

function jsonRpcResult(id: JsonRpcId, result: unknown, status = 200) {
  return NextResponse.json({ jsonrpc: '2.0', id, result }, { status, headers: createCorsHeaders() });
}

function jsonRpcError(id: JsonRpcId, code: number, message: string, data?: unknown, status = 200) {
  return NextResponse.json({ jsonrpc: '2.0', id, error: { code, message, data } }, { status, headers: createCorsHeaders() });
}

function formatTextResult(title: string, payload: unknown) {
  return {
    content: [
      {
        type: 'text',
        text: `${title}\n\n${JSON.stringify(payload, null, 2)}`,
      },
    ],
    structuredContent: payload,
  };
}

function extractBearerToken(request: NextRequest) {
  const authorization = request.headers.get('authorization') || '';
  const bearerMatch = authorization.match(/^Bearer\s+(.+)$/i);
  if (!bearerMatch) {
    return { error: 'Missing Authorization: Bearer <token> header' } as const;
  }

  const token = bearerMatch[1].trim();
  if (!token) {
    return { error: 'Empty bearer token' } as const;
  }

  return { token } as const;
}

async function resolveSecondMeProfile(token: string) {

  const profileEndpoint =
    process.env.SECONDME_PROFILE_ENDPOINT || 'https://api.mindverse.com/gate/lab/api/secondme/user/info';

  try {
    const response = await fetch(profileEndpoint, {
      headers: { Authorization: `Bearer ${token}` },
      cache: 'no-store',
    });
    if (!response.ok) {
      return null;
    }
    const result = await response.json();
    const data = result?.data || result;
    return {
      id: data?.id || data?.sub || '',
      name: data?.name || data?.nickname || 'SecondMe User',
      email: data?.email || '',
      avatar: data?.avatar || data?.avatarUrl || '',
    };
  } catch {
    return null;
  }
}

function parseArguments(params?: Record<string, unknown>) {
  const raw = params?.arguments;
  if (typeof raw === 'string') {
    try {
      return JSON.parse(raw) as Record<string, unknown>;
    } catch {
      return {};
    }
  }
  if (raw && typeof raw === 'object') {
    return raw as Record<string, unknown>;
  }
  return {};
}

async function handleToolCall(request: NextRequest, params?: Record<string, unknown>) {
  const toolName = params?.name;
  const args = parseArguments(params);
  const auth = extractBearerToken(request);
  if ('error' in auth) {
    return { error: { code: -32001, message: auth.error, status: 401 } };
  }

  const profile = await resolveSecondMeProfile(auth.token);
  if (!profile) {
    return { error: { code: -32001, message: 'Invalid or expired SecondMe bearer token', status: 401 } };
  }

  const baseUrl = process.env.MEDROUNDTABLE_WEB_URL || 'https://mokangmedical.github.io/medroundtable';

  switch (toolName) {
    case 'triage_research_question': {
      const clinicalQuestion = String(args.clinicalQuestion || '').trim();
      if (!clinicalQuestion) {
        return { error: { code: -32602, message: 'clinicalQuestion is required' } };
      }
      const expert = recommendExpert(clinicalQuestion);
      const plan = buildRoundtablePlan({
        clinicalQuestion,
        title: typeof args.title === 'string' ? args.title : undefined,
        includeSecondMe: true,
        profile,
        baseUrl,
      });
      return formatTextResult('Research triage completed', {
        profile,
        recommendedExpert: expert,
        suggestedOpening: expert.suggestedOpening,
        recommendedPlan: plan,
      });
    }
    case 'build_roundtable_plan': {
      const clinicalQuestion = String(args.clinicalQuestion || '').trim();
      if (!clinicalQuestion) {
        return { error: { code: -32602, message: 'clinicalQuestion is required' } };
      }
      const plan = buildRoundtablePlan({
        clinicalQuestion,
        title: typeof args.title === 'string' ? args.title : undefined,
        includeSecondMe: true,
        profile,
        baseUrl,
      });
      return formatTextResult('Roundtable plan ready', {
        profile,
        ...plan,
      });
    }
    case 'list_agent_roster': {
      const roster = listAgentRoster({
        group: typeof args.group === 'string' ? args.group : undefined,
        query: typeof args.query === 'string' ? args.query : undefined,
      });
      return formatTextResult('Agent roster', {
        total: roster.length,
        agents: roster,
      });
    }
    case 'search_public_databases': {
      const databases = searchDatabases({
        query: typeof args.query === 'string' ? args.query : undefined,
        category: typeof args.category === 'string' ? args.category : undefined,
        limit: typeof args.limit === 'number' ? args.limit : undefined,
      });
      return formatTextResult('Public database matches', {
        total: databases.length,
        databases,
      });
    }
    case 'get_platform_snapshot': {
      return formatTextResult('Platform snapshot', buildCapabilitySnapshot());
    }
    default:
      return { error: { code: -32601, message: `Unknown tool: ${String(toolName)}` } };
  }
}

export async function GET(request: NextRequest) {
  return NextResponse.json({
    ok: true,
    server: SERVER_INFO,
    endpoint: `${new URL(request.url).origin}${MCP_ENDPOINT_PATH}`,
    protocolVersion: MCP_PROTOCOL_VERSION,
    authMode: 'bearer_token',
    authRequiredForToolCalls: true,
    tools: TOOL_DEFINITIONS.map(({ name, description }) => ({ name, description, readOnly: true })),
    docs: {
      website: process.env.MEDROUNDTABLE_WEB_URL || 'https://mokangmedical.github.io/medroundtable',
      login: `${new URL(request.url).origin}/api/auth/login`,
      support: `${new URL(request.url).origin}/support`,
      privacy: `${new URL(request.url).origin}/privacy`,
      skill: `${new URL(request.url).origin}/skill.md`,
      integrationManifest: `${new URL(request.url).origin}/secondme-integration-manifest.json`,
      appListing: `${new URL(request.url).origin}/secondme-app-listing.json`,
    },
  });
}

export async function POST(request: NextRequest) {
  let body: JsonRpcRequest;
  try {
    body = (await request.json()) as JsonRpcRequest;
  } catch {
    return jsonRpcError(null, -32700, 'Parse error', undefined, 400);
  }

  const id = body.id ?? null;

  if (body.method === 'initialize') {
    return jsonRpcResult(id, {
      protocolVersion: MCP_PROTOCOL_VERSION,
      capabilities: {
        tools: {
          listChanged: false,
        },
      },
      serverInfo: SERVER_INFO,
      instructions:
        'Use MedRoundTable to triage clinical research questions, choose the right expert, build a roundtable handoff plan, and route users to public research databases. Tool calls require a valid SecondMe bearer token so the integration can resolve the current user context safely.',
    });
  }

  if (body.method === 'ping') {
    return jsonRpcResult(id, {});
  }

  if (body.method === 'notifications/initialized') {
    return new NextResponse(null, { status: 204, headers: createCorsHeaders() });
  }

  if (body.method === 'tools/list') {
    return jsonRpcResult(id, {
      tools: TOOL_DEFINITIONS,
    });
  }

  if (body.method === 'tools/call') {
    const result = await handleToolCall(request, body.params);
    if ('error' in result) {
      const { code, message, status } = result.error as { code: number; message: string; status?: number };
      return jsonRpcError(id, code, message, undefined, status || 200);
    }
    return jsonRpcResult(id, result);
  }

  return jsonRpcError(id, -32601, `Method not found: ${body.method}`);
}

export async function OPTIONS() {
  return new NextResponse(null, { status: 204, headers: createCorsHeaders() });
}
