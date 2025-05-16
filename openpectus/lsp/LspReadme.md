# LSP Dev


# TODO
[] Bugs
  [x] 'Warning: foo' gives an argument error but is using NoCheck
  [x] 'Wait: 5w' does not report error, should be required and only accept time
    unit. caused by analyer not considering PCommandWithDuration 
  [x] 'Increment run counter' gives error 'The command name 'Increment run counter' is not validOpen Pectus(Undefined command)'
[] Fast-track usable LSP - only completions, these are fast regardless of source size and have no locking issues
  [] Add completion support for command thresholds
[] Fix fix aggregator host and port in fetch
  semanticTokens ?
    [] enable on client side and see if the calls are made, no, they are not
    [] expose as server capability - now calls should be made
    [] figure out how pyslp can respond to semanticTokens
    [] build and return token response
  textmate ?
    [] jan will check if coloring works with a simple example
    [] if result is positive
       [] figure out what filename to use
       [] create an endpoint that delivers a fixed example file
       [] generate file from uod_definition

[] Investigate random characters written to stdout, possibly breaking lsp server json output
    - cause not known. Examples:
    - response that was malformed: '}{"jsonrpc":"2.0","id":9,"result":[{"'
      original response: '{"jsonrpc":"2.0","id":9,"result":[{"startLine":3,"endLine":4}]}'
      original request: '{"jsonrpc":"2.0","id":9,"method":"textDocument/foldingRange","params":{"textDocument":{"uri":"file:///workspace/model21.pcode"}}}'
    - response malformed: 'onrpc":"2.0","id":8,"re1sion":3}}{"jsonrpc":"2.0","id":6,"result'
      original response: '{"jsonrpc":"2.0","id":8,"result":[]}'
      original request: '{"jsonrpc":"2.0","id":8,"method":"textDocument/codeLens","params":{"textDocument":{"uri":"file:///workspace/model82.pcode"}}}' 
    - so a fix may be to disable the 'textDocument/foldingRange' feature. should be doable server-side with enough digging
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
[x] Add more source location fields during PProgram build to enable precise condition source locations
   in diagnostics
[] Improve lsp url: http://localhost:9800/uod/MIAWLT-1645-MPO_DemoUod

[] Settings/configuration in file
  - hopefylly disable stuff without code
[x] Implement simple symbols
[] Implement advanced symbols
  - Watch and Alarm should have a condition child symbol
  - A condition symbol should have its 3/4 parts as child symbols: tag, operator, value, [unit]
[] Autocomplete on Info, Warning and Error should only be enabled for the command, not for any arguments since that is the user message
[] Performance tactics
  - Improve parse performance
    - Split document into multiple regions and parse each region independtly
      - lint improvements - only a changed region must be re-parsed and linted
        - requires handling regions
        - requires joining lint results from regions
      - symbol improvements - only a changed region must be re-parsed and have symbols extracted
        - requires handling regions
        - requires joining symbols results from regions
      - handling regions
        - must split at program level for regions to be independant
    - Hand roll a simple custom parser for completions
        - Must handle all cases we support
          - threshold
          - commands with conditions
            - handle many steps of
[] Hook into document updates
  - Need to avoid re-parse on every keystroke and this may be the only way
  - in order to do a full re-parse every once and a while and not parse (lint, symbols) on all changes
  - it seems there is no direct hook for document changes which is probably because document changes are handled
    internally in lsp server. But we might add a hook, by interception workspace.update_document/workspace.apply_edit.

[] Update method on running interpretation
  The above performance discussion should also consider udpating a running method. This is 
  because that too involves a segment (partial) parse. This may even result in out-of-segment updates (macro) (?)

An error causing the plugin to not load has been seen. The current theory is that there was an error in the conda/python environment.
Using python 3.12 in a named (not prefixed) environment does work.

document symbols - 

## Nice to have
[] Go to definition/declaration - only useful for Macro definitions

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
- pylsp_symbols
  - not getting useful results with this. First, returning DocumentSymbol fails on the client. Returning SymbolInformationItem
    does not fail but also doesn't do anything (coloring and what have we). The failure for DocumentSymbolItem is the same
    as we get for SymbolInformationItem with a bad property name. Also, can't figure out which protocol version the client 
    is actually using.
    Trying out DocumentSymbols again. Works if we only use the required properties name, kind, range, selectionRange. The
    client call succeeds but nothing happens visually.

- semantic tokens, may also provide color info - but I can't find a pslsp hook for this kind of request
  docs: https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_semanticTokens

- pylsp_completions
  - This works well. Also consider pylsp_completion_item_resolve for more details to the suggestions
    https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_completion

- Figure out how do disable textDocument/codeLens, textDocument/foldingRange and textDocument/documentHighlight.
  There is a lot going on when typing. Many requests being sent and then cancelled from the client. So we don't want
  unused requests in the mix.

Calls not  yet hooked up, order not confirmed, expected to be anytime
- pylsp_folding_range
  - This seems to work out of the box with the default pyslp implementation. Folding using python syntax seems to work correctly. No need to hook up the method.
- pylsp_code_lens
  - should be disabled if possible. Code lens is actions for a code line, like "execute test". we have no need for this
    and it would be nice to avoid this frequent call
- commands: for this, the 3 methods pylsp_code_actions, pylsp_commands and pylsp_execute_command work together. See code example below

Calls not yet encountered
- pylsp_document_did_save

Nice to have
- hover - signature or tag description
- autocomplete - first tag, then operator, then value, then maybe unit

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
