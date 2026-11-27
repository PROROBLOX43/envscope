# EnvScope

Catch environment variables used in your code but missing from `.env.example`.

EnvScope is a small, dependency-free Python CLI for Python and JavaScript/TypeScript projects. It reports each missing variable with its file and line, and lists example entries it could not find in source.

## Quick start

```bash
python -m pip install -e .
python -m envscope /path/to/your/project
```

Example:

```text
MISSING API_KEY  app.py:12, web.ts:8
UNUSED  OLD_FLAG
Checked 3 variable(s): 1 missing, 1 unused
```

Exit code is `1` if a variable is missing, otherwise `0`, so it works in CI:

```yaml
- name: Check environment docs
  run: python -m envscope .
```

Use `--example config/.env.template` for another example file or `--json` for structured output.

## Scope

Recognizes literal `os.getenv("NAME")`, `os.environ["NAME"]`, `process.env.NAME`, and `process.env["NAME"]` references. It skips dependency/build directories and files larger than 1 MB. Dynamic names, comments, and string literals may produce incomplete or extra results; review findings before editing documentation. EnvScope reads source files and the example file, and never reads your real `.env` values.

## Contributing

Bug reports and small pull requests are welcome. Include a short reproducing example and a test for parser changes. Run `python -m unittest discover -s tests` before submitting.

## License

MIT
