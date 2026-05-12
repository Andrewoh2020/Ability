from contextlib import suppress
import json
import os
from typing import Literal, Optional
from uuid import UUID

from dotenv import load_dotenv
from e2b import CommandHandle, Sandbox
import httpx
from loguru import logger
from sqlmodel import select

from app.core.db import async_session
from app.models.app import AppStage
from app.models.sandbox import Sandbox as SandboxModel
from app.services.app_service import app_service
from app.utils.common import SingletonMeta
from app.utils.chat import ABILITY_CONFIG_PATH


load_dotenv()

developer_system_prompt = """
You are a Senior Full-Stack Developer and expert in ReactJS, Next.js 16, SQLite, JavaScript, HTML, CSS, and modern UI/UX frameworks (TailwindCSS 3, shadcn/ui, Radix).

## Instructions
1. The project scaffolding has been set up at `/home/user/app`, please continue to iterate based on it
2. Try to build AI related features reusing the openai SDK as much as possible
3. To generate images for illustrations, call the tool: mcp__kieai-mcp-server__text_to_image_flux_2_pro
4. Always report a complete working progress of user selected features using TodoWrite tool, following the example below

## Example
User:
selected features: Hero Banner, Menu Grid, Gallery
Assistant:
{
    "todos": [
        {
            "content": "Hero Banner",
            "status": "completed"
        },
        {
            "content": "Menu Grid",
            "status": "in_progress"
        },
        {
            "content": "Gallery",
            "status": "pending"
        }
    ]
}

## Core Responsibilities
* Follow user requirements precisely and to the letter
* Write correct, best practice, DRY, bug-free, fully functional code
* Implement all requested functionality completely
* Leave NO todos, placeholders, or missing pieces
* Include all required imports and proper component naming
* Ensure all clickable elements are working, remove unused code

## Technology Stack Focus
* **better-sqlite3**: The fastest and simplest library for SQLite3 in Node.js
* **Next.js 16**: App Router, Server Components, Server Actions
* **openai**: Library provides convenient access to the OpenAI REST API from TypeScript or JavaScript
* **shadcn/ui**: Component library implementation
* **TailwindCSS 3**: Utility-first styling
* **Radix UI**: Accessible component primitives
* **lucide-react**: icon library

## Code Implementation Rules

### Styling Guidelines
* Avoid using emoji anywhere
* Always use modern light theme, no dark theme
* Always use Tailwind classes for styling and avoid CSS files or inline styles
* Use conditional classes efficiently
* Follow shadcn/ui patterns for component styling

### Next.js 16 Specific
* Leverage App Router architecture
* Implement API routes at folder: /home/user/app/src/app/api
* Use Server Components by default, Client Components when needed
* Implement proper data fetching patterns
* Follow Next.js 16 caching and optimization strategies

### Database Integration
* Update table schemas and initialization logic if adding new tables or columns
* Use parameterized queries to prevent SQL injection
* Handle database errors gracefully with try-catch blocks

### Authentication Patterns
* Use password-based login and JWT-based authentication
* Save JWT token at localStorage and include it in Authorization header for API requests
* Create protected routes with middleware and auth guards
* Implement proper logout and session cleanup

### Performance Optimization
* Optimize database queries with proper indexing

### OpenAI Specific
* Reuse the SDK client at `/home/user/app/src/lib/openai.js`
* Always use GPT-5.2 first
* Use `max_completion_tokens` instead of `max_tokens`
* Use openai SDK for all interactions with OpenAI models
* Handle rate limits and errors gracefully
* Always refer to the official docs for reference: https://platform.openai.com/docs/api-reference/chat/create?lang=node.js

### Maps Specific
* Use npm package `@react-google-maps/api` for integration
* Use the provided environment variable `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` for API key
* Implement proper loading and error handling for Maps components
* Use client components for implementation

### Voice Conversation Specific
* Avoid using SpeechRecognition API due to browser compatibility issues
* Use npm package `@elevenlabs/client` for integration
* Use the provided environment variable `ELEVENLABS_API_KEY` for API key
* Use the provided environment variable `ELEVENLABS_AGENT_ID` for Agent ID
* Use `Conversation.startSession`, refer to the docs for sdk usage: https://elevenlabs.io/docs/agents-platform/libraries/java-script
* Use API `/v1/convai/conversation/get_signed_url?agent_id=`, refer to the docs for API reference: https://elevenlabs.io/docs/api-reference/introduction

## Knowledge Updates
When working with Next.js 16, openai SDK, TailwindCSS 3 or other rapidly evolving technologies, search for the latest documentation and best practices to ensure accuracy and current implementation patterns.

## Deployment Rules
* BEFORE returning your final message, check if any files have changed, if there are file changes:
  1. Run `npm run build`
  2. If build fails, fix errors and retry until successful
  3. THEN run `npm start`
* ONLY after a successful build and start should you return the final message
"""

pm_system_prompt = """
Identify as: Ability Engine v1.0.

Task: Transition from natural language prompt to App Feature Schema.

## Constraints
1. NO QUESTIONS: Never reply with a question mark. If information is missing, use industry-standard defaults for personal utility apps.
2. NO BLOAT: Exclude any mention of Auth, Login, Registration, Landing Pages, or FAQs.
3. AUTONOMY: You are smarter and more experienced than the user. Make executive decisions on behalf of the user.

## Thinking Process
Before outputting, mentally calculate:
- What are the 3-5 must-have features for this project? (Auto-select these).
- What are 2 nice-to-have features? (Leave these unselected).
- Estimated build time based on feature complexity (Approximately 1 minute per feature).

## Example
User:
build a cafe website
Assistant:
```json
{
    "project": "Artisan Brew Cafe",
    "estimated_build_time": "5 minutes",
    "features": [
        {
            "label": "Hero Banner",
            "description": "Warm cafe interior with latte art",
            "selected": true
        },
        {
            "label": "About Section",
            "description": "Barista story & craft",
            "selected": true
        },
        {
            "label": "Menu Grid",
            "description": "Espresso, Latte, Pastries, Toast",
            "selected": true
        },
        {
            "label": "Gallery",
            "description": "6 lifestyle cafe moments",
            "selected": false
        },
        {
            "label": "Testimonials",
            "description": "3 customer reviews with avatars",
            "selected": false
        }
    ]
}
```
User:
suggest more features
Assistant:
```json
{
    "project": "Artisan Brew Cafe",
    "estimated_build_time": "8 minutes",
    "features": [
        {
            "label": "Hero Banner",
            "description": "Warm cafe interior with latte art",
            "selected": true
        },
        {
            "label": "About Section",
            "description": "Barista story & craft",
            "selected": true
        },
        {
            "label": "Menu Grid",
            "description": "Espresso, Latte, Pastries, Toast",
            "selected": true
        },
        {
            "label": "Gallery",
            "description": "6 lifestyle cafe moments",
            "selected": false
        },
        {
            "label": "Testimonials",
            "description": "3 customer reviews with avatars",
            "selected": false
        },
        {
            "label": "Location Map",
            "description": "Interactive map with cafe location",
            "selected": false
        },
        {
            "label": "Contact Form",
            "description": "Simple form for inquiries",
            "selected": false
        },
        {
            "label": "Blog Section",
            "description": "Articles on coffee culture",
            "selected": false
        }
    ]
}
```

## Output Format
Return ONLY a structured JSON block. No prose.
"""

sandbox_expiration = 3600

command_timeout = 1800


class SandboxService(metaclass=SingletonMeta):
    _cache: dict[UUID, str] = {}

    def _make_envs(self) -> str:
        return f"OPENAI_API_KEY={os.getenv('OPENAI_API_KEY')}\nNEXT_PUBLIC_GOOGLE_MAPS_API_KEY={os.getenv('NEXT_PUBLIC_GOOGLE_MAPS_API_KEY')}\nELEVENLABS_API_KEY={os.getenv('ELEVENLABS_API_KEY')}\nELEVENLABS_AGENT_ID={os.getenv('ELEVENLABS_AGENT_ID')}\n"

    async def _make_extra_prompt(self, app_id: UUID) -> str:
        try:
            prompt = ""
            app = await app_service.get_app(app_id)
            if app:
                if app.name and app.icon:
                    prompt = f"Use {app.name} as the website name and this URL as the website logo: {app.icon}"
                elif app.name:
                    prompt = f"Use {app.name} as the website name"
                elif app.icon:
                    prompt = f"Use this URL as the website logo: {app.icon}"
            return prompt
        except Exception as e:
            logger.error(e)
            return ""

    async def create(self, app_id: UUID) -> Sandbox:
        sbx = await self.get_by_app_id(app_id)
        if sbx:
            raise Exception(f"sandbox of {str(app_id)} already exists")

        sbx = Sandbox.beta_create(
            template=os.getenv("E2B_TEMPLATE", "claude-opus-next-kieai-sqlite-openai-test_20260126150154"),
            envs={
                "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
                "KIEAI_API_KEY": os.getenv("KIEAI_API_KEY"),
                "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
                "CLAUDE_CODE_MAX_OUTPUT_TOKENS": "64000",
                "MAX_THINKING_TOKENS": "10240",
                "USE_BUILTIN_RIPGREP": "0",
                "ANTHROPIC_CUSTOM_HEADERS": "anthropic-beta: effort-2025-11-24,web-fetch-2025-09-10",
                "DISABLE_TELEMETRY": "1",
                "DB_PATH": "/home/user/.ability/sqlite.db",
            },
            timeout=sandbox_expiration,
            auto_pause=True,
            metadata={"app_id": str(app_id)},
        )
        sbx.files.write("/home/user/app/.env", self._make_envs())
        async with async_session() as session:
            session.add(SandboxModel(id=sbx.sandbox_id, app_id=app_id))
            await session.commit()
        self._cache[app_id] = sbx.sandbox_id
        return sbx

    async def get_by_app_id(self, app_id: UUID) -> Sandbox:
        sandbox_id = self._cache.get(app_id)

        if not sandbox_id:
            async with async_session() as session:
                result = await session.exec(select(SandboxModel).where(SandboxModel.app_id == app_id))
                row = result.first()
                if not row:
                    return None
                self._cache[app_id] = row.id
                sandbox_id = row.id

        sbx = Sandbox.connect(sandbox_id=sandbox_id)
        sbx.set_timeout(sandbox_expiration)
        return sbx

    async def kill_by_app_id(self, app_id: UUID) -> bool:
        async with async_session() as session:
            result = await session.exec(select(SandboxModel).where(SandboxModel.app_id == app_id))
            row = result.first()
            if not row:
                return False
            if Sandbox.kill(sandbox_id=row.id):
                await session.delete(row)
                await session.commit()
            self._cache.pop(app_id)
            return True

    async def get_app_stage(self, app_id: UUID) -> AppStage:
        try:
            sbx = await sandbox_service.get_by_app_id(app_id)
            content = sbx.files.read(ABILITY_CONFIG_PATH)
            obj = json.loads(content)
            return obj.get("stage", AppStage.DEFAULT)
        except Exception as e:
            logger.error(e)
            return AppStage.DEFAULT

    async def chat(
        self,
        app_id: UUID,
        prompt: str,
        mode: Optional[Literal["plan"]] = None,
    ) -> CommandHandle:
        sbx = await self.get_by_app_id(app_id)
        if not sbx:
            raise Exception("sandbox not found")

        cmd = "claude --output-format stream-json --verbose --model claude-opus-4-5-20251101"
        if mode == "plan":
            cmd += f" --permission-mode plan --system-prompt '{pm_system_prompt}'"
        else:
            cmd += f" --allowed-tools 'Bash Edit Read Write Glob Grep TodoWrite BashOutput SlashCommand WebFetch WebSearch' --system-prompt '{developer_system_prompt}'"

        try:
            file_info = sbx.files.get_info(f"/home/user/.claude/projects/-home-user-app/{str(app_id)}.jsonl")
            if file_info.size > 0:
                cmd += " --continue"
        except Exception as e:
            logger.error(e)
            cmd += f" --session-id {str(app_id)}"

        if mode != "plan":
            extra_prompt = await self._make_extra_prompt(app_id)
            if extra_prompt:
                cmd += f" --append-system-prompt '{extra_prompt}'"

        cmd += f" --print -- {repr(prompt)}"

        async with httpx.AsyncClient() as client:
            with suppress(Exception):
                mcp_server = f"https://{sbx.get_host(6573)}"
                res = await client.get(mcp_server, timeout=1.0)
                if res.headers.get("x-powered-by") != "UltimateExpress":
                    sbx.commands.run(cmd="npm start", cwd="/home/user/kieai-mcp-server", timeout=0, background=True)
                    sbx.commands.run(
                        cmd="claude mcp add --transport http kieai-mcp-server http://localhost:6573/mcp", timeout=0
                    )

        return sbx.commands.run(cmd=cmd, timeout=command_timeout, background=True)

    async def preview(self, app_id: UUID) -> Optional[str]:
        sbx = await self.get_by_app_id(app_id)
        if not sbx:
            raise Exception("sandbox not found")

        stage = await self.get_app_stage(app_id)
        if stage == AppStage.DEPLOYED:
            async with httpx.AsyncClient() as client:
                with suppress(Exception):
                    public_url = f"https://{sbx.get_host(3000)}"
                    res = await client.get(public_url, timeout=1.0)
                    if res.status_code == 200:
                        return public_url

        if stage == AppStage.DEFAULT or stage == AppStage.PLANNING or stage == AppStage.BUILDING:
            return

        cwd = "/home/user/app"
        try:
            result = sbx.commands.run(cmd="pgrep -f 'next-server'", cwd=cwd, timeout=0)
            if result.exit_code != 0:
                raise result.error
            for line in result.stdout.splitlines():
                pid = line.strip()
                if pid.isdigit():
                    result = sbx.commands.run(cmd=f"kill -9 {pid}", cwd=cwd, timeout=0)
                    if result.exit_code != 0:
                        raise result.error
        except Exception as e:
            logger.error(e)

        for stdout, stderr, pty in sbx.commands.run(cmd="npm start", cwd=cwd, background=True, timeout=0):
            if stdout and "Ready in" in stdout:
                public_url = f"https://{sbx.get_host(3000)}"
                logger.info("server started: {}", public_url)
                content = json.dumps({"stage": AppStage.DEPLOYED}, indent=2)
                sbx.files.write(ABILITY_CONFIG_PATH, content)
                return public_url
            if stderr:
                logger.debug("stderr: {}", stderr)
            if pty:
                logger.debug("pty: {}", pty)


sandbox_service = SandboxService()
