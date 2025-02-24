import { AfterViewInit, ChangeDetectionStrategy, Component, ElementRef, input, OnDestroy, ViewChild } from '@angular/core';
// import '@codingame/monaco-vscode-json-default-extension';
import '@codingame/monaco-vscode-theme-defaults-default-extension';
import { editor as MonacoEditor, KeyCode, Range } from '@codingame/monaco-vscode-editor-api';
import { concatLatestFrom } from '@ngrx/operators';
import { Store } from '@ngrx/store';
import { MonacoEditorLanguageClientWrapper, WrapperConfig } from 'monaco-editor-wrapper';
import { Logger } from 'monaco-languageclient/tools';
import { useWorkerFactory } from 'monaco-languageclient/workerFactory';
import { combineLatest, filter, firstValueFrom, Observable, Subject, takeUntil } from 'rxjs';
import { LogLevel } from 'vscode';
import { MethodLine } from '../../api';
import { UtilMethods } from '../../shared/util-methods';
import { MethodEditorActions } from './ngrx/method-editor.actions';
import { MethodEditorSelectors } from './ngrx/method-editor.selectors';

const startedLineClassName = 'started-line';
const executedLineClassName = 'executed-line';
const injectedLineClassName = 'injected-line';
const lineIdClassNamePrefix = 'line-id-';

@Component({
  selector: 'app-monaco-editor',
  changeDetection: ChangeDetectionStrategy.OnPush,
  styleUrls: ['monaco-editor.component.scss'],
  template: `
    <div #editor class="w-full h-full"></div>
  `,
})
export class MonacoEditorComponent implements AfterViewInit, OnDestroy {
  editorSizeChange = input<Observable<void>>();
  readOnlyEditor = input(false);
  unitId = input<string>();
  @ViewChild('editor', {static: true}) editorElement!: ElementRef<HTMLDivElement>;
  private componentDestroyed = new Subject<void>();
  private wrapper = new MonacoEditorLanguageClientWrapper();
  private methodContent = this.store.select(MethodEditorSelectors.methodContent);
  private executedLineIds = this.store.select(MethodEditorSelectors.executedLineIds);
  private injectedLineIds = this.store.select(MethodEditorSelectors.injectedLineIds);
  private startedLineIds = this.store.select(MethodEditorSelectors.startedLineIds);
  private lineIds = this.store.select(MethodEditorSelectors.lineIds);
  private methodLines = this.store.select(MethodEditorSelectors.methodLines);
  private storeModelChangedFromHere = false;
  private editorModelChangedFromStore = false;

  constructor(private store: Store) {}

  // adapted from https://github.com/TypeFox/monaco-languageclient/blob/70f92b740a06f56210f91464d694b5e5d4dc87db/packages/examples/src/common/client/utils.ts
  configureMonacoWorkers(logger?: Logger) {
    useWorkerFactory({
      workerLoaders: {
        'TextEditorWorker': () => new Worker('/monaco-workers/editorWorker-es.js', {type: 'module'}),
        'TextMateWorker': () => new Worker(
          new URL('@codingame/monaco-vscode-textmate-service-override/worker', import.meta.url), {type: 'module'},
        ),
        OutputLinkDetectionWorker: undefined,
        LanguageDetectionWorker: undefined,
        NotebookEditorWorker: undefined,
        LocalFileSearchWorker: undefined,
      },
      logger,
    });
  };

  async ngAfterViewInit() {
    const methodContent = await firstValueFrom(this.methodContent);
    await this.wrapper.initAndStart(this.buildWrapperUserConfig(this.editorElement.nativeElement, methodContent), false);
    this.setupEditor(this.wrapper.getEditor());
    if(this.unitId() !== undefined) {
      this.wrapper.initLanguageClients();
      await this.wrapper.startLanguageClients();
    }
    this.store.dispatch(MethodEditorActions.monacoEditorComponentInitialized());
  }

  buildWrapperUserConfig(htmlContainer: HTMLElement, text: string): WrapperConfig {
    return {
      $type: 'extended',
      htmlContainer,
      logLevel: LogLevel.Warning,
      vscodeApiConfig: {
        // vscodeApiInitPerformExternally: true,
        // enableExtHostWorker: true,
        userConfiguration: {
          json: JSON.stringify({
            'editor.fontSize': 18,
            'editor.glyphMargin': false,
            'editor.fixedOverflowWidgets': true,
            'editor.lineNumbersMinChars': UtilMethods.isMobile ? 1 : 3,
            'editor.minimap': {
              enabled: UtilMethods.isDesktop,
            },
            'editor.lightbulb.enabled': 'off',
            'editor.experimental.asyncTokenization': true,
            'editor.foldingStrategy': 'indentation',
            'editor.wordBasedSuggestions': 'off',
            // "editor.quickSuggestions": false
          }),
        },
      },
      extensions: [{
        config: {
          name: 'pcode',
          version: '0.0.0',
          publisher: 'openpectus',
          engines: {vscode: '0.10.x'},
          categories: ['Programming Languages'],
          contributes: {
            languages: [{
              id: 'pcode',
              aliases: ['PCODE', 'pcode'],
              extensions: ['.pcode'],
              mimetypes: ['application/pcode'],
              configuration: './language-configuration.json',
            }],
          },
        },
        filesOrContents: new Map([
          ['./language-configuration.json', JSON.stringify({ // adapted from language-configuration.json in @codingame/monaco-vscode-json-default-extension
              comments: {lineComment: '#'},
              onEnterRules: [{
                beforeText: {pattern: '^\\s*(Alarm|Block|Watch|Macro).*$'},
                action: {indent: 'indent'},
              }, {
                beforeText: {pattern: '^\\s*End block$'},
                action: {indent: 'outdent'},
              }, {
                beforeText: {pattern: '^\\s*End blocks$'},
                action: {indent: 'none', removeText: Number.MAX_VALUE},
              }],
            },
          )],
        ]),
      }],
      editorAppConfig: {
        codeResources: {
          modified: {
            text,
            fileExt: 'pcode',
          },
        },
        monacoWorkerFactory: this.configureMonacoWorkers,
      },
      languageClientConfigs: {
        'pcode': {
          clientOptions: {
            documentSelector: ['pcode'],
            initializationOptions: {
              engineId: this.unitId(),
            },
          },
          connection: {
            options: {
              $type: 'WebSocketUrl',
              url: `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://localhost:2087/lsp`,
              // startOptions: {
              //   onCall: () => {
              //     console.log('Connected to socket.');
              //   },
              //   reportStatus: false,
              // },
              // stopOptions: {
              //   onCall: () => {
              //     console.log('Disconnected from socket.');
              //   },
              //   reportStatus: false,
              // },
            },
          },
        },
      },
    } satisfies WrapperConfig;
  };

  ngOnDestroy() {
    this.componentDestroyed.next();
    void this.wrapper.dispose();
    this.store.dispatch(MethodEditorActions.monacoEditorComponentDestroyed());
  }

  private setupEditor(editor?: MonacoEditor.IStandaloneCodeEditor) {
    if(editor === undefined) return;
    this.setupOnEditorChanged(editor);
    this.setupOnStoreModelChanged(editor);
    this.setupInjectedLines(editor);
    this.setupStartedAndExecutedLines(editor);
    this.setupReactingToResize(editor);
  }

  private setupOnEditorChanged(editor: MonacoEditor.IStandaloneCodeEditor) {
    editor.onDidChangeModelContent(() => {
      if(this.editorModelChangedFromStore) return;
      setTimeout(() => { // setTimeout to allow for line id decorations to be placed before this is executed
        const model = editor.getModel();
        if(model === null) return;
        const linesContents = model.getLinesContent();

        const lines = linesContents.map<MethodLine>((lineContent, index) => {
          const decorations = model.getLineDecorations(index + 1);
          const idDecoration = decorations.find(decoration => decoration.options.className?.startsWith(lineIdClassNamePrefix));
          const id = idDecoration?.options.className?.substring(lineIdClassNamePrefix.length);
          return {
            id: id ?? crypto.randomUUID(),
            content: lineContent,
          } satisfies MethodLine;
        });
        this.storeModelChangedFromHere = true;
        this.store.dispatch(MethodEditorActions.linesChanged({lines}));
        this.storeModelChangedFromHere = false;
      });
    });
  }

  // Sets up both edits to content and line id decorations, because it's important that they happen right after each other and in this order.
  private setupOnStoreModelChanged(editor: MonacoEditor.IStandaloneCodeEditor) {
    const lineIdsDecorationCollection = editor.createDecorationsCollection();
    this.methodLines.pipe(
      filter(() => !this.storeModelChangedFromHere),
      takeUntil(this.componentDestroyed),
    ).subscribe(methodLines => {
      // Apply edits
      const methodContent = methodLines.map(line => line.content).join('\n');
      const preEditSelection = editor.getSelection();

      this.editorModelChangedFromStore = true;
      editor.getModel()?.applyEdits([{range: new Range(0, 0, Number.MAX_VALUE, Number.MAX_VALUE), text: methodContent}]);
      this.editorModelChangedFromStore = false;

      if(preEditSelection !== null) editor.setSelection(preEditSelection);

      // Set line id decorations
      const lineIds = methodLines.map(line => line.id);
      const lineIdDecorations = lineIds.map<MonacoEditor.IModelDeltaDecoration>((lineId, index) => {
        const lineNumber = index + 1;
        return {
          range: new Range(lineNumber, 0, lineNumber, 0),
          options: {
            className: lineIdClassNamePrefix + lineId,
            shouldFillLineOnLineBreak: false,
            stickiness: MonacoEditor.TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges,
          },
        };
      });
      lineIdsDecorationCollection.set(lineIdDecorations);
    });
  }

  private getLineNumberFunction(injectedLines: number[]) {
    return (lineNumber: number) => {
      if(injectedLines.includes(lineNumber)) return '';
      const injectedLinesBeforeThis = injectedLines.filter(injectedLineNumber => injectedLineNumber < lineNumber);
      const lineNumberWithoutInjectedLines = lineNumber - injectedLinesBeforeThis.length;
      return lineNumberWithoutInjectedLines.toString();
    };
  }

  private setupStartedAndExecutedLines(editor: MonacoEditor.IStandaloneCodeEditor) {
    const startedAndExecutedLinesDecorationCollection = this.setupDecoratingStartedAndExecutedLines(editor);
    if(this.readOnlyEditor()) {
      editor.updateOptions({readOnly: true, readOnlyMessage: {value: 'You cannot edit an already executed program.'}});
    } else {
      this.setupLockingStartedAndExecutedLines(editor, startedAndExecutedLinesDecorationCollection);
    }
  }

  private setupLockingStartedAndExecutedLines(editor: MonacoEditor.IStandaloneCodeEditor,
                                              startedAndExecutedLineDecorations: MonacoEditor.IEditorDecorationsCollection) {
    const lockEditorIfSelectionIntersectsExecutedLines = () => {
      const selectionInLockedRange = editor.getSelections()?.some(selection => {
        return startedAndExecutedLineDecorations.getRanges()
          .flatMap(range => UtilMethods.getNumberRange(range.startLineNumber, range.endLineNumber))
          .some(lockedLineNumber => {
            return selection.intersectRanges(new Range(lockedLineNumber, 0, lockedLineNumber + 1, 0));
          });
      });
      editor.updateOptions({readOnly: selectionInLockedRange, readOnlyMessage: {value: 'Cannot edit lines already started or executed.'}});
    };
    editor.onDidChangeCursorSelection(lockEditorIfSelectionIntersectsExecutedLines);
    this.executedLineIds.pipe(takeUntil(this.componentDestroyed)).subscribe(lockEditorIfSelectionIntersectsExecutedLines);

    // Block specifically delete/backspace when at the ending/starting edge of the line before/after the locked line.
    editor.onKeyDown(event => {
      const isBackspace = event.keyCode === KeyCode.Backspace;
      const isDelete = event.keyCode === KeyCode.Delete;
      if(!isBackspace && !isDelete) return;
      const selectionInLockedRange = editor.getSelections()?.some(selection => {
        return startedAndExecutedLineDecorations.getRanges()
          .flatMap(range => UtilMethods.getNumberRange(range.startLineNumber, range.endLineNumber))
          .some(lockedLineNumber => {
            const previousLineLength = editor?.getModel()?.getLineLength(Math.max(1, lockedLineNumber - 1)) ?? 0;
            const lockedRange = isDelete
                                ? new Range(lockedLineNumber - 1, previousLineLength + 1, lockedLineNumber, 0)
                                : new Range(lockedLineNumber, 0, lockedLineNumber + 1, 1);
            return selection.intersectRanges(lockedRange);
          });
      });
      if(selectionInLockedRange) {
        event.stopPropagation();
        event.preventDefault();
      }
    });
  }

  private setupDecoratingStartedAndExecutedLines(editor: MonacoEditor.IStandaloneCodeEditor) {
    const startedAndExecutedLinesDecorationsCollection = editor.createDecorationsCollection();
    const createDecoration = (lineIds: string[], lineClassName: string, hoverMessage: string) => (executedLineId: string) => {
      const lineNumber = lineIds.findIndex(lineId => lineId === executedLineId) + 1;
      if(lineNumber === undefined) throw Error(`could not find line id decoration with id ${executedLineId}`);
      return {
        range: new Range(lineNumber, 0, lineNumber, 0),
        options: {
          isWholeLine: true,
          className: lineClassName,
          hoverMessage: {value: hoverMessage},
          shouldFillLineOnLineBreak: false,
          stickiness: MonacoEditor.TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges,
        },
      };
    };

    combineLatest([this.startedLineIds, this.executedLineIds]).pipe(
      concatLatestFrom(() => this.lineIds),
      takeUntil(this.componentDestroyed),
    ).subscribe(([[startedLineIds, executedLineIds], lineIds]) => {
      const executedLinesDecorations = executedLineIds.map<MonacoEditor.IModelDeltaDecoration>(
        createDecoration(lineIds, executedLineClassName, 'This line has been executed and is no longer editable.'),
      );
      const startedLinesDecorations = startedLineIds.map<MonacoEditor.IModelDeltaDecoration>(
        createDecoration(lineIds, startedLineClassName, 'This line has been started and is no longer editable.'),
      );
      startedAndExecutedLinesDecorationsCollection.set([...executedLinesDecorations, ...startedLinesDecorations]);
    });
    return startedAndExecutedLinesDecorationsCollection;
  }

  private decorateInjectedLines(editor: MonacoEditor.IStandaloneCodeEditor) {
    const injectedLinesDecorationCollection = editor.createDecorationsCollection();
    this.injectedLineIds.pipe(
      concatLatestFrom(() => this.lineIds),
      takeUntil(this.componentDestroyed),
    ).subscribe(([injectedLineIds, lineIds]) => {
      const injectedLinesDecorations = injectedLineIds.map<MonacoEditor.IModelDeltaDecoration>(injectedLineId => {
        const lineNumber = lineIds.findIndex(lineId => lineId === injectedLineId) + 1;
        return {
          range: new Range(lineNumber, 0, lineNumber, 0),
          options: {
            className: injectedLineClassName,
            isWholeLine: true,
            hoverMessage: {value: 'This line has been injected and is not part of the methodContent.'},
            linesDecorationsClassName: 'codicon-export codicon',
            shouldFillLineOnLineBreak: false,
            stickiness: MonacoEditor.TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges,
          },
        };
      });
      injectedLinesDecorationCollection.set(injectedLinesDecorations);
    });
    return injectedLinesDecorationCollection;
  }

  private setupInjectedLines(editor: MonacoEditor.IStandaloneCodeEditor) {
    const decorations = this.decorateInjectedLines(editor);
    decorations.onDidChange(() => {
      const lineNumbers = decorations.getRanges().flatMap(range => UtilMethods.getNumberRange(range.startLineNumber, range.endLineNumber));
      editor.updateOptions({lineNumbers: this.getLineNumberFunction(lineNumbers)});
    });
  }

  private setupReactingToResize(editor: MonacoEditor.IStandaloneCodeEditor) {
    this.editorSizeChange()?.pipe(takeUntil(this.componentDestroyed)).subscribe(() => editor?.layout());
    window.onresize = () => editor?.layout();
  }
}
