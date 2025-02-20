# LSP Dev


# TODO
[] Investigate random characters written to stdout, possibly breaking lsp server json output
[x] Create module for the lsp code that is used form plugin
[x] Create new UodDescription that can be built and serialized from uod
    -x include uod tags and commands
    - fix missing uod commands, eg. TestInt
    -x include system tags
    -x include system commands
    -x for all commands, include arg spec model as data, maybe this is really just glorified regexes
[x] Send UodDescription as part of uod_info to aggregator, expose it from lsp aggregator endpoint
[x] Create arg spec model and an annotations format for it to use in validation command arguments
    - either infer this data from existing uod definitions or change uod definition api to be better
      (wrap regexes into a better abstraction that more cleanly exposes current functionality and exposes
      arg spec model)
    - json schema? this trivially includes the data we need
[X] Maybe the system_tags can be created and shared so engine can add its stuff without needing to create them?
  That would clean up uod loading/initializing/validating
[] Support closing document and releasing uod
[x] Make lsp server start and stop with aggregator
[x] logging does not work. logs in console but should log to file
[] Add more source location fields during PProgram build to enable precise condition source locations
   in diagnostics
[] Improve lsp url: http://localhost:9800/uod/MIAWLT-1645-MPO_DemoUod



## Debugging client/server config
- Debug without aggregator+engine
```
cd frontend
ng serve
```
The open browser @ http://localhost:4200
Seems we get many errors from the frontend when using only MSW - goes away if aggregator is started

Start lsp server with
```
pylsp --ws -vv --log-file lsp_server.log
```

## Very simple client
The client in lsp-demos\editor-playground can be run with ng serve for a simple "offline" editor that only 
does LSP communication

This works well with the debug launcher "Open Pectus LSP server (debug)".

<!-- Looks like we need to add a 'Save' button to the client to be able to receive pylsp_document_did_save. -->

<!-- Consider workspace, see node_modules\monaco-languageclient\src\monaco-language-client.ts and the comment there.
The client option workspaceFolder influences whether the WorkspaceFoldersFeature is added. This in turn likely
influences the workspace argument provided to hook methods in the plugin. -->

## How to get the plugin to load
The 'proper' way is to create the plugin as a seperate project and the to install it. That works.
But we can install it with our existing package, it just needs to be registered as plugin so
pylsp will load it. This is done using a "setuptools entry-point" added in pyproject.toml.
as documented here https://pluggy.readthedocs.io/en/stable/index.html and here
https://setuptools.pypa.io/en/latest/userguide/entry_point.html#entry-points.

Plugin dev 'docs' here: https://github.com/python-lsp/cookiecutter-pylsp-plugin


## Configure client
Client configuration is performed in this file:
```
frontend/src/app/details/method-editor/monaco-editor.component.ts
```

languageId = 'pcode'

## TODO tasks
- Define feature flag for frontend - do we have something already?
  - involve jan
  - it is really a kind of LspSettings{ enabled, uri(include port)}
- Settings/configuration in file
  - hopefylly disable stuff without code
- Define some logging configurations
  - A debug config that logs heavily. This includes stuff we probably don't need
  - A customized log tailored ot only include our plugin
  
## Server lifetime
These are the call hooks important for an lsp session.

The complete hook list is here https://github.com/python-lsp/python-lsp-server/blob/develop/pylsp/hookspecs.py
LSP spec overview: https://microsoft.github.io/language-server-protocol/overviews/lsp/overview/

Note about document. It appears that the document instance provided as argument to most hook methods
is automatically kept up to date by pyslp. In particular, the 'textDocument/didChange' message has no
matching hook method. Instead, when 'textDocument/didChange' is sent from client, pylsp_lint is invoked
with document updated with the text change that were sent in 'textDocument/didChange'. That's very neat.

- pylsp-openpectus plugin module loading
- pylsp_settings
- pylsp_initialize
- pylsp_commands (not yet)
- pylsp_experimental_capabilities (not yet)
-  (send capabilities)
-  (receive initialized)
- pylsp_initialized
- pylsp_document_did_open
  -  arguments:
     -  config: Config,
     -  workspace: Workspace
     -  document: Document
  -  `document.source` has code text content if already present in editor
  -  `document.uri` has 'filename' that we should use to identify uod an 

Calls, order not confirmed, expected to be anytime
- pylsp_lint
  - create and return diagnostics, possibly cache result
  - canlled frequently, possibly on each keystroke during editing
- pylsp_hover
- 

Calls not  yet hooked up, order not confirmed, expected to be anytime
- pylsp_folding_range
  - This seems to work out of the box with the default pyslp implementation. Folding using python syntax seems to work correctly. No need to hook up the method.
- pylsp_code_lens
  - should be disabled if possible. Code lens is actions for a code line, like "execute test". we have no need for this
    and it would be nice to avoid this frequent call

Calls not yet encountered
- pylsp_document_did_save



# Code Actions
see example https://github.com/python-rope/pylsp-rope/blob/main/test/test_inline.py


---------------------
actions working example:

# Command and CodeActionKind may or may not be useful
CodeActionKind = Literal[
    "",
    "quickfix",
    "refactor",
    "refactor.extract",
    "refactor.inline",
    "refactor.rewrite",
    "source",
    "source.organizeImports",
    "source.fixAll",
]

class Command:
    name: str
    title: str
    kind: CodeActionKind


@hookimpl
def pylsp_code_actions(config, workspace, document, range, context):
    logger.info("textDocument/codeAction: %s %s %s", document, range, context)

    return [
        {
            "title": "Extract method",
            "kind": "refactor.extract",
            "command": {
                "command": "example.refactor.extract",
                "arguments": [document.uri, range],
            },
        },
        {
            "title": "Foo",
            "kind": "myown.kind",
            "command": {
                "command": "Foo",
                "arguments": [document.uri, range],
            },
        },
        {
            "title": "Bar",
            "kind": "my own kind with spaces and all",
            "command": {
                "command": "Bar",
                "arguments": [document.uri, range],
            },
        },
    ]

# This is required for a command returned from pylsp_code_actions to work. When executed, calls pylsp_execute_command
@hookimpl
def pylsp_commands(config, workspace) -> List[str]:
    return ["example.refactor.extract", "Foo", "Bar"]

@hookimpl
def pylsp_execute_command(config, workspace, command, arguments):
    logger.info("workspace/executeCommand: %s %s", command, arguments)

    if command == "Foo":
        workspace.show_message(
            f"Some server error here. The command was: {command}",
            msg_type=MessageType.Error,
        )
    if command == "Bar":
        workspace.show_message(
            f"Some server info here. The command was: {command}",
            msg_type=MessageType.Info,
        )

---------------------
