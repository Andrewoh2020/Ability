from datetime import datetime, timezone
from dotenv import load_dotenv
from e2b import Template, default_build_logger

load_dotenv()

template = (
    Template()
    .from_node_image("20")
    .make_dir("/home/user/.ability")
    .make_dir("/home/user/.claude")
    .copy("CLAUDE.md", "/home/user/.claude/CLAUDE.md", force_upload=True)
    .apt_install(["curl", "git", "ripgrep"])
    .npm_install("@anthropic-ai/claude-code degit", g=True)
    .set_workdir("/home/user/kieai-mcp-server")
    .run_cmd("degit marswong/kieai-mcp-server")
    .run_cmd("npm ci")
    .run_cmd("npm run build")
    .set_workdir("/home/user/app")
    .run_cmd("degit marswong/claude-code-web-template")
    .run_cmd("npm i")
    .run_cmd("npm run build")
)


Template.build(
    template,
    alias=f"claude-opus-next-kieai-sqlite-openai-test_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
    cpu_count=1,
    memory_mb=2048,
    on_build_logs=default_build_logger(),
    skip_cache=True,
)
