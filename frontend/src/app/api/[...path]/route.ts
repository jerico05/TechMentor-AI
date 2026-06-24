import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const HOP_BY_HOP = new Set([
  "connection",
  "keep-alive",
  "proxy-authenticate",
  "proxy-authorization",
  "te",
  "trailers",
  "transfer-encoding",
  "upgrade",
  "host",
  "content-length",
]);

function backendBase(): string {
  let base = process.env.BACKEND_URL?.trim() || "http://localhost:8000";
  if (!/^https?:\/\//i.test(base)) {
    base = `http://${base}`;
  }
  return base.replace(/\/$/, "");
}

function buildTargetUrl(request: NextRequest, path: string[]): string {
  const suffix = path.length > 0 ? path.join("/") : "";
  const query = request.nextUrl.search;
  return `${backendBase()}/api/${suffix}${query}`;
}

function forwardHeaders(request: NextRequest): Headers {
  const headers = new Headers();
  request.headers.forEach((value, key) => {
    if (!HOP_BY_HOP.has(key.toLowerCase())) {
      headers.set(key, value);
    }
  });
  return headers;
}

async function proxy(request: NextRequest, path: string[]): Promise<NextResponse> {
  const target = buildTargetUrl(request, path);
  const method = request.method.toUpperCase();
  const headers = forwardHeaders(request);

  let body: BodyInit | undefined;
  if (method !== "GET" && method !== "HEAD") {
    body = await request.arrayBuffer();
  }

  let upstream: Response;
  try {
    upstream = await fetch(target, {
      method,
      headers,
      body,
      redirect: "manual",
      cache: "no-store",
    });
  } catch {
    return NextResponse.json(
      {
        error: {
          code: "backend_unreachable",
          message:
            "Impossible de joindre le backend. Vérifiez BACKEND_URL sur Vercel et le port 8000 sur EC2.",
        },
      },
      { status: 502 },
    );
  }

  const responseHeaders = new Headers();
  upstream.headers.forEach((value, key) => {
    if (!HOP_BY_HOP.has(key.toLowerCase())) {
      responseHeaders.set(key, value);
    }
  });

  return new NextResponse(upstream.body, {
    status: upstream.status,
    headers: responseHeaders,
  });
}

type RouteContext = { params: Promise<{ path?: string[] }> };

async function resolvePath(context: RouteContext): Promise<string[]> {
  const { path } = await context.params;
  return path ?? [];
}

export async function GET(request: NextRequest, context: RouteContext) {
  return proxy(request, await resolvePath(context));
}

export async function POST(request: NextRequest, context: RouteContext) {
  return proxy(request, await resolvePath(context));
}

export async function PUT(request: NextRequest, context: RouteContext) {
  return proxy(request, await resolvePath(context));
}

export async function PATCH(request: NextRequest, context: RouteContext) {
  return proxy(request, await resolvePath(context));
}

export async function DELETE(request: NextRequest, context: RouteContext) {
  return proxy(request, await resolvePath(context));
}

export async function OPTIONS(request: NextRequest, context: RouteContext) {
  return proxy(request, await resolvePath(context));
}
