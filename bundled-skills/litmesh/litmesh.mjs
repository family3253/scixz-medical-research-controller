#!/usr/bin/env node
/**
 * LitMesh —— 跨环境通用 CLI 适配层（direct 模式，免 API Key）。
 *
 * LitMesh 参考了基于 cordis（DeepSeek Harness）的开源学术检索实现；其业务层通过
 * cordis 的 apply(ctx, config) 把学术工具注册进上下文。本脚本用「最小假 ctx」加载该业务层，
 * 使其完全脱离原宿主独立运行，并按工具名直接调用，输出 JSON 或自带的 Markdown 渲染。
 *
 * 本文件是环境无关的：WorkBuddy / Claude Code / Codex 三种环境都通过它来调用工具，
 * 配置统一走环境变量，三者互不冲突、可各自自定义。
 *
 * 运行模式：
 *   - direct（默认，免密钥）：直连免费公共 API —— Semantic Scholar / PubMed(E-utilities)
 *     / OpenAlex(Google Scholar) / arXiv / bioRxiv / medRxiv / DOI / 本地 auto_cite 管线。
 *   - proxy（需 ai4scholar.net API Key）：提供 sci_draw 与额度查询，本技能默认不含。
 *
 * 用法：
 *   node litmesh.mjs --list
 *   node litmesh.mjs <tool_name> '<json_args>' [--render]
 *   node litmesh.mjs <tool_name> '<json_args>' --mode direct [--render]
 *
 * 环境变量（三者均可独立设置，互不冲突）：
 *   LITMESH_MODE           direct | proxy（默认 direct）
 *   LITMESH_TIMEOUT_MS     单工具 HTTP 超时毫秒（默认 30000；网络慢可调大，如 60000）
 *   SEMANTIC_SCHOLAR_API_KEY 可选，仅提高 Semantic Scholar 限流额度（不设也能用）
 *
 * 退出码：0 成功 / 1 工具执行错误 / 2 参数或未知工具
 */
import { apply, Config } from './lib/index.js'

function buildCtx() {
  const tools = new Map()
  const sections = []
  const ctx = {
    tools: {
      register(d) {
        tools.set(d.name, d)
        return () => tools.delete(d.name)
      },
    },
    systemPrompt: {
      section(s) {
        sections.push(s)
        return () => undefined
      },
    },
    // 没有 dsh credentials 服务；凭据统一走 process.env（direct 模式根本不需要）
    get: () => undefined,
    inject(_deps, cb) {
      cb({
        ...ctx,
        commands: { register: () => () => undefined },
        webServer: { register: () => () => undefined },
      })
    },
  }
  return { ctx, tools, sections }
}

const mode = process.env.LITMESH_MODE === 'proxy' ? 'proxy' : 'direct'
const cfg = { mode }
if (process.env.LITMESH_TIMEOUT_MS) {
  const ms = Number(process.env.LITMESH_TIMEOUT_MS)
  if (Number.isFinite(ms) && ms > 0) cfg.requestTimeoutMs = ms
}

const { ctx, tools } = buildCtx()
apply(ctx, new Config(cfg))

const argv = process.argv.slice(2)
if (argv.length === 0 || argv[0] === '--list' || argv[0] === '--help' || argv[0] === '-h') {
  console.log([...tools.keys()].sort().join('\n'))
  process.exit(0)
}

// 打印某工具的精确 JSON 参数 schema（便于学习/复现，无需查源码）
if (argv[0] === '--schema' || argv[0] === 'schema') {
  const name = argv[1]
  const t = name ? tools.get(name) : undefined
  if (!t) {
    console.error(`unknown tool: ${name}\n可用工具: node litmesh.mjs --list`)
    process.exit(2)
  }
  console.log(JSON.stringify(t.parameters ?? null, null, 2))
  process.exit(0)
}

const toolName = argv[0]
const rawArgs = argv[1] && !argv[1].startsWith('--') ? argv[1] : '{}'
const wantRender = argv.includes('--render')

const tool = tools.get(toolName)
if (!tool) {
  console.error(`unknown tool: ${toolName}`)
  console.error('可用工具列表: node litmesh.mjs --list')
  process.exit(2)
}

let args
try {
  args = JSON.parse(rawArgs)
} catch (e) {
  console.error(`invalid JSON args: ${e instanceof Error ? e.message : String(e)}`)
  process.exit(2)
}

const controller = new AbortController()
const exec = { signal: controller.signal, agent: undefined }

try {
  const value = await tool.execute(args, exec)
  if (wantRender && tool.output && typeof tool.output.render === 'function') {
    for (const block of tool.output.render(args, value)) {
      if (block && block.type === 'text') process.stdout.write(block.text + '\n')
    }
  } else {
    process.stdout.write(JSON.stringify(value, null, 2) + '\n')
  }
} catch (error) {
  console.error(`TOOL_ERROR: ${error instanceof Error ? error.message : String(error)}`)
  process.exit(1)
}
