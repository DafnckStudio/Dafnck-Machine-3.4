import inspect
from pathlib import Path
from fastmcp import FastMCP
from fastmcp.client import Client

async def test_multi_client(tmp_path: Path):
    server_script = inspect.cleandoc("""
        from fastmcp import FastMCP

        mcp = FastMCP(enable_task_management=False)

        @mcp.tool
        def add(a: int, b: int) -> int:
            return a + b

        if __name__ == '__main__':
            mcp.run()
        """)

    script_path = tmp_path / "test.py"
    script_path.write_text(server_script)

    # We need to get the parent of the current working directory to add it to the PYTHONPATH
    # so that the tests can find the `fastmcp` module.
    python_path = str(Path.cwd() / "src")

    config = {
        "mcpServers": {
            "test_1": {
                "command": "python",
                "args": [str(script_path)],
                "env": {"PYTHONPATH": python_path},
            },
            "test_2": {
                "command": "python",
                "args": [str(script_path)],
                "env": {"PYTHONPATH": python_path},
            },
        }
    }

    client = Client(config)

    async with client:
        tools = await client.list_tools()
        assert len(tools) == 2

        result_1 = await client.call_tool("test_1_add", {"a": 1, "b": 2})
        result_2 = await client.call_tool("test_2_add", {"a": 1, "b": 2})
        assert result_1[0].text == "3"  # type: ignore[attr-dict]
        assert result_2[0].text == "3"  # type: ignore[attr-dict] 